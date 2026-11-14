# Day Off Saving The World — P3rzibel — Reel #1 (Chorus Hook)

**File:** `output/DayOff_Reel_Chorus_Hook_9x16.mp4` (1080×1920, 30 fps, H.264/AAC, -14 LUFS, 25.3 s)
**Cover frame:** `output/DayOff_Reel_cover.jpg`
**Song window used:** 01:04.35 → 01:29.65 (Chorus 1, full 8 lines)

## Why this cut
- It is the title line. "I need a day off saving the world!" is in the first second, so the hook and the song name land together.
- It is relatable. It reads as burnout / "everyone needs me" humour that people send to a friend.
- The visuals change every line (about 3 s) and on every beat in the montage, which helps retention.
- It loops: "…who's gonna carry me through?" rolls straight back into "I need a day off…".

## Virality Predictor score (heuristic estimate): **79 / 100** (post, with minor tweaks)
| Dimension | Score | Note |
|---|---|---|
| Hook (0–3 s) | 21/25 | Title line and text hook from frame 0; the opening image could be more striking |
| Retention & loop | 16/20 | 25 s, scene change every line, clean loop point |
| Emotion & shareability | 12/15 | Strong "tag someone who needs a day off" energy |
| Audio trend-fit | 11/15 | Shoutable chorus; it's a new original, so trend-fit is unproven |
| Visual & format | 7/10 | Native 9:16, safe-zone captions; procedural art is simpler than the planned illustrated video |
| Caption & CTA | 8/10 | See copy below |
| Discoverability | 4/5 | Niche tags plus a collab post |

**Top fix:** swap in real illustrated frames from the full video once they're rendered (same timeline, same captions).

## Post copy
**On-screen hook:** WHEN EVERYONE NEEDS YOU... EVERY DAY
**Caption:**
> Even superheroes need a Friday night 🦸‍♂️😮‍💨 Tag the friend who never gets a day off.
> "Day Off Saving The World" — out now. Full video 🔗 in bio.

**Hashtags (keep it to 5):** #P3rzibel #DayOffSavingTheWorld #AltRock #NewMusic #Superhero

## Posting plan
- Post as a **Reel** with original audio named "Day Off Saving The World – P3rzibel", so others can reuse the sound.
- Pin a comment with the stream/YouTube link; ask "What would YOU do on your day off?" to get comments.
- Reshare to Stories in the first hour and reply to every early comment.
- Post on a weekday evening in your audience's time zone; check the 3 s hold rate and shares after 24 h.
- A/B: next cut = final chorus ("…but I'd still come running for you!") or the ending punchline ("Oh, you've gotta be kidding me").

## Re-rendering / adjusting timing
I estimated the lyric timing from audio analysis (beat grid plus gaps in the vocal). If a line feels early or late, edit its `t` in `render/clip_chorus1.json` and run:
```
python3 render/render_clip.py render/clip_chorus1.json "<song.mp3>" output/DayOff_Reel_Chorus_Hook_9x16.mp4
```
`--frames 66.2,70.0` renders stills for quick checks. The font is Bangers (SIL Open Font License).
