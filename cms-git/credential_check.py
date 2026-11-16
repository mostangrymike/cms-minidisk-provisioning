#!/usr/bin/env python3
"""
Simple offline check to ensure no credentials are embedded in the cms-git tree.
This is a lightweight guard (no external dependencies) to help maintain policy.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SENSITIVE = re.compile(r"(password|passwd|pwd|userid|user|secret|credential)", re.IGNORECASE)


def scan_dir(root: Path) -> list[tuple[str, int, str]]:
    hits = []
    for path in root.rglob("*"):
        if path.is_file():
            if path.name.endswith((".md", ".txt", ".json", ".yaml", ".yml")):
                # lightweight skip for docs
                pass
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, start=1):
                        if SENSITIVE.search(line):
                            hits.append((str(path), i, line.strip()))
            except Exception:
                continue
    return hits


def main(argv=None):
    root = Path(os.environ.get("CMS_ROOT", "."))
    hits = scan_dir(root)
    if hits:
        for p, line, line_text in hits:
            print(f"{p}:{line}:{line_text}")
        return 2
    print("No credentials-like entries detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
