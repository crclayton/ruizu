
#turn these on next time
#find /home/crclayton/Music/spotdl -mindepth 1 -maxdepth 1 -type d
#find /home/crclayton/Music/bandcamp -mindepth 1 -maxdepth 1 -type d
#find /home/crclayton/Music/ytmdl -mindepth 1 -maxdepth 1 -type d

# copy new downloads
#find /home/crclayton/Music/spotdl -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/library/recently_added \;
#find /home/crclayton/Music/bandcamp -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/library/recently_added \;
#find /home/crclayton/Music/ytmdl -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/library/recently_added \;



echo ""
echo "--- Copying strawberry playlists to folders ---"
echo ""

# copy files in the xspf into the folder
python3 copy_xspf.py soft.xspf   library/playlists/soft/
python3 copy_xspf.py medium.xspf library/playlists/medium/
python3 copy_xspf.py hard.xspf   library/playlists/hard/
python3 copy_xspf.py liked.xspf  library/liked/
python3 copy_xspf.py mixternmixtus.xspf   library/playlists/mixter_n_mixtus/
python3 copy_xspf.py hits.xspf            library/playlists/hits

rm ~/Music/library/new_liked/* -rf
rm ~/Music/library/new_soft/* -rf
rm ~/Music/library/new_medium/* -rf
find ~/Music/library/playlists/soft/ ~/Music/library/playlists/medium/ -maxdepth 1 -type f -name "*.mp3" -printf "%f\t%p\n" | sort -r | head -n 100 | cut -f2 | xargs -I {} cp "{}" ~/Music/library/new_liked/
find ~/Music/library/playlists/soft/ -maxdepth 1 -type f -name "*.mp3" -printf "%f\t%p\n" | sort -r | head -n 50 | cut -f2 | xargs -I {} cp "{}" ~/Music/library/new_soft/
find ~/Music/library/playlists/medium/ -maxdepth 1 -type f -name "*.mp3" -printf "%f\t%p\n" | sort -r | head -n 50 | cut -f2 | xargs -I {} cp "{}" ~/Music/library/new_medium/
cd ~/Music

mv soft.xspf   soft.backup
mv medium.xspf medium.backup
mv hard.xspf   hard.backup
mv liked.xspf  liked.backup
mv mixternmixtus.xspf  mixternmixtus.backup
mv hits.xspf hits.backup

# creating a new xspf from what's in the folder
python3 sync_xspf.py library/playlists/soft/   -o soft.xspf
python3 sync_xspf.py library/playlists/medium/ -o medium.xspf
python3 sync_xspf.py library/playlists/hard/   -o hard.xspf
python3 sync_xspf.py library/playlists/mixter_n_mixtus/   -o mixternmixtus.xspf
python3 sync_xspf.py library/playlists/hits/   -o hits.xspf
python3 sync_xspf.py library/liked/            -o liked.xspf


echo ""
echo "--- Starting update ---"
echo ""

echo ""
echo "--- Clearing auto folders ---"
echo ""

rm ~/Music/library/recently_added/* -rf
rm ~/Music/library/random_albums/* -rf
rm ~/Music/library/random_songs/* -rf
rm ~/Music/library/random_new/* -rf

echo ""
echo "--- Contents ---"
echo ""

ls ~/Music/library/recently_added/
ls ~/Music/library/random_albums/
ls ~/Music/library/random_songs/
ls ~/Music/library/random_new/

echo ""
echo "--- recently created albums: ---"
echo ""

python3 move_recently_added.py --count 15

#find library/ -type d -name "[0-9][0-9][0-9][0-9]-*" -ctime -5

#echo "--- Copying into folder ---"

#find library/ -type d -name "[0-9][0-9][0-9][0-9]-*" -ctime -5 -exec cp -r {} ~/Music/library/recently_added \;

echo "--- 2025 albums: ---"

#find library/ -type d -name "2025-*"

echo "--- Copying into folder ---"

#find library/ -type d -name "2025-*" -exec cp -r {} ~/Music/library/recently_added \;







echo ""
echo "--- Creating random playlists ---"
echo ""

# create new shuffle playlist

# random albums
python3 move_random.py --count 5

# random songs
bash update_random.sh

echo ""
echo "--- Running detox ---"
echo ""

# encode correct
detox ~/Music/library/ -r -v

# remove track numbers from playlists
bash ~/Music/clean_names.sh ~/Music/library/playlists/soft ~/Music/library/playlists/medium ~/Music/library/playlists/hard ~/Music/library/liked ~/Music/library/new_liked ~/Music/library/playlists/hits


echo ""
echo "--- Track count: $(find ~/Music/library/ -type f -name "*.mp3"  | wc -l) ---"
echo ""


#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
