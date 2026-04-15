#!/usr/bin/env bash
# download_session.sh — fetch a YouTube panel for the AI Assembly transcription pipeline.
#
# Usage:
#   ./download_session.sh "https://www.youtube.com/watch?v=XXXX" sessions/my_session/audio.m4a
#
# Re-encodes to 96 kbps mono AAC — the sweet spot for ASR on spoken-word
# content. WER on Universal-3 Pro is flat from ~256 kbps down to ~64 kbps;
# 96 kbps gives clean fidelity with ~3x smaller files than yt-dlp's default,
# and mono cuts another 2x because panel speech is effectively single-channel.
#
# Requires: yt-dlp, ffmpeg, both already installed in the project venv.

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <youtube_url> <output_path>"
    echo "Example: $0 'https://www.youtube.com/watch?v=XXXX' sessions/my_session/audio.m4a"
    exit 1
fi

URL="$1"
OUTPUT="$2"
OUTPUT_DIR=$(dirname "$OUTPUT")

mkdir -p "$OUTPUT_DIR"

yt-dlp \
    -x \
    --audio-format m4a \
    --postprocessor-args "ffmpeg:-b:a 96k -ac 1" \
    -o "$OUTPUT" \
    "$URL"

# Report final size and duration
SIZE_MB=$(ls -l "$OUTPUT" | awk '{printf "%.1f", $5/1024/1024}')
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null)
DURATION_MIN=$(printf "%.1f" "$(echo "$DURATION / 60" | bc -l)")
BITRATE=$(ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 "$OUTPUT" 2>/dev/null)
BITRATE_KBPS=$((BITRATE / 1000))

echo ""
echo "Done: $OUTPUT"
echo "  $SIZE_MB MB · $DURATION_MIN min · $BITRATE_KBPS kbps mono"
