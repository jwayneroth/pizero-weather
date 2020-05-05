cd "$(dirname "$0")"

echo "$(date): starting..." >> weather.log
 
eips -c
eips -c

rm -f /mnt/us/weather/pz-weather.png
 
#curl -k --fail http://pi.hole/weather/pz-weather.png >> pz-weather.png 
curl -k --fail http://192.168.2.11/weather/pz-weather.png >> pz-weather.png

if [ $? -ne 0 ]; then
	eips -g weather-image-error.png
	echo "$(date): error" >> weather.log
else
	eips -g pz-weather.png
	echo "$(date): wrote output.png" >> weather.log
fi
