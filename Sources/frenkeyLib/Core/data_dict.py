import json
import os
import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Callable, Generic, Mapping, Optional, cast

from Sources.frenkeyLib.Core.json_serializable import JsonSerializableDictionary, T_DICT_KEY, T_SERIALIZABLE_VALUE, JsonSerializableList


_VERSION_PATTERN = re.compile(r'"version"\s*:\s*("([^"\\]|\\.)*"|-?\d+(?:\.\d+)?)')
_VERSION_SCAN_BYTES = 512


@total_ordering
@dataclass(frozen=True)
class FileVersion:
    raw: str

    def __post_init__(self):
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


class DataList(JsonSerializableList[T_SERIALIZABLE_VALUE]):
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

    def resolve_local_path(self) -> str:
        return self.get_local_path()

    def resolve_default_path(self) -> str:
        return self.get_default_path()

    def resolve_active_path(self) -> str:
        local_path = self.resolve_local_path()
        if os.path.exists(local_path):
            return local_path
        return self.resolve_default_path()

    def to_dict(self) -> dict:
        return {
            'version': str(self.version),
            'data': super().to_dict(),
        }
        
    def queue_save(self):
        self.requires_save = True

    def save(self, path: Optional[str] = None, *, indent: Optional[int] = None):
        target_path = path or self.resolve_local_path()
        directory = os.path.dirname(target_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(target_path, 'w', encoding='utf-8') as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, separators=(',', ':') if indent is None else None, indent=indent)
        self.requires_save = False

    def load(self):
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

    def _load_path(self, path: str, *, replace: bool, merge_missing: bool = False, update_version: bool = True):
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

class DataDict(JsonSerializableDictionary[T_DICT_KEY, T_SERIALIZABLE_VALUE]):
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

    def resolve_local_path(self) -> str:
        return self.get_local_path()

    def resolve_default_path(self) -> str:
        return self.get_default_path()

    def resolve_active_path(self) -> str:
        local_path = self.resolve_local_path()
        if os.path.exists(local_path):
            return local_path
        return self.resolve_default_path()

    def to_dict(self) -> dict:
        return {
            'version': str(self.version),
            'data': super().to_dict(),
        }
        
    def queue_save(self):
        self.requires_save = True

    def save(self, path: Optional[str] = None, *, indent: Optional[int] = None):
        target_path = path or self.resolve_local_path()
        directory = os.path.dirname(target_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(target_path, 'w', encoding='utf-8') as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, separators=(',', ':') if indent is None else None, indent=indent)
        self.requires_save = False

    def load(self):
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

    def _load_path(self, path: str, *, replace: bool, merge_missing: bool = False, update_version: bool = True):
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
