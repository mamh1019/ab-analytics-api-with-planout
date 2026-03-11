docker buildx build --load -f Dockerfile.dev --platform=linux/amd64 -t ab-analytics-api.local .
docker rm -f ab-analytics-api.local
docker run --name ab-analytics-api.container -p 8001:8001 -v $(pwd)/app:/code/app ab-analytics-api.local
docker image prune -af --filter "until=24h"