import json
S = [
 ('cold', 'kinetic', None, None, ["Every video comes with the same boring jobs.", "Timing the script. Checking if your title gets cut off. Making subtitles. Resizing the thumbnail.", "And if you want a map animation, that's an afternoon in After Effects.", "Add it up, and it's hours, for every single upload."]),
 ('intro', 'home', 'Creator Bench', 'fourteen free tools, one site', ["So I built Creator Bench.", "Fourteen free tools for creators, all in one place.", "No sign-up. Nothing gets uploaded. It all runs right in your browser.", "Let me show you every tool."]),
 ('map-stops', 'map-animator', 'Map Animator', 'type the places', ["Let's start with my favourite, the Map Route Animator.", "Type the places in order. Cities work, and so do whole countries.", "For each stop, pick how you travelled. Plane, train, car, ship, or on foot."]),
 ('map-styles', 'map-animator', 'Map Animator', 'pick a look', ["Then pick a look.", "There's explainer paper, vintage atlas, blueprint, night mode, and a satellite style that uses real NASA imagery."]),
 ('map-globe', 'map-animator', 'Map Animator', 'the globe intro', ["Turn on the globe intro, and your video opens on a spinning Earth that zooms into your first stop.", "Press play, and the route draws itself, highlighting every country on the way."]),
 ('map-export', 'map-animator', 'Map Animator', 'export for any platform', ["Choose sixteen by nine for YouTube, or vertical for Reels and Shorts.", "Then hit export. You get a video file with no watermark."]),
 ('script-timer', 'script-timer', 'Script Timer', 'know your video length', ["Script Timer tells you how long your script takes to read out loud.", "Paste it in and pick your speaking pace.", "You get the total length, plus a timestamp for every paragraph."]),
 ('title-preview', 'title-preview', 'Title Preview', 'see where titles cut off', ["Title Preview shows your title and thumbnail the way viewers see them.", "On the home feed, in search, and in the sidebar, so you can spot exactly where your title gets cut off."]),
 ('safe-zones', 'safe-zones', 'Safe Zones', 'nothing hidden behind buttons', ["Safe Zones lays the TikTok, Reels and Shorts buttons over your vertical video.", "So your text never hides behind them."]),
 ('frame-extractor', 'frame-extractor', 'Frame Extractor', 'every frame, one click', ["Frame Extractor pulls frames out of any video.", "Grab the exact frame you need, or extract a whole set and download it as a zip. Perfect for thumbnails."]),
 ('youtube-earnings', 'youtube-earnings', 'Earnings Calculator', 'what your views are worth', ["The Earnings Calculator estimates what your views could earn.", "It adjusts for your niche, and for where your viewers live."]),
 ('image-resizer', 'image-resizer', 'Image Resizer', 'every size, every platform', ["Image Resizer gives you the exact size for every platform.", "YouTube thumbnails, Instagram posts, Shorts covers. And it can compress your image under any file size limit."]),
 ('caption-formatter', 'caption-formatter', 'Caption Formatter', 'line breaks that stick', ["Caption Formatter keeps your line breaks on Instagram.", "It moves hashtags to the end, removes duplicates, and checks every limit."]),
 ('youtube-chapters', 'youtube-chapters', 'YouTube Chapters', 'timestamps YouTube accepts', ["YouTube Chapters builds timestamps from your section lengths.", "Or paste your own, and it checks them against YouTube's rules, so your chapters actually show up."]),
 ('srt-subtitles', 'srt-subtitles', 'Text to SRT', 'script to subtitles', ["Text to S R T turns your script into a subtitle file.", "And if your subtitles are out of sync, it can shift them in seconds."]),
 ('word-counter', 'word-counter', 'Word Counter', 'every limit, live', ["Word Counter checks every platform limit as you type, from YouTube titles to TikTok captions."]),
 ('case-converter', 'case-converter', 'Case Converter', 'one click, any case', ["Case Converter switches between title case, upper case, sentence case and more, in one click."]),
 ('qr-code', 'qr-code', 'QR Code', 'never expires', ["QR Code makes codes for links, text, or Wi-Fi.", "Download them as P N G or S V G. They never expire, and there's no sign-up."]),
 ('pdf-tools', 'pdf-tools', 'JPG to PDF', 'nothing uploaded', ["And JPG to PDF turns your images into a PDF, or merges PDFs together, without uploading anything."]),
 ('outro', 'kinetic', None, None, ["That's all fourteen tools.", "Everything is free, there's no sign-up, and your files never leave your device.", "Try it at creator bench tool dot com. The link is in the description.", "And tell me in the comments, which tool should I build next?"]),
]
json.dump([dict(id=a, page=b, name=c, sub=d, lines=e) for a, b, c, d, e in S], open('script.json', 'w'), indent=1)
print(sum(len(' '.join(x[4]).split()) for x in S), 'words')
