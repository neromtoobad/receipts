#!/bin/bash
# Record the cold-start recall beat as one continuous take.
#
# Run this from a Terminal window that is FULL SCREEN, so nothing else is in
# shot. It starts the screen recording, runs the real demo, and stops the
# recording when the demo finishes — one paste, no timing to coordinate, and
# no cut anywhere inside the segment, which is what the gate asks for.
#
#   ./scripts/record_demo.sh [market_id]
set -u
cd "$(dirname "$0")/.."

MARKET=${1:-championship:2026-09-01:Portsmouth:Derby}
OUT="video/recall_$(date -u +%Y%m%dT%H%M%SZ).mp4"
mkdir -p video

# The bench saturates Ollama, which turns a 6-second forecast into 25 seconds
# of dead air on camera. SIGSTOP pauses it where it stands and SIGCONT resumes
# it, so the recording is crisp and the run loses nothing. The trap matters:
# if this script dies, the bench must not be left stopped forever.
BENCH=$(pgrep -f "bench.run" | head -1 || true)
resume () { [ -n "${BENCH:-}" ] && kill -CONT "$BENCH" 2>/dev/null && echo "bench resumed"; }
trap resume EXIT INT TERM
if [ -n "$BENCH" ]; then kill -STOP "$BENCH" 2>/dev/null && echo "bench paused (pid $BENCH)"; fi

printf '\033[2J\033[H'
echo "Recording starts in 3 seconds. Do not switch windows until it says DONE."
sleep 3

ffmpeg -y -f avfoundation -capture_cursor 1 -framerate 30 -i "1:none" \
       -c:v libx264 -preset ultrafast -crf 20 -pix_fmt yuv420p "$OUT" \
       >/tmp/rec.log 2>&1 &
REC=$!
sleep 2

PUNDIT=${PUNDIT:-vertex} ./scripts/demo_recall.sh "$MARKET"

sleep 2
# 'q' on stdin is how ffmpeg finalises the file. Killing it truncates the mp4.
kill -INT $REC 2>/dev/null
wait $REC 2>/dev/null

echo
if [ -s "$OUT" ]; then
  DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" 2>/dev/null)
  echo "DONE — $OUT (${DUR}s)"
else
  echo "DONE — but $OUT is empty. See /tmp/rec.log"
fi
