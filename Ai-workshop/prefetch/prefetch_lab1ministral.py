#!/usr/bin/env python3
"""Optional Lab 1 Part 1e downloads: Ministral 3 3B at about 1 GB (about 3.2 GB). Run: python3 prefetch_lab1ministral.py   (Windows: py -3 prefetch_lab1ministral.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab1ministral"] + sys.argv[1:]))
