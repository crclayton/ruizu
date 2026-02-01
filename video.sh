source /home/crclayton/myenv/bin/activate
rm cover.jpg
rm out.mp4
python3 make_video.py $1
detox . -r -v

f="$(ls -Art | tail -n 1)"
bash wrap_it_up.sh $f

rm cover.jpg
