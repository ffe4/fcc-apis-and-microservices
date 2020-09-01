This repository contains implementations of the [freeCodeCamp APIs and Microservices Projects](https://www.freecodecamp.org/learn/apis-and-microservices/).
They can be deployed on Kubernetes using the manifest files in the `kubernetes` folder.

On Minikube, enable the ingress controller first.
```console
minikube addons enable ingress
```

Then clone the repository and apply the manifests.
```console
git clone https://github.com/ffe4/fcc-apis-and-microservices.git
kubectl apply -f fcc-apis-and-microservices/kubernetes
```

All services are implemented in Python on top of Flask. 
Docker images are automatically pushed to the Docker Hub whenever a new version is pushed to master.
Databases for the url shortener and the exercise tracker are Redis and PostgreSQL respectively. 
