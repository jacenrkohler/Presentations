#!/usr/bin/env python3
"""Downloads for the bonus labs (benchmark matrix files, llama.cpp image, notes).
Run: python3 prefetch_bonus.py   (Windows: py -3 prefetch_bonus.py)
Options: --with-mistral (4.4 GB, needs 16 GB RAM), --big (qwen2.5:7b), --background, --dry-run."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["bonus"] + sys.argv[1:]))
