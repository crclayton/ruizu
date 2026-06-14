import re
import os
import shutil
import difflib

def normalize(name):
    base = re.sub(r'\.mp3$', '', name, flags=re.IGNORECASE).lower()
    return re.sub(r'[^0-9a-z]', '', base)

def build_library_index(root_dir):
    """
    Walk the library and return:
      - norm_map: { normalized_basename: full_path OR [full_path,…] }
      - all_norms: list of all normalized basenames
    """
    norm_map = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.lower().endswith('.mp3'):
                path = os.path.join(dirpath, fn)
                norm = normalize(fn)
                if norm in norm_map:
                    # turn into list on first duplicate
                    if isinstance(norm_map[norm], list):
                        norm_map[norm].append(path)
                    else:
                        norm_map[norm] = [norm_map[norm], path]
                else:
                    norm_map[norm] = path
    return norm_map, list(norm_map.keys())

def find_best_match(norm_map, all_norms, query):
    """
    Try to match 'query' (raw extracted) to a file in the library:
      1) exact normalized match
      2) substring match
      3) difflib.get_close_matches
    Returns the chosen full path or None.
    """
    nq = normalize(query)
    # 1) exact
    if nq in norm_map:
        val = norm_map[nq]
        return val[0] if isinstance(val, list) else val

    # 2) substring
    subs = [n for n in all_norms if nq in n]
    if len(subs) == 1:
        val = norm_map[subs[0]]
        return val[0] if isinstance(val, list) else val


    # 3) fuzzy
    close = difflib.get_close_matches(nq, all_norms, n=1, cutoff=0.6)
    if close:
        val = norm_map[close[0]]
        return val[0] if isinstance(val, list) else val

    # no luck
    return None

def extract_mp3_filenames_iso88591(filepath):
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
    except FileNotFoundError:
        return []

    # Try UTF-16-LE - some proprietary device formats embed a BOM mid-file
    # after an ASCII header, so BOM position cannot be used for detection.
    text = raw.decode('utf-16-le', errors='ignore')

    # Each entry is also individually prefixed with its own BOM (U+FEFF)
    # followed by the track name and terminated by a null byte - the most
    # reliable extraction when present, including names with no digits/ext.
    bom_pattern = re.compile(r'﻿([^\x00]+)')
    bom_matches = {m.group(1) for m in bom_pattern.finditer(text)}
    if bom_matches:
        return sorted(bom_matches)

    utf16_pattern = re.compile(r'(?<![^\W_])\d{8}[\w\-]+', re.IGNORECASE)
    utf16_matches = {m.group(0) for m in utf16_pattern.finditer(text)}

    # Secondary pattern for truncated entries (no .mp3 suffix): matches ASCII
    # track filenames like "12_All_Around_the_World_Re" that the binary-digit
    # heuristic above misses when preceding bytes don't decode to digit chars.
    track_pattern = re.compile(r'(?<![A-Za-z0-9])\d{2,}[._-][A-Za-z_][\w_\-]{4,}')
    track_matches = {m.group(0) for m in track_pattern.finditer(text)}

    all_matches = sorted(utf16_matches | track_matches)
    if all_matches:
        return all_matches

    data = raw.decode('ISO-8859-1', errors='ignore')
    clean = ''.join(c for c in data if c.isprintable() and ord(c) < 128)
    clean = re.sub(r'\.(?i:m)', '.', clean)
    pattern = re.compile(r'\d[\w\-\_]+\.', re.IGNORECASE)
    return sorted({m.group(0) for m in pattern.finditer(clean)})

def copy_with_fuzzy(src_root, dest_dir, raw_names, lib_dir, dest_resolver=None):
    """
    Build the library index once, then for each raw_name:
      – find_best_match → actual_path
      – pick destination via dest_resolver(actual_path) if given, else (dest_dir, False)
        dest_resolver returns (target_dir, move) where move=True deletes the original
      – copy/move actual_path → destination
      – log misses
    """
    norm_map, all_norms = build_library_index(lib_dir)
    os.makedirs(dest_dir, exist_ok=True)

    for raw in raw_names:
        match = find_best_match(norm_map, all_norms, raw)
        if match:
            target_dir, move = dest_resolver(match) if dest_resolver else (dest_dir, False)
            os.makedirs(target_dir, exist_ok=True)
            dst = os.path.join(target_dir, os.path.basename(match))
            if not os.path.exists(dst):
                if move:
                    shutil.move(match, dst)
                    print(f"✓ {raw} → {match} (moved)")
                else:
                    shutil.copy(match, dst)
                    print(f"✓ {raw} → {match}")
            else:
                pass
                print(f"⚠ {raw} - {match}: already exists, skipped")
        else:
            print(f"✗ {raw}: NO MATCH")
            with open("misses.txt","w") as f:
                f.writelines(raw)

if __name__ == "__main__":
    # map each playlist to a difficulty folder
    playlists = {
        "/home/crclayton/Music/USERPL1.PL":
            "/home/crclayton/Music/library/playlists/soft",
        "/home/crclayton/Music/USERPL2.PL":
            "/home/crclayton/Music/library/playlists/medium",
        "/home/crclayton/Music/USERPL3.PL":
            "/home/crclayton/Music/library/playlists/hard",
    }
    LIBRARY_DIR = "/home/crclayton/Music/library"
    SOFT_DIR = os.path.join(LIBRARY_DIR, "playlists/soft")
    MEDIUM_DIR = os.path.join(LIBRARY_DIR, "playlists/medium")
    HARD_DIR = os.path.join(LIBRARY_DIR, "playlists/hard")
    RECYCLING_BIN_DIR = os.path.join(LIBRARY_DIR, "playlists/recycling_bin")

    for pl_file, out_dir in playlists.items():
        print(f"\n=== Processing {os.path.basename(pl_file)} → {out_dir} ===")
        names = extract_mp3_filenames_iso88591(pl_file)
        if out_dir == HARD_DIR:
            # tracks currently in soft/medium get demoted to hard (-> cringe backup,
            # since they were liked at some point); everything else is moved to the
            # recycling bin and removed from its current spot entirely
            def hard_resolver(match, out_dir=out_dir):
                if os.path.dirname(match) in (SOFT_DIR, MEDIUM_DIR):
                    return out_dir, False
                return RECYCLING_BIN_DIR, True
            copy_with_fuzzy(LIBRARY_DIR, out_dir, names, LIBRARY_DIR, dest_resolver=hard_resolver)
        else:
            copy_with_fuzzy(LIBRARY_DIR, out_dir, names, LIBRARY_DIR)

    # USERPL3 (hard) = tracks to remove from soft and medium
    hard_dir = "/home/crclayton/Music/library/playlists/hard"
    remove_from = [
        "/home/crclayton/Music/library/playlists/soft",
        "/home/crclayton/Music/library/playlists/medium",
        "/home/crclayton/Music/library/liked",
    ]
    print("\n=== Removing hard tracks from soft/medium ===")
    hard_files = {f for f in os.listdir(hard_dir) if f.lower().endswith('.mp3')}
    hard_norms = {normalize(f) for f in hard_files}
    for folder in remove_from:
        for fname in os.listdir(folder):
            if not fname.lower().endswith('.mp3'):
                continue
            if fname in hard_files or normalize(fname) in hard_norms:
                target = os.path.join(folder, fname)
                os.remove(target)
                print(f"✗ removed from {os.path.basename(folder)}: {fname}")

