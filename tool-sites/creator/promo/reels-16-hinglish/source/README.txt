Hinglish re-cut of the 16 reels. Reuses the live-demo captures from ../reels-16 (out/<id>/cap, cap.json).
1. reels_hi.py   on-screen text (Hinglish, English letters) + voiceover lines (Devanagari + English words)
2. rtts_hi.py    Hindi narrator (Kokoro hm_omega) using phonemes from g2p_cli.mjs, which runs the site's
                 shared/vendor/hindi-g2p.js; writes out/<id>/vo.wav + meta.json (captions in Hinglish)
3. pipeline.sh   rrender.py (reel.html, frame by frame) -> rsound.py (music + sfx) -> ffmpeg mux
reel.html reads the UI strings (manual / turn / cta / bio) from meta.json and stretches each demo
capture to the length of its narration.
