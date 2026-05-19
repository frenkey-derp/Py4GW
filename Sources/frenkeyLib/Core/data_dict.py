import json
import msvcrt
import os
import re
import tempfile
import time
from dataclasses import dataclass
from functools import total_ordering
from typing import TYPE_CHECKING, Callable, IO, Mapping, Optional, cast

from Sources.frenkeyLib.Core.json_serializable import JsonSerializableDictionary
from Sources.frenkeyLib.Core.json_serializable import JsonSerializableList
from Sources.frenkeyLib.Core.json_serializable import T_DICT_KEY
from Sources.frenkeyLib.Core.json_serializable import T_SERIALIZABLE_VALUE


_VERSION_PATTERN = re.compile(r'"version"\s*:\s*("([^"\\]|\\.)*"|-?\d+(?:\.\d+)?)')
_VERSION_SCAN_BYTES = 512
_DEFAULT_LOCK_TIMEOUT_SECONDS = 5.0
_DEFAULT_LOCK_POLL_INTERVAL_SECONDS = 0.05
_LOCK_SIZE_BYTES = 1


@total_ordering
@dataclass(frozen=True)
class FileVersion:
    raw: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'raw', str(self.raw))

    def _parts(self) -> tuple[int | str, ...]:
        parts: list[int | str] = []
        for piece in self.raw.split('.'):
            parts.append(int(piece) if piece.isdigit() else piece)
        return tuple(parts)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, FileVersion):
            return NotImplemented
        return self._parts() < other._parts()

    def __str__(self) -> str:
        return self.raw


class FileLockTimeoutError(TimeoutError):
    def __init__(self, target_path: str, timeout_seconds: float):
        super().__init__(f'Timed out after {timeout_seconds:.2f}s waiting for lock: {target_path}')
        self.target_path = target_path
        self.timeout_seconds = timeout_seconds


class _WindowsFileLock:
    def __init__(self, lock_path: str):
        self.lock_path = lock_path
        self._file: Optional[IO[bytes]] = None

    def acquire(
        self,
        *,
        timeout_seconds: float = _DEFAULT_LOCK_TIMEOUT_SECONDS,
        poll_interval_seconds: float = _DEFAULT_LOCK_POLL_INTERVAL_SECONDS,
    ) -> None:
        deadline = time.monotonic() + max(timeout_seconds, 0.0)
        directory = os.path.dirname(self.lock_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        while True:
            lock_file = open(self.lock_path, 'a+b')
            try:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, _LOCK_SIZE_BYTES)
                lock_file.seek(0)
                lock_file.truncate()
                lock_file.write(str(os.getpid()).encode('ascii', errors='ignore'))
                lock_file.flush()
                self._file = lock_file
                return
            except OSError:
                lock_file.close()
                if time.monotonic() >= deadline:
                    raise FileLockTimeoutError(self.lock_path, timeout_seconds)
                time.sleep(max(poll_interval_seconds, 0.0))

    def release(self) -> None:
        if self._file is None:
            return

        lock_file = self._file
        self._file = None

        try:
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, _LOCK_SIZE_BYTES)
        finally:
            lock_file.close()

    def __enter__(self) -> '_WindowsFileLock':
        self.acquire()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.release()


class _DataFileMixin:
    get_local_path: Callable[..., str]
    get_default_path: Callable[..., str]
    version: FileVersion
    requires_save: bool

    if TYPE_CHECKING:
        def clear(self) -> None:
            ...

    def resolve_local_path(self) -> str:
        return self.get_local_path()

    def resolve_default_path(self) -> str:
        return self.get_default_path()

    def resolve_active_path(self) -> str:
        local_path = self.resolve_local_path()
        if os.path.exists(local_path):
            return local_path
        return self.resolve_default_path()

    def resolve_lock_path(self, path: Optional[str] = None) -> str:
        target_path = path or self.resolve_local_path()
        return f'{target_path}.lock'

    def is_locked(self, path: Optional[str] = None) -> bool:
        lock = _WindowsFileLock(self.resolve_lock_path(path))
        try:
            lock.acquire(timeout_seconds=0.0, poll_interval_seconds=0.0)
        except FileLockTimeoutError:
            return True
        else:
            lock.release()
            return False

    def wait_for_unlock(
        self,
        path: Optional[str] = None,
        *,
        timeout_seconds: float = _DEFAULT_LOCK_TIMEOUT_SECONDS,
        poll_interval_seconds: float = _DEFAULT_LOCK_POLL_INTERVAL_SECONDS,
    ) -> bool:
        lock = _WindowsFileLock(self.resolve_lock_path(path))
        try:
            lock.acquire(
                timeout_seconds=timeout_seconds,
                poll_interval_seconds=poll_interval_seconds,
            )
        except FileLockTimeoutError:
            return False
        else:
            lock.release()
            return True

    def queue_save(self) -> None:
        self.requires_save = True

    def _to_file_payload(self) -> dict:
        raise NotImplementedError

    def _load_path(self, path: str, *, replace: bool, merge_missing: bool = False, update_version: bool = True) -> None:
        raise NotImplementedError

    def save(
        self,
        path: Optional[str] = None,
        *,
        indent: Optional[int] = None,
        lock_timeout_seconds: float = _DEFAULT_LOCK_TIMEOUT_SECONDS,
        lock_poll_interval_seconds: float = _DEFAULT_LOCK_POLL_INTERVAL_SECONDS,
    ) -> None:
        target_path = path or self.resolve_local_path()
        lock = _WindowsFileLock(self.resolve_lock_path(target_path))
        lock.acquire(
            timeout_seconds=lock_timeout_seconds,
            poll_interval_seconds=lock_poll_interval_seconds,
        )
        try:
            self._save_locked(target_path, indent=indent)
        finally:
            lock.release()

        self.requires_save = False

    def try_save(
        self,
        path: Optional[str] = None,
        *,
        indent: Optional[int] = None,
    ) -> bool:
        if not self.requires_save:
            return False
        
        target_path = path or self.resolve_local_path()
        lock = _WindowsFileLock(self.resolve_lock_path(target_path))
        try:
            lock.acquire(timeout_seconds=0.0, poll_interval_seconds=0.0)
        except FileLockTimeoutError:
            return False

        try:
            self._save_locked(target_path, indent=indent)
        finally:
            lock.release()

        self.requires_save = False
        return True

    def _save_locked(self, target_path: str, *, indent: Optional[int] = None) -> None:
        directory = os.path.dirname(target_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        if os.path.exists(target_path):
            self._load_path(target_path, replace=False, merge_missing=True, update_version=False)

        payload = json.dumps(
            self._to_file_payload(),
            ensure_ascii=False,
            separators=(',', ':') if indent is None else None,
            indent=indent,
        ).encode('utf-8')
        self._atomic_write_bytes(target_path, payload)

    @staticmethod
    def _atomic_write_bytes(target_path: str, payload: bytes) -> None:
        directory = os.path.dirname(target_path) or '.'
        temp_file: Optional[IO[bytes]] = None
        temp_path = ''

        try:
            temp_file = tempfile.NamedTemporaryFile(
                mode='wb',
                delete=False,
                dir=directory,
                prefix=f'{os.path.basename(target_path)}.',
                suffix='.tmp',
            )
            temp_path = temp_file.name
            temp_file.write(payload)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_file.close()
            temp_file = None

            os.replace(temp_path, target_path)

            with open(target_path, 'r+b') as target_file:
                os.fsync(target_file.fileno())
        finally:
            if temp_file is not None:
                temp_file.close()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    def load(self) -> None:
        self.clear()

        default_path = self.resolve_default_path()
        local_path = self.resolve_local_path()
        default_version = self.read_version(default_path)
        local_version = self.read_version(local_path)

        if default_version is not None and (local_version is None or default_version > local_version):
            self._load_path(default_path, replace=True)
            self._load_path(local_path, replace=False, merge_missing=True, update_version=False)
            self.version = default_version

        elif os.path.exists(local_path):
            self._load_path(local_path, replace=True)

        else:
            self._load_path(default_path, replace=True)

        self.requires_save = False

    def read_version(self, path: Optional[str] = None) -> Optional[FileVersion]:
        resolved_path = path or self.resolve_active_path()
        if not resolved_path or not os.path.exists(resolved_path):
            return None

        with open(resolved_path, 'rb') as file:
            prefix = file.read(_VERSION_SCAN_BYTES)

        if not prefix:
            return None

        match = _VERSION_PATTERN.search(prefix.decode('utf-8', errors='ignore'))
        if not match:
            return None

        raw_value = match.group(1)
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            parsed = raw_value.strip('"')
        return FileVersion(str(parsed))

    def requires_update(self) -> bool:
        default_version = self.read_version(self.resolve_default_path())
        local_version = self.read_version(self.resolve_local_path())

        if default_version is None:
            return False

        if local_version is None:
            return True

        return default_version > local_version


class DataList(_DataFileMixin, JsonSerializableList[T_SERIALIZABLE_VALUE]):
    def __init__(
        self,
        get_local_path: Callable[..., str],
        get_default_path: Callable[..., str],
        data: Optional[list[T_SERIALIZABLE_VALUE]] = None,
        *,
        version: str = '1.0',
        value_type: Optional[type[T_SERIALIZABLE_VALUE]] = None,
        key_decoder: Optional[Callable[[str], T_DICT_KEY]] = None,
        key_encoder: Optional[Callable[[T_DICT_KEY], str]] = None,
    ):
        super().__init__(item_type=value_type, data=data)
        self.get_local_path = get_local_path
        self.get_default_path = get_default_path
        self.version = FileVersion(version)
        self.requires_save = False

    def _to_file_payload(self) -> dict:
        return {
            'version': str(self.version),
            'data': JsonSerializableList.to_dict(self),
        }

    def _load_path(self, path: str, *, replace: bool, merge_missing: bool = False, update_version: bool = True) -> None:
        if not path or not os.path.exists(path):
            return

        with open(path, 'r', encoding='utf-8') as file:
            payload = json.load(file)

        file_version = payload.get('version', None)
        if update_version and file_version is not None:
            self.version = FileVersion(str(file_version))

        raw_data = cast(list[dict], payload.get('data', []))
        if replace:
            self.replace_from_dict(raw_data)
        elif merge_missing:
            self.merge_missing_from_dict(raw_data)


class DataDict(
    _DataFileMixin,
    JsonSerializableDictionary[T_DICT_KEY, T_SERIALIZABLE_VALUE],
):
    def __init__(
        self,
        get_local_path: Callable[..., str],
        get_default_path: Callable[..., str],
        data: Optional[dict[T_DICT_KEY, T_SERIALIZABLE_VALUE]] = None,
        *,
        version: str = '1.0',
        value_type: Optional[type[T_SERIALIZABLE_VALUE]] = None,
        key_decoder: Optional[Callable[[str], T_DICT_KEY]] = None,
        key_encoder: Optional[Callable[[T_DICT_KEY], str]] = None,
    ):
        super().__init__(value_type=value_type, data=data, key_decoder=key_decoder, key_encoder=key_encoder)
        self.get_local_path = get_local_path
        self.get_default_path = get_default_path
        self.version = FileVersion(version)
        self.requires_save = False

    def _to_file_payload(self) -> dict:
        return {
            'version': str(self.version),
            'data': JsonSerializableDictionary.to_dict(self),
        }

    def _load_path(self, path: str, *, replace: bool, merge_missing: bool = False, update_version: bool = True) -> None:
        if not path or not os.path.exists(path):
            return

        with open(path, 'r', encoding='utf-8') as file:
            payload = json.load(file)

        file_version = payload.get('version', None)
        if update_version and file_version is not None:
            self.version = FileVersion(str(file_version))

        raw_data = cast(Mapping[str, dict], payload.get('data', {}))
        if replace:
            self.replace_from_dict(raw_data)
        elif merge_missing:
            self.merge_missing_from_dict(raw_data)
