dir=$1
mpv --shuffle --no-video $(find $1 -type f -iname "*.mp3")
