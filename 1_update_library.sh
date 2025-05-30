
#turn these on next time
#find /home/crclayton/Music/spotdl -mindepth 1 -maxdepth 1 -type d
#find /home/crclayton/Music/bandcamp -mindepth 1 -maxdepth 1 -type d
#find /home/crclayton/Music/ytmdl -mindepth 1 -maxdepth 1 -type d

# copy new downloads
#find /home/crclayton/Music/spotdl -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/library/Recently_Added \;
#find /home/crclayton/Music/bandcamp -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/library/Recently_Added \;
#find /home/crclayton/Music/ytmdl -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/library/Recently_Added \;

echo ""
echo "--- Starting update ---"
echo ""

echo ""
echo "--- Clearing auto folders ---"
echo ""

rm ~/Music/library/Recently_Added/* -rf
rm ~/Music/library/Random_Albums/* -rf
rm ~/Music/library/Random_Songs/* -rf

echo ""
echo "--- Contents ---"
echo ""

ls ~/Music/library/Recently_Added/
ls ~/Music/library/Random_Albums/
ls ~/Music/library/Random_Songs/

echo ""
echo "--- Recently created albums: ---"
echo ""

python3 move_recently_added.py --count 20

#find library/ -type d -name "[0-9][0-9][0-9][0-9]-*" -ctime -5

#echo "--- Copying into folder ---"

#find library/ -type d -name "[0-9][0-9][0-9][0-9]-*" -ctime -5 -exec cp -r {} ~/Music/library/Recently_Added \;

#echo "--- 2025 albums: ---"

#find library/ -type d -name "2025-*"

#echo "--- Copying into folder ---"

#find library/ -type d -name "2025-*" -exec cp -r {} ~/Music/library/Recently_Added \;

echo ""
echo "--- Creating random playlists ---"
echo ""

# create new shuffle playlist
bash update_random.sh

python3 move_random.py --count 20

# encode correct
detox library/ -r -v

echo ""
echo "--- Track count: $(find library/ -type f -name "*.mp3"  | wc -l) ---"
echo ""


#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
