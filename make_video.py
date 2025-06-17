#!/usr/bin/env python3
import subprocess
import urllib.parse
import sys
import json
import webbrowser

def get_current_mp3():
    try:
        url = subprocess.check_output(
            ['playerctl', '-p', 'strawberry', 'metadata', 'xesam:url'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        sys.exit("Error: couldn’t read Strawberry’s metadata. Is it running?")

    if url.startswith('file://'):
        return urllib.parse.unquote(url[len('file://'):])
    return url

def get_metadata(mp3_path):
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_entries', 'format_tags=artist,title,genre,date,location',
        mp3_path
    ]
    out = subprocess.check_output(cmd).decode()
    data = json.loads(out)
    tags = data.get('format', {}).get('tags', {})
    return {
        'artist': tags.get('artist', 'Unknown Artist'),
        'title': tags.get('title', mp3_path.rsplit('/', 1)[-1]),
        'genre': tags.get('genre', '').strip(),
        'year': tags.get('date', '').strip(),
        'location': tags.get('location', '').strip()
    }

def extract_cover(mp3_path):
    subprocess.run([
        'ffmpeg', '-y', '-i', mp3_path,
        '-an', '-vcodec', 'copy', 'cover.jpg'
    ], stderr=subprocess.DEVNULL)

def make_video(mp3_path, filename):
    subprocess.run([
        'ffmpeg', '-y',
        '-loop', '1', '-i', 'cover.jpg',
        '-i', mp3_path,
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k',
        '-pix_fmt', 'yuv420p', '-shortest',
        filename + '.mp4'
    ], check=True)

def main():
    mp3 = get_current_mp3()
    print(f"Using track: {mp3}", file=sys.stderr)

    meta = get_metadata(mp3)
    parts = [meta['genre'], meta['year'], meta['location']]
    bracket = ', '.join([p for p in parts if p])
    info = f"{meta['artist']} - \"{meta['title']}\" [{bracket}]"
    print(info)

    extract_cover(mp3)
    make_video(mp3, meta['artist'])
    print("⇨ out.mp4 created")
    print(info)
    webbrowser.open("https://old.reddit.com/r/punk/submit/?title=" + info)

if __name__ == '__main__':
    main()
