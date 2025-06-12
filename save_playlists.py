import re
import os
import shutil
import difflib

def normalize(name):
    """
    Lowercase, strip extension, and remove anything but letters+digits
    so “04-Afterthought.mp3” → “afterthought”.
    """
    base = os.path.splitext(name)[0].lower()
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
    Try to match ‘query’ (raw extracted) to a file in the library:
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
    """
    (As before) read raw bytes, decode ISO-8859-1, strip nonprintable,
    then find things ending in ‘.mp3’ via regex.
    """
    with open(filepath, 'rb') as f:
        data = f.read().decode('ISO-8859-1', errors='ignore')
    # keep only ASCII-printable
    clean = ''.join(c for c in data if c.isprintable() and ord(c) < 128)
    # ensure we separate filenames
    clean = re.sub(r'\.(?i:mp3)', '.mp3 ', clean)
    pattern = re.compile(r'\d[\w\-\_]+\.mp3', re.IGNORECASE)
    return sorted({m.group(0) for m in pattern.finditer(clean)})

def copy_with_fuzzy(src_root, dest_dir, raw_names, lib_dir):
    """
    Build the library index once, then for each raw_name:
      – find_best_match → actual_path
      – copy actual_path → dest_dir
      – log misses
    """
    norm_map, all_norms = build_library_index(lib_dir)
    os.makedirs(dest_dir, exist_ok=True)

    for raw in raw_names:
        match = find_best_match(norm_map, all_norms, raw)
        if match:
            dst = os.path.join(dest_dir, os.path.basename(match))
            if not os.path.exists(dst):
                shutil.copy(match, dst)
                print(f"✓ {raw} → {match}")
            else:
                pass
                print(f"⚠ {raw} - {match}: already exists, skipped")
        else:
            print(f"✗ {raw}: NO MATCH")
            with open("misses.txt","rb") as f:
                f.writeline(raw)

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

    for pl_file, out_dir in playlists.items():
        print(f"\n=== Processing {os.path.basename(pl_file)} → {out_dir} ===")
        names = extract_mp3_filenames_iso88591(pl_file)
        copy_with_fuzzy(LIBRARY_DIR, out_dir, names, LIBRARY_DIR)

