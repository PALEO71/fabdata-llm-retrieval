#!/usr/bin/env python
"""
Run the connection agent layer.

Usage:
    python scripts/run_connections.py --group topical
    python scripts/run_connections.py --all
    python scripts/run_connections.py --group bridges --pairs 100
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(override=True)

parser = argparse.ArgumentParser()
group_arg = parser.add_mutually_exclusive_group(required=True)
group_arg.add_argument("--group",
                       choices=["topical", "bridges", "place", "voice_form",
                                "temporal", "pedagogical", "bilingual"])
group_arg.add_argument("--all", action="store_true")
parser.add_argument("--pairs", type=int, default=50,
                    help="Node pairs to evaluate per agent (default: 50)")
args = parser.parse_args()

from scirag.connections.dispatch import dispatch

group = "all" if args.all else args.group
print(f"Running connection agents — group: {group}, pairs: {args.pairs}")
total = dispatch(group=group, n_pairs=args.pairs)
print(f"Done — {total} connection(s) written.")

# Keep the same git discipline as the Second Brain
repo = Path(__file__).resolve().parents[1]
subprocess.run(["git", "add", "scirag.db"], cwd=repo, check=False)
subprocess.run(
    ["git", "commit", "-m", f"connections: {group} — {total} edges written"],
    cwd=repo, check=False,
)
