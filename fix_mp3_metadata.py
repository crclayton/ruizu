#!/usr/bin/env python3
"""
fix_mp3_metadata.py

Scan only directories whose name starts with a year (YYYY-) and contains MP3s.
Determine the majority artist/album/genre/year/cover-art from the existing tags,
and apply those tags to every track in that folder—preserving each file's
original track title and track number.

Requires: pip install mutagen
"""

import os
import sys
import re
import argparse
from collections import Counter
from mutagen.id3 import (
    ID3, ID3NoHeaderError,
    TPE1, TALB, TCON, TDRC, TYER, APIC, TIT2, TRCK
)

# Only match directories starting with 4 digits and a hyphen, e.g. "1999-Album_Name"
YEAR_DIR_REGEX = re.compile(r'^\d{4}-')

def get_common_tags(files):
    artists, albums, genres, years = [], [], [], []
    cover_data_list, cover_mime_list = [], []
    for fp in files:
        try:
            tags = ID3(fp)
        except ID3NoHeaderError:
            continue

        if 'TPE1' in tags:
            artists.append(tags['TPE1'].text[0])
        if 'TALB' in tags:
            albums.append(tags['TALB'].text[0])
        if 'TCON' in tags:
            genres.append(tags['TCON'].text[0])
        if 'TDRC' in tags:
            years.append(str(tags['TDRC'].text[0]))
        elif 'TYER' in tags:
            years.append(str(tags['TYER'].text[0]))

        apics = tags.getall('APIC')
        if apics:
            cover_data_list.append(apics[0].data)
            cover_mime_list.append(apics[0].mime)

    def mode_or_none(lst):
        return Counter(lst).most_common(1)[0][0] if lst else None

    common_artist = mode_or_none(artists)
    common_album  = mode_or_none(albums)
    common_genre  = mode_or_none(genres)
    common_year   = mode_or_none(years)

    cover_pairs = list(zip(cover_data_list, cover_mime_list))
    if cover_pairs:
        most_common_data = Counter(c for c, m in cover_pairs).most_common(1)[0][0]
        common_mime = next(m for c, m in cover_pairs if c == most_common_data)
    else:
        most_common_data = common_mime = None

    return common_artist, common_album, common_genre, common_year, (common_mime, most_common_data)

def fix_directory(path):
    mp3s = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.mp3')]
    if not mp3s:
        return

    artist, album, genre, year, (mime, cover_data) = get_common_tags(mp3s)
    print(f"\n[Album: {os.path.basename(path)}] Applying →",
          f"Artist={artist!r}, Album={album!r}, Genre={genre!r}, Year={year!r}, Cover={'yes' if cover_data else 'no'}")

    for fp in mp3s:
        try:
            tags = ID3(fp)
        except ID3NoHeaderError:
            tags = ID3()

        title_frame = tags.get('TIT2')
        track_frame = tags.get('TRCK')

        for key in ('TPE1','TALB','TCON','TDRC','TYER','APIC'):
            tags.delall(key)

        if artist:
            tags.add(TPE1(encoding=3, text=artist))
        if album:
            tags.add(TALB(encoding=3, text=album))
        if genre:
            tags.add(TCON(encoding=3, text=genre))
        if year:
            tags.add(TDRC(encoding=3, text=year))
        if cover_data and mime:
            tags.add(APIC(
                encoding=3,
                mime=mime,
                type=3,
                desc='Cover',
                data=cover_data
            ))

        if title_frame:
            tags.add(title_frame)
        if track_frame:
            tags.add(track_frame)

        tags.save(fp)
        print("  ✔", os.path.basename(fp))

def main():
    p = argparse.ArgumentParser(
        description="Fix MP3 tags in year-prefixed directories by majority-vote from existing files."
    )
    p.add_argument('root', help="Album folder (must start with YYYY-) or root folder if using --recursive")
    p.add_argument('-r','--recursive', action='store_true',
                   help="Walk subdirectories and fix each qualifying album-folder found")
    args = p.parse_args()

    def should_process(dirpath):
        name = os.path.basename(dirpath)
        return bool(YEAR_DIR_REGEX.match(name))

    if args.recursive:
        for dirpath, dirnames, filenames in os.walk(args.root):
            if should_process(dirpath) and any(f.lower().endswith('.mp3') for f in filenames):
                fix_directory(dirpath)
    else:
        if should_process(args.root):
            fix_directory(args.root)
        else:
            print(f"Skipping '{args.root}': folder name does not start with 'YYYY-'.")

if __name__ == '__main__':
    main()

