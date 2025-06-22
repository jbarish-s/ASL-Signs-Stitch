#!/usr/bin/env bash
# scripts/concatenate_with_transitions.sh
# Concatenate reference ASL clips with slow-down and smooth fades
# Usage: bash scripts/concatenate_with_transitions.sh A B C

set -euo pipefail

# Configuration
REF_DIR="data/ref_videos"
TMP_DIR="temp_clips"
OUT_DIR="static/outputs"
SPEED_FACTOR=1.25   # setpts multiplier (1.25× slower = 80% speed)
FADE_DUR=1          # duration of fade-in/out in seconds

# Ensure directories exist
mkdir -p "$TMP_DIR" "$OUT_DIR"

# Process each input letter
for letter in "$@"; do
  input="$REF_DIR/${letter}.mp4"
  if [[ ! -f "$input" ]]; then
    echo "Error: File not found: $input" >&2
    exit 1
  fi
  # Probe clip duration
  DURATION=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$input")
  # Calculate fade-out start
  FADE_OUT_START=$(echo "$DURATION - $FADE_DUR" | bc)

  output="$TMP_DIR/${letter}_proc.mp4"
  ffmpeg -y -i "$input" -vf "
    setpts=${SPEED_FACTOR}*PTS,
    fade=t=in:st=0:d=${FADE_DUR},
    fade=t=out:st=${FADE_OUT_START}:d=${FADE_DUR}
  " -c:v libx264 -an "$output"
done

# Create concat list
LIST_FILE="$TMP_DIR/concat_list.txt"
: > "$LIST_FILE"
for letter in "$@"; do
  echo "file '$TMP_DIR/${letter}_proc.mp4'" >> "$LIST_FILE"
done

# Concatenate processed clips without re-encoding
output_video="$OUT_DIR/fingerspelling_${*}.mp4"
ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c copy "$output_video"

# Cleanup
rm "$LIST_FILE"

echo "✅ Created fingerspelling video at $output_video"