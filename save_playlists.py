import re


from pathlib import Path

import os


def find_file(root_dir, fname):
    matches = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            #print(filename)
            if filename == fname:
                full_path = os.path.join(dirpath, filename)
                matches.append(full_path)

    if len(matches) == 1:
        #print("Match:", matches[0])
        return matches[0]
    elif len(matches) == 0:
        #print("No matching files found.")
        pass
    else:
        #print("Multiple matching files found:")
        for match in matches:
            #print("Match 1:", match)
            return match

    return None



def find_file_ending_with(root_dir, suffix):
    matches = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            #print(filename)
            if filename.endswith(suffix):
                full_path = os.path.join(dirpath, filename)
                matches.append(full_path)

    if len(matches) == 1:
        #print("Match:", matches[0])
        return matches[0]
    elif len(matches) == 0:
        #print("No matching files found.")
        pass
    else:
        #print("Multiple matching files found:")
        for match in matches:
            #print("Match 1:", match)
            return match

    return None

def find_file_starting_with(root_dir, prefix):
    matches = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            #print(filename)
            if filename.startswith(prefix):
                full_path = os.path.join(dirpath, filename)
                matches.append(full_path)

    if len(matches) == 1:
        #print("Match:", matches[0])
        return matches[0]
    elif len(matches) == 0:
        #print("No matching files found.")
        pass
    else:
        #print("Multiple matching files found:")
        for match in matches:
            #print("Match 1:", match)
            return match

    return None


def extract_mp3_filenames_iso88591(filepath):
    """
    Extracts MP3 filenames from an ISO-8859-1 encoded file.

    Args:
        filepath: The path to the ISO-8859-1 encoded file.

    Returns:
        A list of MP3 filenames, or an empty list if none are found.
    """
    try:
        with open(filepath, 'rb') as f: #, encoding='ISO-8859-1') as f:
            text_data = f.read()



            clean_text = str(text_data.decode("ISO-8859-1"))
            #print("RAW TEXT:",clean_text)

            #print(clean_text)



            clean_text = ''.join([c for c in clean_text if c.isprintable()])  # Remove non-printable chars
            clean_text = ''.join([c for c in clean_text if ord(c) < 128])

            clean_text = clean_text.replace(".mp3",".mp3 ")
            clean_text = clean_text.replace(".MP3",".MP3 ")
            clean_text = clean_text.replace("mp3","mp3 ")
            clean_text = clean_text.replace("MP3","MP3 ")
            clean_text = clean_text.replace("mp3MP3","mp3 ")
            clean_text = clean_text.replace("mpMP3","mp3 ")
            #print("CLEANED TEXT:",clean_text)

            #pattern = r'\d[A-Za-z0-9\-\_\.al]+\.mp3(?=\s|$|(?=\d[A-Za-z0-9\-\_\.]+\.mp3))'
            #pattern = r'\d[A-Za-z0-9\-\_\.]+\.mp3(?!\S)'
            #pattern = r'\d[A-Za-z0-9\-\_\.]+\.mp3(?=\s|$)'
            #pattern = r'\d[A-Za-z0-9\-\_\.]+\.mp3(?=\b)'
            pattern = r'\d[A-Za-z0-9\-\_\.]+\.mp3'
            #pattern = r'\d[A-Za-z0-9\-\_\.]+\.mp3(?!\w)'
            #pattern = r'\b\d[A-Za-z0-9\-\_\.]+\.mp3' # begins with a number and is an mp3 file

            # Regular expression to find MP3 filenames (basic pattern for filenames)
            mp3_pattern = re.compile(pattern, re.IGNORECASE)

            # Find all matches
            matches = list(sorted([m.strip() for m in mp3_pattern.findall(clean_text)]))



            pattern = r'\d[A-Za-z0-9\-\_\.]+mp3'
            #pattern = r'\d[A-Za-z0-9\-\_\.]+\.mp3(?!\w)'
            #pattern = r'\b\d[A-Za-z0-9\-\_\.]+\.mp3' # begins with a number and is an mp3 file

            # Regular expression to find MP3 filenames (basic pattern for filenames)
            mp3_pattern = re.compile(pattern, re.IGNORECASE)

            # Find all matches
            possible_misses_suffix = [m.strip() for m in mp3_pattern.findall(clean_text)]
            possible_misses_suffix = list(sorted(set(possible_misses_suffix) - set(matches)))

            for m in matches:
                if find_file("/home/crclayton/Music/picard", m) is None:
                    possible_misses_suffix.append(m)

            print("SONGS:", matches, len(matches))

            for f in ["1.UMP3", "2.UMP3", "3.UMP3"]:
                if f in possible_misses_suffix: possible_misses_suffix.remove(f)

            print("POSSIBLE MISSES:", possible_misses_suffix)

            for file in possible_misses_suffix:
                match = find_file_starting_with("/home/crclayton/Music/picard", file.replace("MP3",""))
                if match is None:
                    print("-> Couldn't find starting with, trying ending with:", file, "->", file[1:])
                    match = find_file_ending_with("/home/crclayton/Music/picard", file[1:])
                    if match is None:
                        print(" -> Couldn't find starting with, trying ending with:", file, "->", file[2:])
                        match = find_file_ending_with("/home/crclayton/Music/picard", file[2:])
                        if match is None:
                            print("  -> Couldn't find starting with, trying ending with:", file, "->", file[3:])
                            match = find_file_ending_with("/home/crclayton/Music/picard", file[3:])
                            if match is None:
                                print("STILL MISSING:", file) 
                                f = open("misses.txt", "a")
                                f.write(str(file) + "\n")
                                f.close()
                                continue

                match = os.path.basename(match)
                print("Resolved miss:", file.replace("MP3",""), "->", match)
                matches.append(match)


            #possible_misses_prefix




        matches = [m for m in matches if not m is None]
        return matches

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    #except Exception as e:
    #    print(f"An unexpected error occurred: {e}")
    #    return []

import os
import shutil

def copy_files_by_name(src_dir, dest_dir, filenames):
    """Recursively search for files by name and copy them to a given directory."""

    # Ensure destination directory exists, create if not
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    found = []

    # Loop through the directory and subdirectories
    for root, _, files in os.walk(src_dir):
        for file in files:
            # If the file is in the list of filenames, copy it
            if file in filenames:
                src_file_path = os.path.join(root, file)
                dest_file_path = os.path.join(dest_dir, file)

                # If a file with the same name already exists in the destination, we can skip or overwrite
                if os.path.exists(dest_file_path):
                    print(f"File {file} already exists in destination, skipping.")
                    pass
                else:
                    shutil.copy(src_file_path, dest_file_path)
                    print(f"Copied {file} to {dest_dir}")

                found.append(file)
            #else:
            #    print("Not found: ", file)



    print("File search and copy completed.")

files = {
        "/media/crclayton/MP3/USERPL1.PL":  "/home/crclayton/Music/picard/Playlists/soft",
        "/media/crclayton/MP3/USERPL2.PL":  "/home/crclayton/Music/picard/Playlists/medium",
        "/media/crclayton/MP3/USERPL3.PL":  "/home/crclayton/Music/picard/Playlists/hard",
    }

for playlist_file, playlist_dir in files.items():
    mp3_list = extract_mp3_filenames_iso88591(playlist_file)
    print("MP3 list", mp3_list)
    copy_files_by_name("picard", playlist_dir, mp3_list)
    print("")

