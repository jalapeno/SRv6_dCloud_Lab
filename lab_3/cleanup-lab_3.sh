#/bin/sh

docker-compose -f docker-compose.yml down

docker volume rm xrd01
docker volume rm xrd02
docker volume rm xrd03
docker volume rm xrd04
docker volume rm xrd05
docker volume rm xrd06
docker volume rm xrd07
