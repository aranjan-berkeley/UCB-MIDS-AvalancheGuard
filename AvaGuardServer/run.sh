#!/bin/bash

################################################
# datasci255:lab3 run.sh script
# Author: Amiya Ranjan (aranjan@berkeley.edu)
################################################
API_IMAGE_NAME=aranjanlab4:latest
REDIS_APP_NAME=w255:redis
REDIS_URL = "redis://service-redis.aranjan:6379"
#################################################

if [[ ${MINIKUBE_TUNNEL_PID:-"unset"} != "unset" ]]; then
    echo "Potentially existing Minikube Tunnel at PID: ${MINIKUBE_TUNNEL_PID}"
    kill ${MINIKUBE_TUNNEL_PID}
fi
#################################################
echo "******* Training Model *************"
FILE=model_pipeline.pkl
if [ -f ./${FILE} ]; then
    echo "${FILE} exist. No need to build"
else
    echo "${FILE} does not exist."
    poetry run python ./trainer/train.py
fi

#################################################
# Start Minikube
echo "******* STARTING MINIKUBE *************"
minikube delete
minikube start --kubernetes-version=v1.25.4
minikube addons enable metrics-server
kubectl delete all --all -n aranjan


# Setup docker -daemon to build with minikube
# rebuild and run the new image within the minikube context
eval $(minikube docker-env)

###################################################
# Build Docker image for the API
# rebuild and run the new image
# rebuild and run the new image within the minikube context
echo "******* Building Docker Images *************"
docker build -t lab3:latest -f ./Dockerfile_api .
docker build -t redis:lab3 -f ./DockerfileRedis .
###################################################
# Build and Deploy Cluster
echo "******* Using Kustomize to apply K8 yaml manifest *************"
# apply yamls for building environment
kubectl apply -k  ./infra/overlays/dev
###################################################
echo "********* waiting for 30 seconds *********"
for i in {1..100}; do for X in '-' '/' '|' '\'; do echo -en "\b$X"; sleep 0.1; done; done

echo "******* port forwarding *************"
kubectl port-forward -n aranjan svc/lab3 8000:8000 &
kubectl port-forward -n aranjan svc/redis 6379:6379 &
##################################################
# wait for the /health endpoint to return a 200 and then move on
echo "******* Health Check *************"
finished=false
while ! $finished; do
    health_status=$(curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/health")
    if [ $health_status == "200" ]; then
        finished=true
        echo "API is ready"
    else
        echo "API not responding yet"
        sleep 1
    fi
done

###################################################
# some tests
echo "******* Some Tests *************"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?name=aranjan"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/hello?nam=aranjan"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/"
curl -o /dev/null -s -w "%{http_code}\n" -X GET "http://localhost:8000/docs"

echo "**** my test****"
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"houses": [{ "MedInc": 8.3252, "HouseAge": 42, "AveRooms": 6.98, "AveBedrms": 1.02, "Population": 322, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23 }]}'

echo "**** my test 2****"
curl -X POST "http://localhost:8000/predict" -H 'Content-Type: application/json' -d '{
  "houses": [
    {
      "MedInc": 0,
      "HouseAge": 0,
      "AveRooms": 0,
      "AveBedrms": 0,
      "Population": 0,
      "AveOccup": 0,
      "Latitude": 0,
      "Longitude": 0
    }
  ]
}'

# output and tail the logs for the api deployment
#kubectl logs -n ${NAMESPACE} -l app=${APP_NAME}


