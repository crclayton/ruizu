#!/bin/bash

SOURCE_DIR=~/Music/library
TARGET_DIR=/media/crclayton/MP3


rm /media/crclayton/MP3/Recently_Added/* -rf
rm /media/crclayton/MP3/Random_Weekly/* -rf


echo "🔍 Scanning for MP3 files in $SOURCE_DIR..."

# Find and sort MP3 files
find "$SOURCE_DIR" -type f -iname "*.mp3" | sort | while read -r src_file; do
    # Get the relative path
    rel_path="${src_file#$SOURCE_DIR/}"

    # Destination file path
    dest_file="$TARGET_DIR/$rel_path"

    #echo $rel_path $dest_file

    # Only copy if it doesn't exist
    if [ ! -f "$dest_file" ]; then
        echo "📥 Copying: $rel_path"
        mkdir -p "$(dirname "$dest_file")"
        cp "$src_file" "$dest_file"
    #else

        #echo "✅ Already exists: $rel_path"
    fi
done

echo "🎉 Sync complete!"

