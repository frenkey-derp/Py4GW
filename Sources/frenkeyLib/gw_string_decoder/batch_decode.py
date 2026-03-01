#!/usr/bin/env python3
"""Batch decode encoded strings from a file into one or more languages.

Usage:
    python batch_decode.py input.txt --lang english,french
    python batch_decode.py input.txt --lang 0,2,korean
    python batch_decode.py input.txt --lang all

Input format (one encoded string per line):
    0x8101 0x47D8 0xB358 0xFFE1 0x4077
    8101 47D8 B358 FFE1 4077
    33025, 18392, 45912, 65505, 16503

Hex values (with or without 0x prefix) and decimal are both accepted.
Commas between values are optional. Lines starting with # are skipped.

Output: one file per language named {input_stem}-{lang_name}.txt
Each line corresponds to the input line. Failed decodes produce empty lines.
"""

import argparse
import os
import sys

from decode import GwStringDecoder, LANGUAGES, _NAME_TO_ID


def parse_codepoints(line: str) -> list[int]:
    """Parse a line of codepoints in any reasonable format."""
    line = line.strip()
    if not line or line.startswith('#'):
        return []
    # Strip commas, split on whitespace
    tokens = line.replace(',', ' ').split()
    cps = []
    for t in tokens:
        t = t.strip()
        if not t:
            continue
        if t.startswith('0x') or t.startswith('0X'):
            cps.append(int(t, 16))
        elif all(c in '0123456789abcdefABCDEF' for c in t) and len(t) >= 3:
            # 4+ hex digits without prefix → treat as hex
            cps.append(int(t, 16))
        else:
            cps.append(int(t))
    return cps


def resolve_langs(spec: str) -> list[str | int]:
    """Parse comma-separated lang spec like 'english,2,korean' or 'all'."""
    if spec.strip().lower() == 'all':
        return ['all']
    parts = []
    for token in spec.split(','):
        token = token.strip()
        if not token:
            continue
        try:
            parts.append(int(token))
        except ValueError:
            parts.append(token)
    return parts


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('input', help='Input file with one encoded string per line')
    p.add_argument('--lang', default='english',
                   help='Comma-separated languages (names or ids), or "all"')
    args = p.parse_args()

    lang_spec = resolve_langs(args.lang)
    if lang_spec == ['all']:
        dec = GwStringDecoder('all')
    else:
        dec = GwStringDecoder(lang_spec)

    # Read and parse input
    with open(args.input, 'r') as f:
        lines = f.readlines()

    entries = [parse_codepoints(line) for line in lines]
    stem = os.path.splitext(args.input)[0]

    for lang_id, lang_name in sorted(dec.loaded_languages.items()):
        out_path = f'{stem}-{lang_name}.txt'
        with open(out_path, 'w', encoding='utf-8') as out:
            decoded = 0
            for i, cps in enumerate(entries):
                raw = lines[i].rstrip('\n\r')
                if raw.lstrip().startswith('#') or not raw.strip():
                    out.write(raw + '\n')
                    continue
                text = dec.decode(cps, lang=lang_id)
                out.write((text or '') + '\n')
                if text:
                    decoded += 1
        print(f'{out_path}: {decoded}/{len(entries)} decoded')


if __name__ == '__main__':
    main()
