source /home/crclayton/myenv/bin/activate
rm cover.jpg
rm out.mp4
python3 make_video.py
rm cover.jpg
detox . -r -v
bash pad.sh $(ls -Art | tail -n 1)
detox . -r -v
