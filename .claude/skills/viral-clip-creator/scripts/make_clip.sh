#!/usr/bin/env bash
# Usage: make_clip.sh <video> <start> <end> <out.mp4> "<hook text>" ["<lower caption>"]
# Env: SRT=lyrics.srt (optional burned subtitles), FONT=/path/font.ttf
set -euo pipefail
IN="${1:?}"; SS="${2:?}"; TO="${3:?}"; OUT="${4:?}"; HOOK="${5:-}"; CAP="${6:-}"
FONT="${FONT:-$(fc-match -f '%{file}' 'DejaVu Sans:bold' 2>/dev/null || echo /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf)}"
esc(){ printf '%s' "$1" | sed "s/[\\\\:']/\\\\&/g"; }
DUR=$(awk "BEGIN{print $TO-$SS}")
# 9:16 blurred-background fit (keeps full frame for 16:9 sources)
VF="[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5[bg];[b]scale=1080:-2:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
[ -n "$HOOK" ] && VF="$VF,drawtext=fontfile='$FONT':text='$(esc "$HOOK")':fontsize=64:fontcolor=white:borderw=5:bordercolor=black:x=(w-text_w)/2:y=260:enable='between(t,0,3)'"
[ -n "$CAP" ]  && VF="$VF,drawtext=fontfile='$FONT':text='$(esc "$CAP")':fontsize=48:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=14:x=(w-text_w)/2:y=1450"
[ -n "${SRT:-}" ] && VF="$VF,subtitles='$(esc "$SRT")':force_style='Alignment=2,MarginV=380,FontSize=18,Outline=2'"
ffmpeg -y -hide_banner -ss "$SS" -t "$DUR" -i "$IN" -filter_complex "$VF[v]" -map "[v]" -map 0:a? \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=$(awk "BEGIN{print $DUR-0.4}"):d=0.4" \
  -r 30 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$OUT"
echo "Wrote $OUT"
