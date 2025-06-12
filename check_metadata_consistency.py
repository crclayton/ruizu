#!/usr/bin/env python3
"""
sync_mp3_year_and_directory.py

Scan directories named like YYYY-Album_Title (year prefixed), and ensure the earliest year between the directory name and the MP3 files’ metadata is applied consistently:
- If an MP3’s tag-year predates the folder’s prefix, rename the folder to that earlier year.
- Otherwise, update all MP3s’ year tags to match the folder’s prefix.

Requires: pip install mutagen
"""

import os
import re
import argparse
from mutagen.id3 import ID3, ID3NoHeaderError, TDRC, TYER

# Match folders starting with YYYY- and capture the year and rest
YEAR_DIR_REGEX = re.compile(r'^(?P<year>\d{4})-(?P<rest>.+)$')


def sync_year(path):
    """Sync the year between directory name and MP3 metadata for a single folder."""
    folder = os.path.basename(path)
    m = YEAR_DIR_REGEX.match(folder)
    if not m:
        return
    dir_year_str = m.group('year')
    rest = m.group('rest')
    try:
        dir_year = int(dir_year_str)
    except ValueError:
        return

    # List MP3 files in this directory
    mp3s = [f for f in os.listdir(path) if f.lower().endswith('.mp3')]
    if not mp3s:
        return

    # Gather tag years
    tag_years = []
    for fname in mp3s:
        full = os.path.join(path, fname)
        try:
            tags = ID3(full)
        except ID3NoHeaderError:
            continue
        # extract either TDRC or TYER
        if 'TDRC' in tags:
            try:
                tag_years.append(int(str(tags['TDRC'].text[0])))
            except Exception:
                pass
        elif 'TYER' in tags:
            try:
                tag_years.append(int(str(tags['TYER'].text[0])))
            except Exception:
                pass

    # Determine earliest year among tags, default to dir_year
    earliest_tag_year = min(tag_years) if tag_years else dir_year

    # If tag-year is earlier than directory-year, rename folder
    if earliest_tag_year < dir_year:
        parent = os.path.dirname(path)
        new_folder_name = f"{earliest_tag_year}-{rest}"
        new_path = os.path.join(parent, new_folder_name)
        try:
            os.rename(path, new_path)
            print(f"Renamed folder: '{folder}' → '{new_folder_name}'")
        except Exception as e:
            print(f"Failed to rename '{folder}': {e}")
    else:
        # Otherwise update all MP3s to dir_year
        for fname in mp3s:
            full = os.path.join(path, fname)
            try:
                tags = ID3(full)
            except ID3NoHeaderError:
                tags = ID3()

            # Remove old year frames
            tags.delall('TDRC')
            tags.delall('TYER')
            # Add new year frame
            tags.add(TDRC(encoding=3, text=str(dir_year)))
            tags.save(full)
            print(f"Updated '{fname}' year tag → {dir_year}")


def main():
    parser = argparse.ArgumentParser(
        description="Synchronize year tags and directory name for year-prefixed MP3 folders."
    )
    parser.add_argument('root', help="Album folder (must start with YYYY-) or root folder if using --recursive")
    parser.add_argument('-r', '--recursive', action='store_true',
                        help="Recursively scan subdirectories for year-prefixed folders")
    args = parser.parse_args()

    if args.recursive:
        for dirpath, dirnames, filenames in os.walk(args.root):
            sync_year(dirpath)
    else:
        sync_year(args.root)


if __name__ == '__main__':
    main()
