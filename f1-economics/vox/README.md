# Vox-style cold open: how to add real photos and clips

The animation is `cold_open.html`, rendered with `../source/render.py`.
**Real photos drop straight in.** Save a PNG with the exact filename below into `assets/photos/` and re-render. It replaces the halftone placeholder automatically, gets a grayscale collage treatment and a torn white paper border, and keeps all the motion.

| Filename (`assets/photos/…`) | What to source | Where |
|---|---|---|
| `claire_williams.png` | Claire Williams portrait, background removed (PNG with transparency) | Wikimedia Commons / Getty editorial |
| `frank_williams.png` | Sir Frank Williams, 1980s–90s archive | Wikimedia Commons / Getty editorial |
| `williams_car_2020.png` | Williams FW43 (2020) side or 3/4 view | Williams media site / Wikimedia Commons |
| `monza_2020.png` | Monza grandstand or pit lane, 2020 (empty stands) | Getty editorial / F1 media |
| `interview_claire_2020.png` | A still from her Italian GP 2020 interview (swap it for the real clip in the edit) | Sky Sports F1 broadcast |

Cutouts: remove.bg, Photoshop "Remove background", or `rembg` (Python) all work.

## Logos
Real SVG logos from simple-icons are in `assets/logos/`: F1, Ferrari, McLaren, Red Bull, Aston Martin, Renault, Cadillac, Audi, Honda, Netflix, DHL, Shell. Brand colors are applied automatically.

## Palette
Light-gray paper `#E3E1DB` · yellow highlighter `#F6D646` · green cards `#2E8B57` · ink `#161616`.

## Render
```bash
cd f1-economics/vox
PAGE=cold_open.html OUT=./out DUR=90 python3 ../source/render.py video 4
python3 vox_sound.py
ffmpeg -i out/video_silent.mp4 -i cold_open_score.wav -c:v copy -c:a aac -shortest cold_open.mp4
```
