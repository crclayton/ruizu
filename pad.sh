ffmpeg -i "$1" -y  -filter:v "setpts=PTS/1.1" -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1" scaled.mp4
#ffmpeg -i scaled.mp4 -y -filter_complex "[0]pad=w=160+iw:h=160+ih:x=80:y=80:color=#FFB343" padded.mp4
ffmpeg -i scaled.mp4 -y -filter_complex "[0]pad=w=160+iw:h=160+ih:x=80:y=80:color=#000000" padded.mp4
# 80px so
ffmpeg -i padded.mp4 -filter_complex "[0:v]setpts=0.95*PTS[v];[0:a]atempo=1.05[a]" -map "[v]" -map "[a]" -y "sped_$1"
# 95% the speed so 1/0.95 and 0.95
