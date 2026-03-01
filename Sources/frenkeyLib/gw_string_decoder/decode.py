"""Offline Guild Wars encoded string decoder.

Decodes encoded name codepoints to text in any supported language
using pre-extracted string table binaries and gw_string_decode.dll.

    from decode import GwStringDecoder

    dec = GwStringDecoder()                    # loads english by default
    dec = GwStringDecoder("all")               # loads all languages
    dec = GwStringDecoder("french")            # by name
    dec = GwStringDecoder(3)                   # by id (german)
    dec = GwStringDecoder(["english", 2, 9])   # mix of names and ids

    dec.decode([0x8101, 0x47D8, 0xB358, 0xFFE1, 0x4077])
    # → {"english": "Sunspear Scout"}

    dec.decode([0x8101, 0x47D8, 0xB358, 0xFFE1, 0x4077], lang="french")
    # → "Eclaireur des Lanciers du Soleil"

    dec.decode_index(50648, key=0xC641949DE77)
    # → {"english": "Sunspear Scout"}
"""

import ctypes
import os
import re
import struct
from typing import Optional, Union

# ── Language map ─────────────────────────────────────────────────────────

LANGUAGES: dict[int, str] = {
    0: "english", 1: "korean", 2: "french", 3: "german",
    4: "italian", 5: "spanish", 6: "chinese_traditional",
    7: "chinese_simplified", 8: "japanese", 9: "polish", 10: "russian",
}
_NAME_TO_ID: dict[str, int] = {v: k for k, v in LANGUAGES.items()}

# ── Constants ────────────────────────────────────────────────────────────

BASE = 0x0100
MORE = 0x8000
RANGE = MORE - BASE

_GRAMMAR_TAG_RE = re.compile(
    r'^\[(M|F|N|U|P|PM|PF|PN|m|u|null|proper|plur|sing)\]'
)
_BRACKET_SUBS = {"[lbracket]": "[", "[rbracket]": "]"}

# ── C DLL ────────────────────────────────────────────────────────────────

_dll_dir = os.path.dirname(os.path.abspath(__file__))
_c_func = None
_c_in = (ctypes.c_uint8 * 8192)()
_c_out = (ctypes.c_uint16 * 4096)()


def _init_dll() -> None:
    global _c_func
    lib = ctypes.CDLL(os.path.join(_dll_dir, "gw_string_decode.dll"))
    fn = lib.gw_decode_entry
    fn.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint64,
                   ctypes.c_void_p, ctypes.c_int]
    fn.restype = ctypes.c_int
    _c_func = fn


def _decode_entry(entry_data: bytes, key: int) -> Optional[str]:
    if _c_func is None:
        _init_dll()
    n = len(entry_data)
    if n > 8192 or n < 6:
        return None
    ctypes.memmove(_c_in, entry_data, n)
    count = _c_func(ctypes.addressof(_c_in), n, key,
                    ctypes.addressof(_c_out), 4096)
    if count <= 0:
        return None
    return ctypes.wstring_at(ctypes.addressof(_c_out), count)


# ── Parsing ──────────────────────────────────────────────────────────────

def parse_encoded_name(codepoints: list[int]) -> tuple[int, int]:
    """Parse encoded codepoints → (string_index, uint64_key)."""
    if not codepoints:
        return (0, 0)

    idx = 0
    pos = 0
    for pos, cp in enumerate(codepoints):
        if cp == 0:
            break
        digit = (cp & 0x7FFF) - BASE
        if digit < 0:
            break
        if cp & MORE:
            idx = (idx + digit) * RANGE
        else:
            idx = idx + digit
            pos += 1
            break

    key = 0
    if pos < len(codepoints) and codepoints[pos] != 0 and (codepoints[pos] & MORE):
        for i in range(pos, len(codepoints)):
            cp = codepoints[i]
            if cp == 0:
                break
            digit = (cp & 0x7FFF) - BASE
            if digit < 0:
                break
            if cp & MORE:
                key = (key + digit) * RANGE
            else:
                key = key + digit
                break

    return (idx, key)


def _postprocess(text: str) -> str:
    text = _GRAMMAR_TAG_RE.sub('', text)
    for old, new in _BRACKET_SUBS.items():
        if old in text:
            text = text.replace(old, new)
    return text


# ── Table loading ────────────────────────────────────────────────────────

def _resolve_lang(lang: Union[int, str]) -> int:
    """Resolve a language name or id to its integer id."""
    if isinstance(lang, int):
        if lang not in LANGUAGES:
            raise ValueError(f"Unknown language id {lang}. Valid: {list(LANGUAGES.keys())}")
        return lang
    name = lang.lower().strip()
    if name in _NAME_TO_ID:
        return _NAME_TO_ID[name]
    raise ValueError(f"Unknown language {lang!r}. Valid: {list(LANGUAGES.values())}")


def _load_table(lang_id: int) -> dict[int, bytes]:
    name = LANGUAGES[lang_id]
    path = os.path.join(_dll_dir, "tables", f"{lang_id}-{name}.bin")
    if not os.path.exists(path):
        return {}
    table: dict[int, bytes] = {}
    with open(path, 'rb') as f:
        data = f.read()
    pos = 0
    while pos + 8 <= len(data):
        idx, length = struct.unpack_from('<II', data, pos)
        pos += 8
        if pos + length > len(data):
            break
        table[idx] = data[pos:pos + length]
        pos += length
    return table


# ── Decoder class ────────────────────────────────────────────────────────

class GwStringDecoder:
    """Offline decoder for Guild Wars encoded strings.

    Args:
        langs: Which languages to load. Can be:
            - "english" (default), "french", 3, etc. — single language
            - "all" — all available languages
            - ["english", 2, "polish"] — list mixing names and ids
    """

    def __init__(self, langs: Union[str, int, list[Union[str, int]]] = "english"):
        self._tables: dict[int, dict[int, bytes]] = {}
        self._cache: dict[tuple[int, tuple[int, ...]], str] = {}

        if isinstance(langs, str) and langs.lower() == "all":
            lang_ids = list(LANGUAGES.keys())
        elif isinstance(langs, list):
            lang_ids = [_resolve_lang(l) for l in langs]
        else:
            lang_ids = [_resolve_lang(langs)]

        for lid in lang_ids:
            table = _load_table(lid)
            if table:
                self._tables[lid] = table

    @property
    def loaded_languages(self) -> dict[int, str]:
        """Languages currently loaded: {id: name}."""
        return {lid: LANGUAGES[lid] for lid in sorted(self._tables)}

    def decode(self, codepoints: list[int],
               lang: Optional[Union[int, str]] = None) -> Union[str, dict[str, str], None]:
        """Decode encoded codepoints to text.

        Args:
            codepoints: Encoded name codepoints (uint16 values).
            lang: If given, return a single string for that language.
                  If None, return dict of {lang_name: text} for all loaded languages.

        Returns:
            str if lang specified, dict[str, str] if lang=None, None on failure.
        """
        # Inline player names (prefix 0xBA9)
        if len(codepoints) >= 3 and codepoints[0] == 0xBA9:
            end = len(codepoints)
            for i in range(2, end):
                if codepoints[i] <= 1:
                    end = i
                    break
            name = bytes(codepoints[2:end]).decode('ascii', 'ignore')
            if lang is not None:
                return name
            return {LANGUAGES[lid]: name for lid in self._tables}

        idx, key = parse_encoded_name(codepoints)
        if idx == 0:
            return None

        if lang is not None:
            lid = _resolve_lang(lang)
            return self._decode_single(idx, key, lid)

        results: dict[str, str] = {}
        for lid in sorted(self._tables):
            text = self._decode_single(idx, key, lid)
            if text:
                results[LANGUAGES[lid]] = text
        return results if results else None

    def decode_index(self, index: int, key: int = 0,
                     lang: Optional[Union[int, str]] = None) -> Union[str, dict[str, str], None]:
        """Decode by raw string index + key (skip codepoint parsing).

        Same return behavior as decode().
        """
        if lang is not None:
            lid = _resolve_lang(lang)
            return self._decode_single(index, key, lid)

        results: dict[str, str] = {}
        for lid in sorted(self._tables):
            text = self._decode_single(index, key, lid)
            if text:
                results[LANGUAGES[lid]] = text
        return results if results else None

    def _decode_single(self, index: int, key: int, lang_id: int) -> Optional[str]:
        cache_key = (lang_id, (index, key))
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        table = self._tables.get(lang_id)
        if table is None:
            return None
        entry = table.get(index)
        if entry is None:
            return None
        text = _decode_entry(entry, key)
        if text:
            text = _postprocess(text)
            self._cache[cache_key] = text
        return text
