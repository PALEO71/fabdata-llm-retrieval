#!/usr/bin/env python
"""Initialise the scirag SQLite database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv
load_dotenv(override=True)

from scirag.db import init_db
init_db()
