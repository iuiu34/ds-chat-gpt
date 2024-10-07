set -e
base_image=$1
repo=$2

echo $base_image
git add .
git commit -m 'docker build' || true
git push
branch=$(git branch --show-current)
echo branch $branch
sleep 1

gcloud compute instances start docker --zone europe-west1-b

command="cd ~/$repo &&
git fetch &&
git checkout $branch &&
git pull &&
docker build -f container/Dockerfile --tag $base_image . &&
docker push $base_image"
echo $command


gcloud compute ssh "docker" --zone=europe-west1-b --command="${command}"

sleep 1

# gcloud compute ssh "docker" --zone=europe-west1-b --command="echo ola"

#gcloud compute ssh "docker" --zone=europe-west1-b --command="docker system prune -a --volumes --force"

