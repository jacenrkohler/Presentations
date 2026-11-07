#!/usr/bin/env python3
"""Downloads for lab9 (homework Lab 9: the abliterated model). Run: python3 prefetch_lab9.py   (Windows: py -3 prefetch_lab9.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab9"] + sys.argv[1:]))
