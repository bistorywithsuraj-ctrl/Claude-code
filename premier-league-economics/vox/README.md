# Episode 2 cold open: how to add real photos and clips

The animation is `cold_open.html`, rendered with `../source/render.py` (same pipeline as Episode 1).
**Real photos drop straight in.** Save a PNG with the exact filename below into `assets/photos/` and re-render. It replaces the halftone placeholder automatically, gets a grayscale collage treatment and a torn white paper border, and keeps all the motion.

| Filename (`assets/photos/…`) | What to source | Where |
|---|---|---|
| `stamford_bridge_2022.png` | Stamford Bridge exterior or empty stands, March 2022 | Getty editorial / Reuters |
| `chelsea_shop_closed.png` | The Chelsea megastore with shutters down, 10–11 March 2022 | Getty editorial / PA Images |
| `abramovich.png` | Roman Abramovich portrait, background removed (PNG with transparency) | Wikimedia Commons / Getty editorial |
| `headline_2003.png` | A July 2003 back page or web headline on the Chelsea takeover (replaces the drawn clipping) | BBC Sport archive, newspaper archive |
| `interview_tuchel_2022.png` | A still from Thomas Tuchel's 10 March 2022 press conference (swap it for the real clip in the edit) | Chelsea FC / Sky Sports News |

Cutouts: remove.bg, Photoshop "Remove background", or `rembg` (Python) all work.

## Logos
Real SVG logos from simple-icons are in `assets/logos/`: Premier League, Sky, TNT, NBC, Amazon Prime, DAZN, Paramount+, BBC, Nike, Adidas, Emirates, EA. Brand colours are applied automatically (dark ink where the brand mark is white or multicolour). Club crests are not included: they are trademarks, so source them from the clubs' media sites for editorial use.

## Palette
Light-gray paper `#E3E1DB` · yellow highlighter `#F6D646` · green cards `#2E8B57` · ink `#161616` · stamp red `#D6453D`.

## Render
```bash
cd premier-league-economics/vox
PAGE=cold_open.html OUT=./out DUR=90 python3 ../source/render.py video 4
python3 vox_sound.py
ffmpeg -i out/video_silent.mp4 -i cold_open_score.wav -c:v copy -c:a aac -shortest cold_open_preview.mp4
```
No system `ffmpeg`? Use the one bundled with imageio: `$(python3 -c 'import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())')` in place of `ffmpeg`.

Stills for checking layout: `PAGE=cold_open.html OUT=./out python3 ../source/render.py stills 9 21 36 47 60 72 82`.
