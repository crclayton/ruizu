#!/usr/bin/env python3
"""
Script to crop embedded album art in audio files to be square.
Supports MP3 (ID3), FLAC, and MP4/M4A files using Mutagen and Pillow.
Usage:
    python crop_album_art.py <directory>
"""
import os
import sys
from io import BytesIO
from PIL import Image
from mutagen.id3 import ID3, APIC, error as ID3Error
from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Cover

def crop_to_square(img: Image.Image) -> Image.Image:
    width, height = img.size
    if width == height:
        return img
    # Center crop larger dimension
    if width > height:
        delta = (width - height) // 2
        box = (delta, 0, width - delta, height)
    else:
        delta = (height - width) // 2
        box = (0, delta, width, height - delta)
    return img.crop(box)

def process_mp3(path: str):
    try:
        tags = ID3(path)
    except ID3Error:
        return
    apics = tags.getall('APIC')
    if not apics:
        return
    modified = False
    for apic in apics:
        img = Image.open(BytesIO(apic.data))
        sq = crop_to_square(img)
        if sq.size != img.size:
            buf = BytesIO()
            sq.save(buf, format=img.format or 'PNG')
            apic.data = buf.getvalue()
            modified = True
    if modified:
        tags.save(path)
        print(f"Cropped album art in MP3: {path}")

def process_flac(path: str):
    audio = FLAC(path)
    pics = audio.pictures
    if not pics:
        return
    modified = False
    for pic in pics:
        img = Image.open(BytesIO(pic.data))
        sq = crop_to_square(img)
        if sq.size != img.size:
            buf = BytesIO()
            fmt = img.format or 'PNG'
            sq.save(buf, format=fmt)
            pic.data = buf.getvalue()
            pic.width, pic.height = sq.size
            modified = True
    if modified:
        audio.save()
        print(f"Cropped album art in FLAC: {path}")

def process_mp4(path: str):
    audio = MP4(path)
    covers = audio.tags.get('covr') or []
    if not covers:
        return
    modified = False
    new_covers = []
    for cover in covers:
        img = Image.open(BytesIO(cover))
        sq = crop_to_square(img)
        if sq.size != img.size:
            buf = BytesIO()
            # Determine format based on existing cover type
            fmt = 'JPEG' if isinstance(cover, MP4Cover) and cover.imageformat == MP4Cover.FORMAT_JPEG else 'PNG'
            sq.save(buf, format=fmt)
            new_covers.append(MP4Cover(buf.getvalue(), imageformat=cover.imageformat))
            modified = True
        else:
            new_covers.append(cover)
    if modified:
        audio.tags['covr'] = new_covers
        audio.save()
        print(f"Cropped album art in MP4/M4A: {path}")

def main(root: str):
    for dirpath, _, files in os.walk(root):
        for fname in files:
            ext = fname.lower().rsplit('.', 1)[-1]
            full = os.path.join(dirpath, fname)
            if ext == 'mp3':
                process_mp3(full)
            elif ext == 'flac':
                process_flac(full)
            elif ext in ('m4a', 'mp4'):
                process_mp4(full)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python crop_album_art.py <directory>")
        sys.exit(1)
    main(sys.argv[1])
