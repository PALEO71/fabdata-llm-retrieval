#!/usr/bin/env python
"""
Ingest a folder into scirag by tier.

Usage:
    python scripts/run_ingest.py --tier 1 --folder path/to/folder
    python scripts/run_ingest.py --tier 2 --folder path/to/folder --no-skip
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(override=True)

parser = argparse.ArgumentParser()
parser.add_argument("--tier", type=int, required=True, choices=[1, 2, 3, 4])
parser.add_argument("--folder", required=True)
parser.add_argument("--no-skip", action="store_true",
                    help="Re-ingest files already in the database")
args = parser.parse_args()

from scirag.ingest.pipeline import ingest_folder

print(f"Ingesting tier {args.tier} from: {args.folder}")
n = ingest_folder(args.folder, tier=args.tier, skip_existing=not args.no_skip)
print(f"Done — {n} source(s) ingested.")
