#!/bin/bash
# Składa rolkę 15 s z 4 klatek 1080x1920: powolny zoom + przenikania, cicha ścieżka audio.
# Użycie: tools/rolka.sh katalog_z_R1..R4_01.jpg plik_wyjsciowy.mp4
set -e; D=$1; OUT=$2; T=4.125; F=$(python3 -c "print(int($T*30))")
in=""; f=""
for i in 1 2 3 4; do
  in="$in -loop 1 -t $T -i $D/R${i}_01.jpg"
  f="$f[$((i-1)):v]scale=1188:2112,zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$F:s=1080x1920:fps=30,setsar=1[v$i];"
done
f="$f[v1][v2]xfade=transition=fade:duration=0.5:offset=3.625[a];[a][v3]xfade=transition=fade:duration=0.5:offset=7.25[b];[b][v4]xfade=transition=fade:duration=0.5:offset=10.875,format=yuv420p[v]"
ffmpeg -y -loglevel error $in -f lavfi -t 15 -i anullsrc=r=44100:cl=stereo -filter_complex "$f" -map "[v]" -map 4:a -c:v libx264 -preset veryfast -crf 20 -c:a aac -shortest -movflags +faststart "$OUT"
