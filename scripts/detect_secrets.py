#!/usr/bin/env python3
"""Cross-platform Secret Detection Scanner for Habot Connect CI/CD.

Enforces Poka-Yoke fail-closed security gates by scanning codebase for
hardcoded private keys, tokens, and cloud credentials before deployment.
"""

import argparse
import os
import re
import sys
from pathlib import Path

# High-confidence credential and key signatures
SECRET_PATTERNS = [
    (
        "Private Key Header",
        re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ),
    (
        "Google Cloud API Key",
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),
    ),
    (
        "AWS Access Key ID",
        re.compile(r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
    ),
    (
        "Slack Token",
        re.compile(r"xox[baprs]-[0-9]{12}-[0-9]{12,13}-[a-zA-Z0-9]{24,32}"),
    ),
    (
        "Generic High-Entropy Secret Assignment",
        re.compile(r"""(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token)\s*=\s*['\"][A-Za-z0-9+/=_-]{20,}['\"]"""),
    ),
]

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "tools",
    "__pycache__",
    ".pytest_cache",
    ".terraform",
    "evidence",
}

IGNORED_EXTENSIONS = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".zip",
    ".exe",
    ".hcl",
    ".txt",
    ".log",
}


def scan_file(file_path: Path):
    findings = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                for rule_name, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        findings.append((line_no, rule_name, line.strip()[:60]))
    except (OSError, UnicodeDecodeError) as e:
        print(f"[WARN] Unable to read {file_path}: {e}")
    return findings


def main():
    parser = argparse.ArgumentParser(description="Poka-Yoke Secret Scanner")
    parser.add_argument("--target", type=str, default=".", help="Directory or file to scan")
    parser.add_argument("--exclude", nargs="*", default=[], help="Relative paths to exclude")
    args = parser.parse_args()

    root = Path(args.target).resolve()
    exclude_paths = [Path(p).resolve() for p in args.exclude]

    print("==================================================")
    print("  HABOT CONNECT: POKA-YOKE SECRET SCANNER GATE   ")
    print("==================================================")
    print(f"Scanning target: {root}")
    if exclude_paths:
        print(f"Excluded paths: {[str(p) for p in exclude_paths]}")

    files_to_scan = []
    if root.is_file():
        files_to_scan.append(root)
    else:
        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix in IGNORED_EXTENSIONS:
                    continue
                if any(ex in fpath.parents or ex == fpath for ex in exclude_paths):
                    continue
                files_to_scan.append(fpath)

    total_findings = 0
    flagged_files = 0

    for fpath in files_to_scan:
        findings = scan_file(fpath)
        if findings:
            flagged_files += 1
            total_findings += len(findings)
            rel_path = fpath.relative_to(root) if root.is_dir() else fpath.name
            print(f"\n[SECURITY ALERT] Secrets detected in '{rel_path}':")
            for line_no, rule, snippet in findings:
                print(f"  Line {line_no} [{rule}]: {snippet}...")

    print("\n--------------------------------------------------")
    print(f"Total files scanned:  {len(files_to_scan)}")
    print(f"Flagged files:        {flagged_files}")
    print(f"Total secret alerts:  {total_findings}")
    print("--------------------------------------------------")

    if total_findings > 0:
        print("\n[FAIL-CLOSED GATE TRIGGERED] Secrets detected! Halting pipeline execution.")
        sys.exit(1)

    print("\n[GATE PASSED] No secrets detected. Repository clean.")
    sys.exit(0)


if __name__ == "__main__":
    main()
