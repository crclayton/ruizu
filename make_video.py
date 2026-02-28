#!/usr/bin/env python3
import subprocess
import urllib.parse
import sys
import json
import webbrowser

import os
import subprocess
import urllib.parse
import sys

import os
import subprocess
import urllib.parse
import sys
import re

import os
import re
import subprocess
import sys
import urllib.parse
from mutagen import File as MutagenFile

def ffprobe_float(args):
    out = subprocess.check_output(args, stderr=subprocess.DEVNULL).decode().strip()
    try:
        return float(out)
    except Exception:
        return None

def probe_duration_seconds(path):
    # format duration is usually most reliable across containers/codecs
    return ffprobe_float([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=nokey=1:noprint_wrappers=1',
        path
    ]) or 0.0

def probe_video_dims(path):
    out = subprocess.check_output([
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=p=0',
        path
    ], stderr=subprocess.DEVNULL).decode().strip()
    w, h = out.split(',')
    return int(w), int(h)

def estimate_char_width_for_video(video_w, font_size, margin_px=80):
    # Monospace glyph is roughly ~0.60 * fontsize wide for DejaVuSansMono
    approx_glyph_w = max(1.0, font_size * 0.60)
    usable = max(200, video_w - margin_px)  # keep sane minimum
    return max(20, int(usable / approx_glyph_w))


def get_current_mp3_blah():
    # 1) Get Strawberry window title
    try:
        # find the first Strawberry window
        win = subprocess.check_output(
            ['xdotool','search','--class','strawberry'],
            stderr=subprocess.DEVNULL,
            text=True
        ).splitlines()[0]
        title = subprocess.check_output(
            ['xdotool','getwindowname', win],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        sys.exit("Error: couldn’t read Strawberry’s window title. Install xdotool and run under X11.")

    # 2) Parse "Artist - Title"
    m = re.match(r'(.+?)\s*[–-]\s*(.+)$', title)
    if not m:
        sys.exit(f"Error: couldn’t parse song from window title “{title}”.")

    artist, track = m.group(1).strip(), m.group(2).strip()

    # 3) Scan your library for a matching file
    root = os.path.expanduser('~/Music/library/genres')
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.lower().endswith('.mp3'):
                continue
            path = os.path.join(dirpath, fn)
            try:
                audio = MutagenFile(path)
                tags = getattr(audio, 'tags', {}) or {}
                # ID3 TPE1 = artist, TIT2 = title
                a = tags.get('TPE1')
                t = tags.get('TIT2')
                ta = a.text[0] if a and hasattr(a, 'text') else None
                tt = t.text[0] if t and hasattr(t, 'text') else None
                if ta == artist and tt == track:
                    return path
            except Exception:
                pass

    sys.exit(f"Error: couldn’t locate “{artist} – {track}” in your library under {root}.")


def get_current_mp3Sbla():
    # 1) Try playerctl
    try:
        url = subprocess.check_output(
            ['playerctl', 'metadata', 'xesam:url'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if url:
            return urllib.parse.unquote(url[len('file://'):]) if url.startswith('file://') else url
    except subprocess.CalledProcessError:
        pass

    # 2) Try gdbus directly
    try:
        out = subprocess.check_output([
            'gdbus', 'call', '--session',
            '--dest', 'org.mpris.MediaPlayer2.strawberry',
            '--object-path', '/org/mpris/MediaPlayer2',
            '--method', 'org.freedesktop.DBus.Properties.Get',
            'org.mpris.MediaPlayer2.Player', 'Metadata'
        ], stderr=subprocess.DEVNULL).decode()
        # look for: 'xesam:url': <('s', 'file:///…')>
        m = re.search(r"'xesam:url': <\('s', '([^']+)'\)>", out)
        if m:
            url = m.group(1)
            return urllib.parse.unquote(url[len('file://'):]) if url.startswith('file://') else url
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # 3) Fallback: scan /proc/<pid>/fd
    pid = None
    for args in (('pgrep','-x','strawberry'), ('pgrep','-f','strawberry')):
        try:
            pid = subprocess.check_output(args).decode().splitlines()[0]
            break
        except subprocess.CalledProcessError:
            continue
    if pid:
        fd_dir = f'/proc/{pid}/fd'
        if os.path.isdir(fd_dir):
            for fd in os.listdir(fd_dir):
                link = os.path.join(fd_dir, fd)
                try:
                    target = os.readlink(link)
                except OSError:
                    continue
                if target.lower().endswith('.mp3'):
                    return target

    sys.exit("Error: couldn’t locate the MP3 via any method.")


def get_current_mp3_old():
    # 1) Try playerctl first
    try:
        url = subprocess.check_output(
            ['playerctl', 'metadata', 'xesam:url'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if url.startswith('file://'):
            return urllib.parse.unquote(url[len('file://'):])
        return url
    except subprocess.CalledProcessError:
        pass

    # 2) Find Strawberry’s PID
    pid = None
    for args in (['pgrep','-x','strawberry'], ['pgrep','-f','strawberry']):
        try:
            pid = subprocess.check_output(args).decode().splitlines()[0]
            break
        except subprocess.CalledProcessError:
            continue
    if not pid:
        sys.exit("Error: cannot find Strawberry process.")

    # 3) Inspect /proc/<pid>/fd for .mp3
    fd_dir = f'/proc/{pid}/fd'
    if os.path.isdir(fd_dir):
        for fd in os.listdir(fd_dir):
            link = os.path.join(fd_dir, fd)
            try:
                target = os.readlink(link)
            except OSError:
                continue
            if target.lower().endswith('.mp3'):
                return target

    sys.exit("Error: couldn’t locate the .mp3 via /proc fallback.")


#def get_current_mp3():
#    # 1) Try playerctl
#    try:
#        url = subprocess.check_output(
#            ['playerctl', 'metadata', 'xesam:url'],
#            stderr=subprocess.DEVNULL
#        ).decode().strip()
#        if url.startswith('file://'):
#            return urllib.parse.unquote(url[len('file://'):])
#        return url
#    except subprocess.CalledProcessError:
#        pass
#
#    # 2) Fallback: find Strawberry PID then first open .mp3
#    try:
#        # exact match, or fallback to any strawberry process
#        pid = subprocess.check_output(
#            ['pgrep', '-x', 'strawberry']
#        ).decode().splitlines()[0]
#    except subprocess.CalledProcessError:
#        try:
#            pid = subprocess.check_output(
#                ['pgrep', '-f', 'strawberry']
#            ).decode().splitlines()[0]
#        except subprocess.CalledProcessError:
#            sys.exit("Error: cannot find Strawberry process via pgrep.")
#
#    try:
#        out = subprocess.check_output(
#            ['lsof', '-n', '-p', pid]
#        ).decode().splitlines()
#        for line in out:
#            parts = line.split()
#            path = parts[-1]
#            if path.lower().endswith('.mp3'):
#                return path
#    except subprocess.CalledProcessError:
#        pass
#
#    sys.exit("Error: couldn’t locate the .mp3 via fallback.")

def get_current_mp3():
    try:
        cmd = ['playerctl', '-p', 'strawberry', 'metadata', 'xesam:url']
        print(" ".join(cmd))
        url = subprocess.check_output(cmd).decode().strip()
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

from mutagen.id3 import USLT

import pyperclip

def get_lyrics(mp3_path=None):
    try:
        text = pyperclip.paste()
        return text.strip() if text else None
    except Exception as e:
        print(f"Error reading from clipboard: {e}")
        return None


#def get_lyrics(mp3_path):
#    try:
#        audio = MutagenFile(mp3_path)
#        print(audio)
#        if not audio or not hasattr(audio, 'tags'):
#            print("here")
#            return None
#        for tag in audio.tags.values():
#            if isinstance(tag, USLT):
#                print(tag.text)
#                return tag.text
#    except Exception:
#        pass
#    return None


#def make_video(mp3_path, filename):
#    subprocess.run([
#        'ffmpeg', '-y',
#        '-loop', '1', '-i', 'cover.jpg',
#        '-i', mp3_path,
#        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
#        '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '192k',
#        '-pix_fmt', 'yuv420p', '-shortest',
#        filename + '.mp4'
#    ], check=True)


import textwrap


import textwrap
import shlex

import textwrap

import re

def escape_ffmpeg_text(text):
    print("before", text)
    text = text.replace('\\', '\\\\')  # must come first
    text = text.replace("'", "")
    text = text.replace("  ", " ")
    #text = text.replace('\n', r'\n')
    text = re.sub(r'([:=%!?#])', r'\\\1', text)  # escape : = % ! ? #
    print("after", text)
    return text

def normalize_cover(input_jpg='cover.jpg', output_jpg='cover_960.jpg'):
    subprocess.run([
        'ffmpeg', '-y',
        '-i', input_jpg,
        '-vf',
        'scale=iw*min(960/iw\\,960/ih):ih*min(960/iw\\,960/ih):flags=lanczos,'
        'pad=960:960:(960-iw*min(960/iw\\,960/ih))/2:(960-ih*min(960/iw\\,960/ih))/2:black',
        output_jpg
    ], check=True)


def normalize_cover_old(input_jpg='cover.jpg', output_jpg='cover_960.jpg'):
    subprocess.run([
        'ffmpeg', '-y',
        '-i', input_jpg,
        '-vf',
        'scale=960:-1:flags=lanczos,pad=960:960:(ow-iw)/2:(oh-ih)/2:black',
        output_jpg
    ], check=True)



def make_video(mp3_path, filename, bg_video=None):
    lyrics = get_lyrics()

    print(filename)

    # Add 400px black padding below image

    character_width = 62 #int(72*960/1080)
    #font_size = 24#max(18, int(48 - len(lines)))
    row_height = 33.3 # 33.2 # was 33.1 #int(32.75*960/1080)

    font_size = 25 #int(24*960/1080)

    padding_below_album_art = 10


    print("RAW: " + lyrics)
    if lyrics:
        print("Doing lyrics")
        # Clean and wrap lyrics
        lyrics = escape_ffmpeg_text(lyrics.strip())
        lyrics = lyrics.replace("%","\\%")
        lyrics = lyrics.replace("{","[")
        lyrics = lyrics.replace("}","]")

        lyrics = re.sub(r"[\(\[].*?[\)\]]", "", lyrics)
        lyrics = re.sub(r"[\(\[].*?[\)\]]", "", lyrics)

        #lyrics = lyrics.replace("'","")
        #lyrics = lyrics.replace(",","")
        #lyrics = lyrics.replace("?","")
        lyrics = lyrics.replace("F*ck","fuck")
        lyrics = lyrics.replace("F**k","fuck")
        lyrics = lyrics.replace("F***","fuck")

        lyrics = lyrics.replace("f*ck","fuck")
        lyrics = lyrics.replace("f**k","fuck")
        lyrics = lyrics.replace("f***","fuck")
        lyrics = lyrics.replace(" , ",", ")
        lyrics = lyrics.replace(" . ",". ")
        lyrics = lyrics.replace("\"","")
        lyrics = lyrics.replace("\"","")
        lyrics = lyrics.replace("[","")
        lyrics = lyrics.replace("]","")
        lyrics = lyrics.replace("  "," ")
        lyrics = lyrics.replace("  "," ")
        #lyrics = re.sub("[\(\[].*?[\)\]]", "", lyrics) # remove [verse] (x2) (Ooh!) etc.
        lyrics = lyrics.strip()
        lyrics = '"' + lyrics + '"'
        lyrics = lyrics.replace(". \"",".")

        wrapped = textwrap.wrap(lyrics.strip(), width=character_width)
        lines = wrapped#[:12]
        final_text = "\n".join(lines)

        num_lines = len(lines) + 1
        height = num_lines*row_height + padding_below_album_art



        # FFmpeg escaping: backslashes, single quotes, newlines
        safe_text = escape_ffmpeg_text(final_text.replace("  "," "))

        title = "\n".join(l.center(character_width, u'\xa0') for l in textwrap.wrap(escape_ffmpeg_text(filename)))

        if "\n" in title:
            height += row_height

        safe_text = title + "\n" + safe_text
        safe_text = safe_text.replace("%","\\\\%")

        vf_filters = []
        #vf_filters.append("pad=iw:ih+" + str(height) + ":0:0:black")
        vf_filters.append(f"pad=iw:ih+{height}:0:0:black")

        print("CLEANED:\n", safe_text)
        print("Character count: ", len(safe_text))


        #count: 714, font size: 24

        drawtext = (
            "drawtext="
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:"
            f"text='{safe_text}':"
            "fontcolor=#FFB343:fontsize={}:".format(font_size) +
            "borderw=1.5:bordercolor=black:"
            "line_spacing=4:"
            "x=(w-text_w)/2:y=h-" + str(int(height)-padding_below_album_art)
        )

        vf_filters.append(drawtext)

        vf_filters.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")


    vf_arg = ",".join(vf_filters)

    print(filename)

    filename = filename.replace("/","")

    print(filename)
    # -stream loop -1

    if bg_video:
        #cmd = [
        #    'ffmpeg', '-y',
        #   '-i', bg_video,
        #   #'-i', mp3_path,
        #    '-vf', vf_arg,
        #    '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '0',
        #    '-pix_fmt', 'yuvj420p', '-shortest',
        #    filename + '.mp4'
        #]

        mid_fade_to_img_seconds = 20
        mid_hold_img_seconds    = 10
        mid_fade_back_seconds   = 20



        xfade_fps = 25

        hold_seconds = 5
        fade_in_seconds  = 20
        fade_out_seconds = 20   # video -> image
        end_hold_seconds = 5    # image only at the very end

        # choose a common fps for the crossfade (match your typical output; 30 is fine too)
        xfade_fps = 25

        v_dur = probe_duration_seconds(bg_video)  # use your existing ffprobe helper
        fade_out_offset = max(0.0, v_dur - (fade_out_seconds + end_hold_seconds))

        mid_block = mid_fade_to_img_seconds + mid_hold_img_seconds + mid_fade_back_seconds
        mid_to_img_offset = max(0.0, (fade_out_offset / 2.0) - (mid_block / 2.0))
        mid_back_offset   = mid_to_img_offset + mid_fade_to_img_seconds + mid_hold_img_seconds


        filter_complex = (
            # --- COVER IMAGE path (input 0) ---
            # Normalize: fps/size/SAR/timebase/pixfmt so xfade can work reliably.
            f"[0:v]"
            f"fps={xfade_fps},"
            f"scale=960:960:force_original_aspect_ratio=decrease,"
            f"pad=960:960:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,"
            f"settb=1/1000,"
            f"format=rgba,"
            f"split=2[img1][img2];"  # we need the image twice: once to fade IN, once to fade OUT

            # --- BG VIDEO path (input 1) ---
            # 1) Drop the first `hold_seconds` of VIDEO so when the fade starts,
            #    the video matches the audio timeline (we were hiding those seconds anyway).
            # 2) Reset timestamps.
            # 3) Normalize to match the image (fps/size/SAR/timebase/pixfmt).
            # 4) Pad the end by `hold_seconds` so the output video isn’t shorter than the audio.
            f"[1:v]"
            f"trim=start={hold_seconds},"
            f"setpts=PTS-STARTPTS,"
            f"fps={xfade_fps},"
            f"scale=960:960:force_original_aspect_ratio=decrease,"
            f"pad=960:960:(ow-iw)/2:(oh-ih)/2,"
            f"setsar=1,"
            f"settb=1/1000,"
            f"format=rgba,"
            f"tpad=stop_mode=clone:stop_duration={hold_seconds}"
            f"[vid];"

            # --- FADE IN (image -> video) ---
            # Hold image for `hold_seconds`, then crossfade to the video over `fade_in_seconds`.
            f"[img1][vid]"
            f"xfade=transition=fade:"
            f"duration={fade_in_seconds}:"
            f"offset={hold_seconds}"
            f"[mix1];"

            # --- FADE OUT (video -> image) ---
            # Start the fade-out at: video_duration - (fade_out_seconds + end_hold_seconds)
            # So the final `end_hold_seconds` are fully the image.
            f"[mix1][img2]"
            f"xfade=transition=fade:"
            f"duration={fade_out_seconds}:"
            f"offset={fade_out_offset},"
            f"format=yuv420p"
            f"{',' + vf_arg if vf_arg else ''}"
            f"[v]"
        )



        #filter_complex = (
        #    # --- COVER IMAGE path (input 0) ---
        #    f"[0:v]"
        #    f"fps={xfade_fps},"
        #    f"scale=960:960:force_original_aspect_ratio=decrease,"
        #    f"pad=960:960:(ow-iw)/2:(oh-ih)/2,"
        #    f"setsar=1,"
        #    f"settb=1/1000,"
        #    f"format=rgba,"
        #    f"split=3[img_start][img_end][img_mid];"

        #    # --- BG VIDEO path (input 1) ---
        #    f"[1:v]"
        #    f"trim=start={hold_seconds},"
        #    f"setpts=PTS-STARTPTS,"
        #    f"fps={xfade_fps},"
        #    f"scale=960:960:force_original_aspect_ratio=decrease,"
        #    f"pad=960:960:(ow-iw)/2:(oh-ih)/2,"
        #    f"setsar=1,"
        #    f"settb=1/1000,"
        #    f"format=rgba,"
        #    f"tpad=stop_mode=clone:stop_duration={hold_seconds},"
        #    f"split=2[vid_a][vid_b];"

        #    # 1) --- FADE IN (image -> video) ---
        #    f"[img_start][vid_a]"
        #    f"xfade=transition=fade:"
        #    f"duration={fade_in_seconds}:"
        #    f"offset={hold_seconds}"
        #    f"[mix1];"

        #    # 2) --- MID FADE (video -> image) ---
        #    f"[mix1][img_mid]"
        #    f"xfade=transition=fade:"
        #    f"duration={mid_fade_to_img_seconds}:"
        #    f"offset={mid_to_img_offset}"
        #    f"[mix2];"

        #    # 3) --- MID FADE BACK (image -> video) ---
        #    f"[mix2][vid_b]"
        #    f"xfade=transition=fade:"
        #    f"duration={mid_fade_back_seconds}:"
        #    f"offset={mid_back_offset}"
        #    f"[mix3];"

        #    # 4) --- FADE OUT (video -> image) ---
        #    f"[mix3][img_end]"
        #    f"xfade=transition=fade:"
        #    f"duration={fade_out_seconds}:"
        #    f"offset={fade_out_offset},"
        #    f"format=yuv420p"
        #    f"{',' + vf_arg if vf_arg else ''}"
        #    f"[v]"
        #)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", "cover_960.jpg",
            "-i", bg_video,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "1:a:0",          # audio from bg_video
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "0",
            "-pix_fmt", "yuv420p",
            "-shortest",
            filename + ".mp4",
        ]



    else:

        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', 'cover_960.jpg',
            '-i', mp3_path,
            '-vf', vf_arg,
            '-c:v', 'libx264', '-c:a', 'aac', '-b:a', '0',
            '-pix_fmt', 'yuvj420p', '-shortest',
            filename + '.mp4'
        ]

    print("COMMAND: " + " ".join(cmd))

    subprocess.run(cmd, check=True)


def main():
    mp3 = get_current_mp3()
    print(f"Using track: {mp3}", file=sys.stderr)

    #mp3 = sys.argv[1]

    meta = get_metadata(mp3)
    parts = [meta['genre'], meta['location'], meta['year']]
    bracket = ', '.join([p for p in parts if p])
    info = f"{meta['artist']} - \"{meta['title']}\" [{bracket}]"
    print(info)

    extract_cover(mp3)
    normalize_cover('cover.jpg', 'cover_960.jpg')  # 👈 added step

    bg_video = sys.argv[1] if len(sys.argv) > 1 else None

    suffix = ""
    if bg_video:
        pass
        #suffix = " - viz"

    make_video(mp3, meta['artist'] + " - " + meta['title'].replace("/","") + suffix, bg_video=bg_video) #+ '"' + ", " + str(meta['year']))


    print("⇨ out.mp4 created")
    print(info)
    info = info.replace("&","%26")
    webbrowser.open("https://old.reddit.com/r/punk/submit/?title=" + info)

if __name__ == '__main__':
    main()
