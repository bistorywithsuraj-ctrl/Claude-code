#!/bin/bash
FF=/tmp/claude-0/-home-user-Claude-code/b8e4b5b5-0315-5db7-bd49-a5dfd041999d/scratchpad/ffmpeg
IDS="map-animator auto-captions youtube-earnings script-timer title-preview image-resizer word-counter safe-zones frame-extractor caption-formatter youtube-chapters srt-subtitles case-converter qr-code pdf-tools video-to-mp3"
i=1
for id in $IDS; do
  if [ -z "$ONLY" ] || [ "$ONLY" = "$id" ]; then
  python3 rrender.py video 4 $id && python3 rsound.py $id && \
  $FF -v error -y -i out/$id/silent.mp4 -i out/$id/mix.wav -map 0:v -map 1:a -c:v libx264 -crf 21 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -shortest final/$(printf %02d $i)-$id-hinglish.mp4 && rm -f out/$id/silent.mp4 && echo "DONE $i $id $(du -h final/$(printf %02d $i)-$id-hinglish.mp4 | cut -f1)"
  fi
  i=$((i+1))
done
echo ALLDONE
