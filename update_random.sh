#!/bin/bash

ORIGINAL_DIR1="/home/crclayton/Music/library/genres/"
ORIGINAL_DIR2="/home/crclayton/Music/library/playlists/"
SONG_DIR="/home/crclayton/Music/library/random_songs"



# Create the destination directory if it doesn't exist
mkdir -p "$SONG_DIR"

rm $SONG_DIR/* -rf

# 500 random songs to the random songs dir
NUM_SONGS=200

# Find all mp3 files and store them in an array
mp3_files=($(find $ORIGINAL_DIR1 $ORIGINAL_DIR2 -type f -iname "*.mp3"))

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
  #echo $random_file
  cp "$random_file" "$SONG_DIR/$(basename "$random_file")"
done

echo "Successfully copied $NUM_SONGS random mp3 files to $SONG_DIR"



# random songs from the recently added to the random new

RECENT_DIR="/home/crclayton/Music/library/recently_added/"
NEW_DIR="/home/crclayton/Music/library/random_new"
NUM_SONGS=50

# Find all mp3 files and store them in an array
mp3_files=($(find $RECENT_DIR -type f -iname "*.mp3"))

# Get the total number of mp3 files
total_files=${#mp3_files[@]}


# Cap to the number of files available, without duplicates
if [ "$total_files" -lt "$NUM_SONGS" ]; then
  echo "Warning: Found only $total_files mp3 files in $RECENT_DIR. Using $total_files instead of $NUM_SONGS."
  NUM_SONGS=$total_files
fi

if [ "$total_files" -eq 0 ]; then
  echo "Error: Found 0 mp3 files in $RECENT_DIR. Skipping $NEW_DIR."
else

# Pick a random selection of unique files and copy them
printf '%s\n' "${mp3_files[@]}" | shuf -n "$NUM_SONGS" | while IFS= read -r random_file; do
  cp "$random_file" "$NEW_DIR/$(basename "$random_file")"
done

echo "Successfully copied $NUM_SONGS random mp3 files to $NEW_DIR"
fi




# random songs from random albums

ALBUM_DIR="/home/crclayton/Music/library/random_albums/"
RANDOM_ALBUM_DIR="/home/crclayton/Music/library/random_albums"
NUM_SONGS=50

# Find all mp3 files and store them in an array
mp3_files=($(find $ALBUM_DIR -type f -iname "*.mp3"))

# Get the total number of mp3 files
total_files=${#mp3_files[@]}

# Check if there are enough mp3 files
#if [ "$total_files" -lt "$NUM_SONGS" ]; then
#  echo "Error: Found only $total_files mp3 files. Need $NUM_SONGS."
#  exit 1
#fi

# Generate random indices and copy the files
for i in $(seq 1 "$NUM_SONGS"); do
  random_index=$((RANDOM % total_files))
  random_file="${mp3_files[$random_index]}"
  #echo $random_file
  cp "$random_file" "$RANDOM_ALBUM_DIR/$(basename "$random_file")"
done

echo "Successfully copied $NUM_SONGS random mp3 files to $RANDOM_ALBUM_DIR"







# Create the destination directory if it doesn't exist
# mkdir -p "$ALBUM_DIR"
#
# # Find all mp3 files and store them in an array
# find library/ -type d -iname "[0-9][0-9][0-9][0-9]-*" | shuf | head -n $NUM_ALBUMS | xargs cp -r -t $ALBUM_DIR
#
# find $ALBUM_DIR -type d
