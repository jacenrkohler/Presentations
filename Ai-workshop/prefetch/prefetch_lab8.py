#!/usr/bin/env python3
"""Downloads for lab8 (homework Lab 8: KoboldCpp, Hermes 3 3B, Qwen 0.5B). Run: python3 prefetch_lab8.py   (Windows: py -3 prefetch_lab8.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab8"] + sys.argv[1:]))
