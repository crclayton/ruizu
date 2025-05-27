
#cp picard "/media/crclayton/Seagate Portable Drive/Music/picard-$(date '+%y-%m-%d')" -r

# save the playlists
#
echo "--- Copying Saved MP3 Playlist Files to Folders ---"

cp /media/crclayton/MP3/USERPL* .
python3 save_playlists.py

echo "--- Creating Liked Folder from Playlists ---"

cp ~/Music/picard/Playlists/hard/*   ~/Music/picard/Playlists/liked
cp ~/Music/picard/Playlists/medium/* ~/Music/picard/Playlists/liked
cp ~/Music/picard/Playlists/soft/*   ~/Music/picard/Playlists/liked

# update to SD card
#rm /media/crclayton/7C3F-6B90/* -rf

#fatsort -cn /media/crclayton/MP3

echo "--- Uploading picard files to SD ---"

bash sync_music.sh

echo "--- Deleting SD files not in picard ---"

rsync -hvrltD --modify-window=2 --size-only --delete ~/Music/picard/ /media/crclayton/MP3
cp USERPL* /media/crclayton/MP3

#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
