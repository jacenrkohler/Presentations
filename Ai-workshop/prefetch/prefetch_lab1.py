#!/usr/bin/env python3
"""Downloads for Lab 1: Python packages and the Qwen3-4B model (2.5 GB). Run: python3 prefetch_lab1.py   (Windows: py -3 prefetch_lab1.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab1"] + sys.argv[1:]))
