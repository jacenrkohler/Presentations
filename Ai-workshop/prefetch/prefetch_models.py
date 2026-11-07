#!/usr/bin/env python3
"""Downloads only the model files for the whole workshop (the largest items).
Run: python3 prefetch_models.py   (Windows: py -3 prefetch_models.py)
Add --background to run hidden, --dry-run to preview sizes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["models"] + sys.argv[1:]))
