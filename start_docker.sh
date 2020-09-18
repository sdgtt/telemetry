IMAGE=$(docker ps -q --filter ancestor="docker-dash" )
if [ "$IMAGE" ]
then
	echo "FOUND"
	docker stop $IMAGE
	docker rm $IMAGE
fi

docker build -t docker-dash .
docker run -d -p 8050:8050 docker-dash
