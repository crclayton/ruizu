#!/usr/bin/env python3
import os
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

# Supported audio file extensions
AUDIO_EXTENSIONS = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac'}

def indent(elem, level=0):
    """Pretty-print indentation for XML elements."""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def generate_xspf(dir_path, output_path):
    """
    Scan directory for audio files and generate an XSPF playlist.
    Running this repeatedly keeps the .xspf in sync with the directory contents.
    """
    root = ET.Element('playlist', version='1', xmlns='http://xspf.org/ns/0/')
    title = ET.SubElement(root, 'title')
    title.text = Path(dir_path).name
    tracklist = ET.SubElement(root, 'trackList')

    for fname in sorted(os.listdir(dir_path)):
        if os.path.splitext(fname)[1].lower() in AUDIO_EXTENSIONS:
            track = ET.SubElement(tracklist, 'track')
            # file:// URI
            loc = ET.SubElement(track, 'location')
            uri = Path(dir_path).joinpath(fname).absolute().as_uri()
            loc.text = uri
            # track title from filename
            title_el = ET.SubElement(track, 'title')
            title_el.text = Path(fname).stem

    indent(root)
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Generated playlist: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate or sync an XSPF playlist from a directory.")
    parser.add_argument('directory', help="Directory containing audio files")
    parser.add_argument('-o','--output', help="Output XSPF file (default: <directory>/playlist.xspf)")
    args = parser.parse_args()

    dir_path = args.directory
    if not os.path.isdir(dir_path):
        print(f"Error: {dir_path} is not a directory")
        return

    output = args.output or os.path.join(dir_path, 'playlist.xspf')
    generate_xspf(dir_path, output)

if __name__ == '__main__':
    main()
