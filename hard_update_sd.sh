
#cp picard "/media/crclayton/Seagate Portable Drive/Music/picard-$(date '+%y-%m-%d')" -r

# save the playlists
cp /media/crclayton/7C3F-6B90/USERPL* .
python3 save_playlists.py

rm /media/crclayton/7C3F-6B90/* -rf

# update to SD card
#rm /media/crclayton/7C3F-6B90/* -rf
rsync -av picard/* /media/crclayton/7C3F-6B90/ --delete


#udisks --unmount  /media/crclayton/7C3F-6B90
#udisks --detatch  /media/crclayton/7C3F-6B90
