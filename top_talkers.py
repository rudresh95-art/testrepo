#!/usr/bin/env python3
"""List top talkers from a status file, ordered by output bitrate (highest first).

File format (CSV, '#' lines are comments/header):
    host,port,input bps,output bps

Usage:
    top_talkers.py [status.txt] [-n N]
"""
import argparse
import sys
from typing import Iterable, List, NamedTuple, TextIO


class Interface(NamedTuple):
    host: str
    port: str
    input_bps: int
    output_bps: int


def parse(lines: Iterable[str], warn: TextIO = sys.stderr) -> List[Interface]:
    """Parse status lines, skipping blanks, comments and malformed rows."""
    entries = []
    for lineno, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = [f.strip() for f in line.split(",")]
        if len(fields) != 4:
            print(f"line {lineno}: expected 4 fields, got {len(fields)}: {line!r}", file=warn)
            continue
        host, port, in_bps, out_bps = fields
        try:
            entries.append(Interface(host, port, int(in_bps), int(out_bps)))
        except ValueError:
            print(f"line {lineno}: non-numeric bitrate: {line!r}", file=warn)
    return entries


def top_talkers(entries: Iterable[Interface], limit: int = 0) -> List[Interface]:
    """Sort by output bps descending; ties broken by host, port for stable output."""
    ranked = sorted(entries, key=lambda e: (-e.output_bps, e.host, e.port))
    return ranked[:limit] if limit > 0 else ranked


def human(bps: int) -> str:
    for unit in ("bps", "Kbps", "Mbps", "Gbps", "Tbps"):
        if abs(bps) < 1000 or unit == "Tbps":
            return f"{bps:.2f} {unit}" if unit != "bps" else f"{bps} bps"
        bps /= 1000


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?", default="status.txt", help="status file ('-' for stdin)")
    ap.add_argument("-n", "--top", type=int, default=0, help="show only the top N (default: all)")
    args = ap.parse_args(argv)

    if args.file == "-":
        entries = parse(sys.stdin)
    else:
        with open(args.file) as fh:
            entries = parse(fh)

    print(f"{'#':>3}  {'host':<10} {'port':<8} {'output bps':>14} {'(human)':>12} {'input bps':>14}")
    for rank, e in enumerate(top_talkers(entries, args.top), 1):
        print(f"{rank:>3}  {e.host:<10} {e.port:<8} {e.output_bps:>14} {human(e.output_bps):>12} {e.input_bps:>14}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
