

## Starting the model and database

Running 
```sh
docker compose up
```
will expose 
- a qdrant database, used for text embedding storage, and
- an ollama instance running mistral7b, which can be prompted via something like
```sh
curl -X POST localhost:11434/api/generate -d "{\"model\":\"mistral\", \"prompt\":\"Are you working?\", \"stream\": false}"
```


## Getting a kubernetes distribution of Ollama

> Note this currently seems to not work due to Docker K8s limitations for giving gpu access to WSL2 when using K8S

https://github.com/otwld/ollama-helm

```
helm repo add ollama-helm https://otwld.github.io/ollama-helm/
helm repo update
helm install ollama ollama-helm/ollama --namespace ollama --create-namespace
```

1. Get the application URL by running these commands:
```
  export POD_NAME=$(kubectl get pods --namespace ollama -l "app.kubernetes.io/name=ollama,app.kubernetes.io/instance=ollama" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace ollama $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace ollama port-forward $POD_NAME 8080:$CONTAINER_PORT
  ```