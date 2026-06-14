#!/bin/bash

# ── Config ────────────────────────────────────────────────────────────────────
SOURCE_DIR=/home/crclayton/Music/library
TARGET_DIR=/media/crclayton/MP3

DIRS_REVERSE_ALPHA=(new_soft new_medium new_liked)   # copied newest-first (date-prefixed filenames)
DIRS_ALPHA=(random_new)                               # copied a→z
DIRS_SHUFFLED=(random_songs)                   # copied in random order # liked
DIRS_CLEAR=(recently_added random_albums)            # cleared only, not rebuilt

DIRS_SPECIAL=("${DIRS_REVERSE_ALPHA[@]}" "${DIRS_ALPHA[@]}" "${DIRS_SHUFFLED[@]}")
# ──────────────────────────────────────────────────────────────────────────────

# Step 1 – Rebuild xspf playlists (parallel)
echo "--- Recreating playlist files ---"
python3 sync_xspf.py library/playlists/soft/            -o soft.xspf &
python3 sync_xspf.py library/playlists/medium/          -o medium.xspf &
python3 sync_xspf.py library/playlists/hard/            -o hard.xspf &
python3 sync_xspf.py library/playlists/mixter_n_mixtus/ -o mixternmixtus.xspf &
python3 sync_xspf.py library/playlists/hits/            -o hits.xspf &
wait

# Step 2 – Build liked folder, then its xspf
echo "--- Creating liked folder ---"
cp --update=none "$SOURCE_DIR/playlists/medium/"* "$SOURCE_DIR/liked"
cp --update=none "$SOURCE_DIR/playlists/soft/"*   "$SOURCE_DIR/liked"
python3 sync_xspf.py library/liked/ -o liked.xspf

# Step 3 – Clear SD dirs (DIRS_CLEAR = contents only; DIRS_SPECIAL = whole dir, rebuilt below)
echo "--- Clearing SD targets ---"
for dir in "${DIRS_CLEAR[@]}";   do rm -f "${TARGET_DIR}/$dir"/*; done
for dir in "${DIRS_SPECIAL[@]}"; do rm -rf "${TARGET_DIR:?}/$dir"; done

# Step 4 – Copy new MP3s to SD, skipping special dirs and genres
echo "--- Uploading new library files to SD ---"
skip_regex="^($(IFS='|'; echo "${DIRS_SPECIAL[*]}"))/"

find "$SOURCE_DIR" -type f -iname "*.mp3" | sort | while IFS= read -r src_file; do
    rel_path="${src_file#$SOURCE_DIR/}"
    [[ "$rel_path" == *genres/*  ]]  && continue
    [[ "$rel_path" =~ $skip_regex ]] && continue
    dest_file="$TARGET_DIR/$rel_path"
    if [[ ! -f "$dest_file" ]]; then
        echo "📥 $rel_path"
        mkdir -p "$(dirname "$dest_file")"
        cp "$src_file" "$dest_file"
    fi
done

# Step 5 – Delete SD files that no longer exist in library
echo "--- Deleting SD files not in library ---"
exclude_args=()
for dir in "${DIRS_SPECIAL[@]}"; do exclude_args+=(--exclude="$dir/"); done
rsync -hvrltD --modify-window=2 --size-only --delete \
    "${exclude_args[@]}" \
    "$SOURCE_DIR/" "$TARGET_DIR"

# Step 6 – Rebuild specially-ordered dirs in parallel
echo "--- Syncing specially-ordered playlists ---"

_copy_dir() {
    local dir=$1 order=$2
    local src="$SOURCE_DIR/$dir" dst="$TARGET_DIR/$dir"
    mkdir -p "$dst"
    case "$order" in
        reverse) find "$src" -maxdepth 1 -type f | sort -r ;;
        alpha)   find "$src" -maxdepth 1 -type f | sort    ;;
        shuffle) find "$src" -maxdepth 1 -type f | shuf    ;;
    esac | while IFS= read -r f; do cp "$f" "$dst/"; done
    echo "  ✓ $dir"
}

echo "reverse-alphabetical (newest songs listed first)"
for dir in "${DIRS_REVERSE_ALPHA[@]}"; do echo "> $dir"; _copy_dir "$dir" reverse; done

echo "alphabetical (track-chronological)"
for dir in "${DIRS_ALPHA[@]}";         do echo "> $dir"; _copy_dir "$dir" alpha;   done

echo "shuffled"
for dir in "${DIRS_SHUFFLED[@]}";      do echo "> $dir"; _copy_dir "$dir" shuffle; done

echo "--- Done ---"
