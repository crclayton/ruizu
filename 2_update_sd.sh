
#cp library "/media/crclayton/Seagate Portable Drive/Music/library-$(date '+%y-%m-%d')" -r

# save the playlists
#
echo "--- Copying Saved MP3 Playlist Files to Folders ---"

cp /media/crclayton/MP3/USERPL1.PL .
cp /media/crclayton/MP3/USERPL2.PL .
cp /media/crclayton/MP3/USERPL3.PL .
python3 save_playlists.py

echo "--- Creating Liked Folder from playlists ---"

cp ~/Music/library/playlists/hard/*   ~/Music/library/playlists/liked
cp ~/Music/library/playlists/medium/* ~/Music/library/playlists/liked
cp ~/Music/library/playlists/soft/*   ~/Music/library/playlists/liked

# update to SD card
#rm /media/crclayton/7C3F-6B90/* -rf

#fatsort -cn /media/crclayton/MP3

echo "--- Uploading library files to SD ---"

bash sync_music.sh

echo "--- Deleting SD files not in library ---"

rsync -hvrltD --modify-window=2 --size-only --delete ~/Music/library/ /media/crclayton/MP3
#cp USERPL* /media/crclayton/MP3

#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
