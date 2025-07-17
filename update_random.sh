#!/bin/bash

ORIGINAL_DIR="/home/crclayton/Music/library/genres/"
RECENT_DIR="/home/crclayton/Music/library/recently_added/"

SONG_DIR="/home/crclayton/Music/library/random_songs"
NEW_DIR="/home/crclayton/Music/library/random_new"

NUM_SONGS=100

# Create the destination directory if it doesn't exist
mkdir -p "$SONG_DIR"

rm $SONG_DIR/* -rf

# Find all mp3 files and store them in an array
mp3_files=($(find $ORIGINAL_DIR -type f -iname "*.mp3"))

# Get the total number of mp3 files
total_files=${#mp3_files[@]}

# Check if there are enough mp3 files
if [ "$total_files" -lt "$NUM_SONGS" ]; then
  echo "Error: Found only $total_files mp3 files. Need $NUM_SONGS."
  exit 1
fi

# Generate random indices and copy the files
for i in $(seq 1 "$NUM_SONGS"); do
  random_index=$((RANDOM % total_files))
  random_file="${mp3_files[$random_index]}"
  echo $random_file
  cp "$random_file" "$SONG_DIR/$(basename "$random_file")"
done

echo "Successfully copied $NUM_SONGS random mp3 files to $SONG_DIR"

# Find all mp3 files and store them in an array
mp3_files=($(find $RECENT_DIR -type f -iname "*.mp3"))

# Get the total number of mp3 files
total_files=${#mp3_files[@]}

NUM_SONGS=100

# Check if there are enough mp3 files
if [ "$total_files" -lt "$NUM_SONGS" ]; then
  echo "Error: Found only $total_files mp3 files. Need $NUM_SONGS."
  exit 1
fi

# Generate random indices and copy the files
for i in $(seq 1 "$NUM_SONGS"); do
  random_index=$((RANDOM % total_files))
  random_file="${mp3_files[$random_index]}"
  echo $random_file
  cp "$random_file" "$NEW_DIR/$(basename "$random_file")"
done

echo "Successfully copied $NUM_SONGS random mp3 files to $NEW_DIR"




# Create the destination directory if it doesn't exist
# mkdir -p "$ALBUM_DIR"
#
# # Find all mp3 files and store them in an array
# find library/ -type d -iname "[0-9][0-9][0-9][0-9]-*" | shuf | head -n $NUM_ALBUMS | xargs cp -r -t $ALBUM_DIR
#
# find $ALBUM_DIR -type d
