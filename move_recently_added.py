#!/usr/bin/env python3

import os
import re
import shutil
import argparse
import sys
from pathlib import Path

YEAR_PREFIX = re.compile(r'^\d{4}-')

def get_album_dirs(source: Path):
    """
    Recursively collect all album directories under source whose names start with a year,
    excluding the 'recently_added' folder itself.
    """
    albums = []
    skip = source / "recently_added"
    for root, subdirs, _ in os.walk(source):
        if Path(root) == skip:
            continue
        for subdir in subdirs:
            if not YEAR_PREFIX.match(subdir):
                continue
            full_path = Path(root) / subdir
            if skip in full_path.parents:
                continue
            albums.append(full_path)
    return albums

def main():
    parser = argparse.ArgumentParser(
        description="Copy the 10 most recent year-prefixed album dirs, appending artist name"
    )
    parser.add_argument(
        "--source", type=Path,
        default=Path("/home/crclayton/Music/library/genres"),
        help="Root folder of library library"
    )
    parser.add_argument(
        "--dest", type=Path,
        default=Path("/home/crclayton/Music/library/recently_added"),
        help="Destination for recently added albums"
    )
    parser.add_argument(
        "--count", type=int, default=10,
        help="Number of albums to copy"
    )
    args = parser.parse_args()
    source = args.source
    dest = args.dest
    count = args.count

    if not source.is_dir():
        print(f"Error: source '{source}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    dest.mkdir(parents=True, exist_ok=True)

    # collect only year-prefixed album dirs
    album_dirs = get_album_dirs(source)

    # pair with creation time
    dirs_with_ctime = []
    for d in album_dirs:
        try:
            dirs_with_ctime.append((d, d.stat().st_mtime))
        except Exception as e:
            print(f"Warning: cannot stat '{d}': {e}", file=sys.stderr)

    # sort by newest first, then take top N
    dirs_with_ctime.sort(key=lambda x: x[1], reverse=True)
    recent_albums = [d for d, _ in dirs_with_ctime[:count]]

    # copy each, appending the artist (parent folder name)
    for album in recent_albums:
        artist = album.parent.name
        new_name = album.name[:4] + "-" + artist + album.name[4:]
        #new_name = f"{album.name}-{artist}"
        target = dest / new_name

        # avoid collisions
        if target.exists():
            i = 1
            while True:
                candidate = dest / f"{new_name}_{i}"
                if not candidate.exists():
                    target = candidate
                    break
                i += 1

        try:
            shutil.copytree(album, target)
            print(f"Copied: {album} → {target}")
        except Exception as e:
            print(f"Failed to copy '{album}': {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

