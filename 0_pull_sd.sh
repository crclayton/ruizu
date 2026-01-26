
#cp library "/media/crclayton/Seagate Portable Drive/Music/library-$(date '+%y-%m-%d')" -r

# save the playlists
#
echo "--- Copying Saved MP3 Playlist Files to Folders ---"

cp /media/crclayton/MP3/USERPL1.PL .
cp /media/crclayton/MP3/USERPL2.PL .
cp /media/crclayton/MP3/USERPL3.PL .
python3 save_playlists.py

