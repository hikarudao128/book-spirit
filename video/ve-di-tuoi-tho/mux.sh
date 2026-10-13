#!/usr/bin/env bash
# Mux rendered video + final audio.
# Usage: bash mux.sh build/video.mp4 build/final_audio.wav out/ve-di-tuoi-tho.mp4
# Video stream is copied; audio is padded with silence / trimmed to the exact
# video duration, encoded AAC 192k; +faststart.
set -euo pipefail
if [ $# -ne 3 ]; then
  echo "usage: $0 VIDEO AUDIO OUT" >&2; exit 1
fi
VID="$1"; AUD="$2"; OUT="$3"
mkdir -p "$(dirname "$OUT")"

VDUR=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$VID" || true)
if [ -z "$VDUR" ] || [ "$VDUR" = "N/A" ]; then
  VDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VID")
fi
ADUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUD")
echo "video ${VDUR}s, audio ${ADUR}s -> audio fitted to ${VDUR}s"

ffmpeg -hide_banner -v error -y -i "$VID" -i "$AUD" \
  -filter_complex "[1:a]apad,atrim=0:${VDUR},asetpts=N/SR/TB[a]" \
  -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart "$OUT"

ffprobe -v error -show_entries stream=codec_type,codec_name,duration -of compact=p=0 "$OUT"
echo "wrote $OUT"
