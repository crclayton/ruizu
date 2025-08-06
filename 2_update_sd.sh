
#cp library "/media/crclayton/Seagate Portable Drive/Music/library-$(date '+%y-%m-%d')" -r

# save the playlists
#
#echo "--- Copying Saved MP3 Playlist Files to Folders ---"
#
#cp /media/crclayton/MP3/USERPL1.PL .
#cp /media/crclayton/MP3/USERPL2.PL .
#cp /media/crclayton/MP3/USERPL3.PL .
#python3 save_playlists.py

echo "--- Recreating the playlist files ---"

# creating a new xspf from what's in the folder
python3 sync_xspf.py library/playlists/soft/   -o soft.xspf
python3 sync_xspf.py library/playlists/medium/ -o medium.xspf
python3 sync_xspf.py library/playlists/hard/   -o hard.xspf


echo "--- Creating Liked Folder from playlists ---"

cp -n ~/Music/library/playlists/hard/*   ~/Music/library/playlists/liked
cp -n ~/Music/library/playlists/medium/* ~/Music/library/playlists/liked
cp -n ~/Music/library/playlists/soft/*   ~/Music/library/playlists/liked

cp -n ~/Music/library/playlists/hard/*   ~/Music/library/playlists/medium-hard
cp -n ~/Music/library/playlists/medium/* ~/Music/library/playlists/medium-hard

cp -n ~/Music/library/playlists/medium/* ~/Music/library/playlists/medium-soft
cp -n ~/Music/library/playlists/soft/*   ~/Music/library/playlists/medium-soft

echo "--- Recreating the playlist files ---"

python3 sync_xspf.py library/playlists/liked/  -o liked.xspf

# update to SD card
#rm /media/crclayton/7C3F-6B90/* -rf

#fatsort -cn /media/crclayton/MP3

#echo "--- Adding shuffled playlist files ---"
#
#rm /media/crclayton/MP3/playlists/liked/*
#rm /media/crclayton/MP3/playlists/soft/*
#rm /media/crclayton/MP3/playlists/medium/*
#rm /media/crclayton/MP3/playlists/hard/*
#
#mkdir -p /media/crclayton/MP3/playlists/liked/
#find ~/Music/library/playlists/liked/ -type f | shuf | while read file; do
#  cp "$file" /media/crclayton/MP3/playlists/liked/
#  echo "liked $file"
#done
#
#mkdir -p /media/crclayton/MP3/playlists/soft/
#find ~/Music/library/playlists/soft/ -type f | shuf | while read file; do
#  cp "$file" /media/crclayton/MP3/playlists/soft/
#done
#
#mkdir -p /media/crclayton/MP3/playlists/medium/
#find ~/Music/library/playlists/medium/ -type f | shuf | while read file; do
#  cp "$file" /media/crclayton/MP3/playlists/medium/
#done
#
#mkdir -p /media/crclayton/MP3/playlists/hard/
#find ~/Music/library/playlists/hard/ -type f | shuf | while read file; do
#  cp "$file" /media/crclayton/MP3/playlists/hard/
#done

echo "--- Uploading library files to SD ---"

bash sync_music.sh

echo "--- Deleting SD files not in library ---"

rsync -hvrltD --modify-window=2 --size-only --delete ~/Music/library/ /media/crclayton/MP3

#cp ~/Music/USERPL1.PL /media/crclayton/MP3
#cp ~/Music/USERPL2.PL /media/crclayton/MP3
#cp ~/Music/USERPL3.PL /media/crclayton/MP3

#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
