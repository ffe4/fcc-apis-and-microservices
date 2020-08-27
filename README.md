This repository contains implementations of the [freeCodeCamp APIs and Microservices Projects](https://www.freecodecamp.org/learn/apis-and-microservices/).
The projects are meant to be deployed on Kubernetes. To deploy all projects, simply clone the repository and apply all manifest files in the `kubernetes` folder.

```console
git clone https://github.com/ffe4/fcc-apis-and-microservices.git
kubectl apply -f fcc-apis-and-microservices/kubernetes
```

All services are implemented in Python on top of Flask. 
Databases for the url shortener and the exercise tracker are Redis and PostgreSQL respectively. 
Docker images are automatically pushed to the Docker Hub whenever a new version is pushed to master.