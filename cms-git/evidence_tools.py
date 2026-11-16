from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Tuple

from .evidence_schema import validate_evidence


def load_evidences(directory: str | Path) -> Iterable[Tuple[Path, dict]]:
    base = Path(directory)
    for p in sorted(base.glob("*.json")):
        try:
            with p.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                yield p, data
        except Exception:
            # skip invalid json files gracefully
            continue


def validate_all(directory: str | Path) -> int:
    count = 0
    for path, data in load_evidences(directory):
        try:
            validate_evidence(data)
        except Exception:
            count += 1
    return count


def summarize(directory: str | Path) -> dict:
    valid = 0
    invalid = 0
    for _, data in load_evidences(directory):
        try:
            validate_evidence(data)
            valid += 1
        except Exception:
            invalid += 1
    return {"valid": valid, "invalid": invalid, "total": valid + invalid}


def diff_files(a: str, b: str) -> str:
    import difflib
    with open(a, "r", encoding="utf-8") as fa, open(b, "r", encoding="utf-8") as fb:
        a_lines = fa.readlines()
        b_lines = fb.readlines()
    return "".join(difflib.unified_diff(a_lines, b_lines, fromfile=a, tofile=b))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Evidence manager (offline)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_load = sub.add_parser("summarize")
    p_load.add_argument("directory")
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("directory")
    p_diff = sub.add_parser("diff")
    p_diff.add_argument("a")
    p_diff.add_argument("b")
    args = ap.parse_args()
    if args.cmd == "summarize":
        print(summarize(args.directory))
    elif args.cmd == "validate":
        print({"invalid": validate_all(args.directory)})
    elif args.cmd == "diff":
        print(diff_files(args.a, args.b))
