set -e
IMAGE=$(docker ps -q --filter ancestor="constellation" )
if [ "$IMAGE" ]
then
	echo "FOUND"
	docker stop $IMAGE
	docker rm $IMAGE
fi

[ -d "telemetry_src" ] && rm -rf "telemetry_src"
OLD_PATH=`pwd`
cd ../../../../.
cp -r telemetry telemetry_src
mv telemetry_src telemetry/web/dashboard/dasher/
cd $OLD_PATH

docker build -t constellation .
docker run -d --restart unless-stopped -p 5000:5000 constellation
