#!/usr/bin/env python3
"""Downloads for the Lab 1 bonus: Docker images for Ollama, llama.cpp and KoboldCpp, plus the
same model inside Ollama. Run: python3 prefetch_lab1bonus.py   (Windows: py -3 prefetch_lab1bonus.py)
Add --background to run hidden, --dry-run to preview, --dir PATH for your ai-night folder."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_prefetch import main
sys.exit(main(["lab1bonus"] + sys.argv[1:]))
