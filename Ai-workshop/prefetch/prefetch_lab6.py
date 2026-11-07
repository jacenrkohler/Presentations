#!/usr/bin/env python3
"""Downloads for lab6 (homework Lab 6: Nielsen's code and MNIST). Run: python3 prefetch_lab6.py   (Windows: py -3 prefetch_lab6.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab6"] + sys.argv[1:]))
