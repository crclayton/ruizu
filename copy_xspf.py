import os
import argparse
import shutil
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_xspf(xspf_path):
    """
    Parse an XSPF playlist and yield local file paths.
    """
    tree = ET.parse(xspf_path)
    root = tree.getroot()
    ns = {'xspf': 'http://xspf.org/ns/0/'}
    tracklist = root.find('xspf:trackList', ns)
    if tracklist is None:
        raise ValueError("No <trackList> found in the XSPF file.")
    for track in tracklist.findall('xspf:track', ns):
        loc = track.find('xspf:location', ns)
        if loc is None or loc.text is None:
            print("Not found")
            continue
        uri = loc.text.strip()
        yield uri
        # Only handle file:// URIs
        #parsed = urllib.parse.urlparse(uri)
        #print(uri)
        #print(parsed.scheme)
        #if parsed.scheme != 'file':
        #    print(f"Skipping non-file URI: {uri}")
        #    continue
        #path = urllib.parse.unquote(parsed.path)
        #yield path

def copy_files(file_paths, dest_dir):
    """
    Copy each file in file_paths into dest_dir.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    for src in file_paths:
        src_path = Path(src)
        if src_path.exists():
            target = dest / src_path.name
            shutil.copy2(src_path, target)
            print(f"Copied: {src_path} -> {target}")
        else:
            print(f"File not found, skipping: {src_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Copy files listed in an XSPF playlist to a specified folder."
    )
    parser.add_argument("playlist", help="Path to the .xspf playlist file")
    parser.add_argument("dest", help="Destination folder to copy files into")
    args = parser.parse_args()

    try:
        file_list = list(parse_xspf(args.playlist))
        copy_files(file_list, args.dest)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
