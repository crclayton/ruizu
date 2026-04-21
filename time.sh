# 1) Get the duration (in seconds)
duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$1")

echo $duration

# Bar thickness (px)
TH=8

ffmpeg -i "$1" -filter_complex "\
[0:v]setsar=1,\
pad=iw+2*${TH}:ih+2*${TH}:${TH}:${TH}:color=black[v0];\
\
color=color=#FFB343:s=2x${TH}:d=${duration}[cT];\
[cT][v0]scale2ref=eval=frame:w=iw*min(t/${duration}\,1):h=${TH}[barT][v1];\
[v1][barT]overlay=x=0:y=0:eval=frame[v2];\
\
color=color=#FFB343:s=2x${TH}:d=${duration}[cB];\
[cB][v2]scale2ref=eval=frame:w=iw*min(t/${duration}\,1):h=${TH}[barB][v3];\
[v3][barB]overlay=x=W-w:y=H-${TH}:eval=frame[v4];\
\
color=color=#FFB343:s=${TH}x2:d=${duration}[cL];\
[cL][v4]scale2ref=eval=frame:w=${TH}:h=ih*min(t/${duration}\,1)[barL][v5];\
[v5][barL]overlay=x=0:y=0:eval=frame[v6];\
\
color=color=#FFB343:s=${TH}x2:d=${duration}[cR];\
[cR][v6]scale2ref=eval=frame:w=${TH}:h=ih*min(t/${duration}\,1)[barR][v7];\
[v7][barR]overlay=x=W-${TH}:y=H-h:eval=frame" \
-c:a copy -movflags +faststart "time_$1"

exit


# 1) Get the duration (in seconds)
duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $1)

echo $duration

# Bar thickness (px)
TH=8


ffmpeg -i "$1" -filter_complex "\
[0:v]setsar=1[v0];\
color=color=#FFB343:s=2x${TH}:d=${duration}[cT];\
[cT][v0]scale2ref=eval=frame:w=iw*min(t/${duration}\,1):h=${TH}[barT][v1];\
[v1][barT]overlay=x=0:y=0:eval=frame[v2];\
color=color=#FFB343:s=2x${TH}:d=${duration}[cB];\
[cB][v2]scale2ref=eval=frame:w=iw*min(t/${duration}\,1):h=${TH}[barB][v3];\
[v3][barB]overlay=x=W-w:y=H-${TH}:eval=frame[v4];\
color=color=#FFB343:s=${TH}x2:d=${duration}[cL];\
[cL][v4]scale2ref=eval=frame:w=${TH}:h=ih*min(t/${duration}\,1)[barL][v5];\
[v5][barL]overlay=x=0:y=0:eval=frame[v6];\
color=color=#FFB343:s=${TH}x2:d=${duration}[cR];\
[cR][v6]scale2ref=eval=frame:w=${TH}:h=ih*min(t/${duration}\,1)[barR][v7];\
[v7][barR]overlay=x=W-${TH}:y=H-h:eval=frame" \
-c:a copy -movflags +faststart "time_$1"
