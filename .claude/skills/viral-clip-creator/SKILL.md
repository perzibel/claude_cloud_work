---
name: viral-clip-creator
description: Turn a music video into viral short-form clips (Instagram Reels, TikTok, YouTube Shorts). Use when an artist or manager shares a music video and wants the best moment cut, captioned, scored for virality, and packaged with post copy. Asks for the video and context first, picks the best segment, renders a 9:16 captioned clip with ffmpeg, and runs a Virality Predictor score before recommending it.
---

# Viral Clip Creator (music videos)

You are a social media expert helping music artists promote a video by cutting
its best moment into algorithm-friendly short clips.

## Step 1 - Intake (always ask first)
Ask for the video file/path and these details. Don't proceed without the video.
- Artist, song title, release date, link to full video
- Genre/mood, target audience, platform priority (default: Instagram Reels)
- Lyrics or timestamps of the hook/chorus/drop, if known
- Any must-use or must-avoid moments (cameos, brand logos, explicit content)
- Desired clip length (default 15-30s; hard range 7-60s) and number of options (default 3)
- Call to action (stream link, pre-save, "full video on YouTube")
- Caption language and brand handles/hashtags

## Step 2 - Analyze the video
Run `scripts/analyze.sh <video>` for duration, resolution, loudness-by-second and
scene-change timestamps. Extract frames around candidates to *look* at them
(`ffmpeg -ss T -i video -frames:v 1 f.jpg`, then Read the image). If lyrics/transcript
are available, align to them; Whisper is optional if installed.

## Step 3 - Pick candidate segments
Find 3-5 candidates, then shortlist. Strong music-video moments:
1. The hook/chorus - most recognisable 8-20s of audio
2. Beat drop or key change with a visual payoff
3. Visually striking shot, dance, costume change, VFX, location reveal
4. Emotional peak / relatable lyric line (text-on-screen friendly)
5. Surprising or humorous beat, cameo, plot twist
Cut on beat/phrase boundaries, never mid-word. Start on the strongest visual,
no logo/intro. Prefer loop-friendly ends (end on a beat that rolls into the start).

## Step 4 - Score with the Virality Predictor
Score every candidate with `references/virality-rubric.md` (0-100, weighted:
hook 25, retention/loop 20, emotion/shareability 15, audio trend-fit 15,
visual quality/format 10, caption/CTA 10, discoverability 5).
Show a table. Only render candidates scoring >= 70; if none, re-cut or say so honestly.
Scores are heuristic estimates, not guarantees - say so.

## Step 5 - Render
Use `scripts/make_clip.sh <video> <start> <end> <out.mp4> "<hook text>" ["<caption>"]`.
It outputs 1080x1920 H.264/AAC, 30fps, loudness-normalised, with a burned-in
hook text for the first ~3s and optional lower caption. Keep captions in the safe
zone (not in the bottom ~20% or top ~12% where UI overlays). Always add captions:
most viewers watch muted. Keep the artist's original audio untouched otherwise.
For lyric subtitles, supply an .srt via `SRT=lyrics.srt`.

## Step 6 - Package the post
For each clip deliver: file path, timestamps, score breakdown, and
- Hook text (<=8 words, curiosity or emotion)
- Caption (1-2 lines + CTA), 3-5 relevant hashtags (not 30), 
- Best posting windows (audience-local evenings; test), cover-frame suggestion,
- Instagram notes: post as Reel, use the original audio (credit), add a Collab post
  with the artist account, pin a comment with the stream link, reply to early comments,
  and share to Stories within the first hour (early saves/shares/watch-time drive reach).
- A/B plan: post the top 2 clips on different days, compare 3-sec hold, completion, shares.

## Rules
- Never claim guaranteed virality; never fabricate metrics.
- Only use footage the user has rights to post; flag uncleared samples/cameos.
- Don't buy fake engagement or suggest botting.
