bash time.sh $1
detox . -r -v

bash pad.sh "time_$1"
detox . -r -v
