# echo "Removing duplicates (I do this here for some reason)"
# cd ~/Music/library/genres
# bash ~/Music/no_dupes.sh
# cd ~/Music

rm ~/Music/USERPL*.PL
#cp library "/media/crclayton/Seagate Portable Drive/Music/library-$(date '+%y-%m-%d')" -r

# save the playlists
#
echo "--- Copying Saved MP3 Playlist Files to Folders ---"

cp /media/crclayton/MP3/USERPL1.PL .
cp /media/crclayton/MP3/USERPL2.PL .
cp /media/crclayton/MP3/USERPL3.PL .

cat USERPL*PL

python3 save_playlists.py

