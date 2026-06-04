#!/bin/bash

SOURCE_DIR=/home/crclayton/Music/library
TARGET_DIR=/media/crclayton/MP3
#TARGEN_DIR=/media/crclayton/0000-006F/Music

rm /media/crclayton/MP3/recently_added/* -rf
rm /media/crclayton/MP3/random_albums/* -rf
rm /media/crclayton/MP3/random_songs/* -rf


echo "🔍 Scanning for MP3 files in $SOURCE_DIR..."

# Find and sort MP3 files
find "$SOURCE_DIR" -type f -iname "*.mp3" | sort | while read -r src_file; do
    # Get the relative path
    rel_path="${src_file#$SOURCE_DIR/}"

    # Destination file path
    dest_file="$TARGET_DIR/$rel_path"

    #echo $rel_path $dest_file

    # Skip files in the genres folder
    if [[ "$rel_path" == *genres/* ]]; then
        continue
    fi

    # Skip folders managed separately with custom ordering/shuffling
    if [[ "$rel_path" == liked/* || "$rel_path" == new_liked/* || "$rel_path" == new_soft/* || \
          "$rel_path" == new_medium/* || "$rel_path" == random_songs/* || "$rel_path" == random_new/* ]]; then
        continue
    fi

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

