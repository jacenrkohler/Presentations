#!/usr/bin/env python3
"""Optional Lab 1 Part 2c downloads: PyTorch, an image recognizer and an image generator (about 3 GB). Run: python3 prefetch_lab1images.py   (Windows: py -3 prefetch_lab1images.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab1images"] + sys.argv[1:]))
