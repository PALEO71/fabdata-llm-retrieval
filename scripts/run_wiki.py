#!/usr/bin/env python
"""
Compile wiki pages.

Usage:
    python scripts/run_wiki.py --all
    python scripts/run_wiki.py --theme paleontologia_algarve
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(override=True)

parser = argparse.ArgumentParser()
target = parser.add_mutually_exclusive_group(required=True)
target.add_argument("--all", action="store_true")
target.add_argument("--theme", type=str)
args = parser.parse_args()

from scirag.wiki.compiler import compile_all, compile_wiki
from scirag.wiki.seeds import SEED_THEMES

if args.all:
    results = compile_all()
    for theme, count in results.items():
        status = f"{count} nodes" if count >= 0 else "ERROR"
        print(f"  {theme}: {status}")
else:
    if args.theme not in SEED_THEMES:
        print(f"Unknown theme '{args.theme}'. Available: {list(SEED_THEMES)}")
        sys.exit(1)
    result = compile_wiki(args.theme)
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    print(f"Wiki compiled: {args.theme} ({result['node_count']} nodes)")

# Git commit after batch writes — Second Brain section 7 discipline
repo = Path(__file__).resolve().parents[1]
subprocess.run(["git", "add", "scirag.db"], cwd=repo, check=False)
subprocess.run(
    ["git", "commit", "-m",
     f"wiki: compiled {'all' if args.all else args.theme}"],
    cwd=repo, check=False,
)
print("Done.")
