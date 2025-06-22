#!/usr/bin/env bash
# scripts/vidstab_detect.sh
# Motion detection pass for vid.stab stabilization
# Usage: bash scripts/vidstab_detect.sh data/ref_videos/*.mp4

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <video1.mp4> [video2.mp4 ...]"
  exit 1
fi

for f in "$@"; do
  if [[ ! -f "$f" ]]; then
    echo "File not found: $f" >&2
    exit 1
  fi
  # Detect unstable motion and write transform file (.trf)
  echo "🔍 Detecting motion in $f..."
  ffmpeg -i "$f" \
    -vf vidstabdetect=shakiness=10:accuracy=15:result="${f%.*}.trf" \
    -f null -
  echo "✅ Generated ${f%.*}.trf"
done