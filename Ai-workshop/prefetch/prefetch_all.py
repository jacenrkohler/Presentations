#!/usr/bin/env python3
"""Downloads for the five workshop labs, in the order the labs need them.
Run: python3 prefetch_all.py   (Windows: py -3 prefetch_all.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["all"] + sys.argv[1:]))
