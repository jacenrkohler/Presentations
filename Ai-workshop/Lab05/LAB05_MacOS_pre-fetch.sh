#!/usr/bin/env bash
# LAB05_MacOS_pre-fetch.sh: downloads for Lab 5, Surprise Bonus Lab (macOS).
# Run it from any folder:  bash LAB05_MacOS_pre-fetch.sh
# Extra options go to ai_prefetch.py, for example:  bash LAB05_MacOS_pre-fetch.sh --dry-run
# Optional parts:  bash LAB05_MacOS_pre-fetch.sh --optional
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
LAB1="$ROOT/Lab01"
echo "Lab 5, Surprise Bonus Lab: nothing to download. You need a web browser and an internet connection."
