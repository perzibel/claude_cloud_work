#!/usr/bin/env bash
# Usage: analyze.sh <video>  -> duration, size, scene changes, loud seconds
set -euo pipefail
V="${1:?video path}"
echo "== Stream info =="
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of default=nw=1 "$V"
echo "== Scene changes (t, score>0.4) =="
ffmpeg -hide_banner -i "$V" -vf "select='gt(scene,0.4)',showinfo" -an -f null - 2>&1 \
  | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 | head -80 | tr '\n' ' '; echo
echo "== Loudest seconds (RMS dB, top 15) =="
ffmpeg -hide_banner -i "$V" -vn -af "asetnsamples=n=44100,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null - 2>/dev/null \
  | awk -F'[:=]' '/pts_time/{t=$3} /RMS_level/{print t, $NF}' | sort -k2 -g -r | head -15
