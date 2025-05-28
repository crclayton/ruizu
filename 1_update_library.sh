
#turn these on next time
#find /home/crclayton/Music/spotdl -mindepth 1 -maxdepth 1 -type d
#find /home/crclayton/Music/bandcamp -mindepth 1 -maxdepth 1 -type d
#find /home/crclayton/Music/ytmdl -mindepth 1 -maxdepth 1 -type d

# copy new downloads
#find /home/crclayton/Music/spotdl -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/picard/Recently_Added \;
#find /home/crclayton/Music/bandcamp -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/picard/Recently_Added \;
#find /home/crclayton/Music/ytmdl -mindepth 1 -maxdepth 1 -type d -exec mv  {} ~/Music/picard/Recently_Added \;

echo ""
echo "--- Starting update ---"
echo ""

echo ""
echo "--- Clearing auto folders ---"
echo ""

rm ~/Music/picard/Recently_Added/* -rf
rm ~/Music/picard/Random_Albums/* -rf
rm ~/Music/picard/Random_Songs/* -rf

echo ""
echo "--- Contents ---"
echo ""

ls ~/Music/picard/Recently_Added/
ls ~/Music/picard/Random_Albums/
ls ~/Music/picard/Random_Songs/

echo ""
echo "--- Recently created albums: ---"
echo ""

python3 move_recently_added.py --count 20

#find picard/ -type d -name "[0-9][0-9][0-9][0-9]-*" -ctime -5

#echo "--- Copying into folder ---"

#find picard/ -type d -name "[0-9][0-9][0-9][0-9]-*" -ctime -5 -exec cp -r {} ~/Music/picard/Recently_Added \;

#echo "--- 2025 albums: ---"

#find picard/ -type d -name "2025-*"

#echo "--- Copying into folder ---"

#find picard/ -type d -name "2025-*" -exec cp -r {} ~/Music/picard/Recently_Added \;

echo ""
echo "--- Creating random playlists ---"
echo ""

# create new shuffle playlist
bash update_random.sh

python3 move_random.py --count 20

# encode correct
detox picard/ -r -v

echo ""
echo "--- Track count: $(find picard/ -type f -name "*.mp3"  | wc -l) ---"
echo ""


#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
