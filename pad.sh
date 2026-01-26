ffmpeg -i "$1" -y -filter_complex "\
[0:v]tpad=stop_mode=clone:stop_duration=1,\
pad=w=iw+80:h=ih+80:x=40:y=40:color=black[v]" \
-map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset veryfast -c:a copy "padded_$1"


#ffmpeg -i "$1" -y  -filter:v "setpts=PTS/1.1" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1" "scaled_$1"
##ffmpeg -i scaled.mp4 -y -filter_complex "[0]pad=w=160+iw:h=160+ih:x=80:y=80:color=#FFB343" padded.mp4
##ffmpeg -i  "scaled_$1" -y -filter_complex "[0]pad=w=160+iw:h=160+ih:x=80:y=80:color=#000000" "padded_$1"
# 80px so

#ffmpeg -i "scaled_$1" -y -filter_complex "\
#[0:v]tpad=stop_mode=clone:stop_duration=1,\
#pad=w=iw+160:h=ih+160:x=80:y=80:color=#000000[v]" \
#-map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset veryfast -c:a copy "padded_$1"


#ffmpeg -i "padded_$1" -filter_complex "[0:v]setpts=PTS/1.05[v];[0:a]rubberband=tempo=1.05:pitch=0.96[a]" -map "[v]" -map "[a]" -y "sped_$1"

#ffmpeg -i "padded_$1" -y -vf "select=eq(n\,0)" -q:v 3 "$1.jpg"


# time AND muting every 20 seconds
#ffmpeg -i padded.mp4 -filter_complex "[0:v]setpts=PTS/1.05[v];[0:a]rubberband=tempo=1.05:pitch=0.96,volume=0:enable='between(mod(t+1,25),0,1)'[a]" -map "[v]" -map "[a]" -y "sped_$1"


#ffmpeg -i "sped_$1" -vf convolution="-2 -1 0 -1 1 1 0 1 2:-2 -1 0 -1 1 1 0 1 2:-2 -1 0 -1 1 1 0 1 2:-2 -1 0 -1 1 1 0 1 2" -c:a copy "vhs_$1"
# 95% the speed so 1/0.95 and 0.95, drop pitch down to 96%
