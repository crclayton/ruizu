source /home/crclayton/myenv/bin/activate
rm cover.jpg
rm out.mp4
python3 make_video.py
#/home/crclayton/myenv/bin/python /usr/bin/python3 make_video.py
detox . -r -v

f="$(ls -Art | tail -n 1)"
bash time.sh $f

f="$(ls -Art | tail -n 1)"
bash pad.sh $f

detox . -r -v
rm cover.jpg
