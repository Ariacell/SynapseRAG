
# First time startup

## Starting the services

Running 
```sh
docker compose up
```
will expose 
- a qdrant database, used for text embedding storage, and

### Services

#### Ollama running mistral7b

An ollama instance running mistral7b, which can be prompted via something like
```sh
curl -X POST localhost:11434/api/generate -d "{\"model\":\"mistral\", \"prompt\":\"Are you working?\", \"stream\": false}"
```

#### Qdrant DB for vector embeddings

#### OpenWebUI

For nicer adhoc prompting UI for the Ollama models

#### SearXNG

#### ComfyUI

For image generation.
This example workflow is using this model: https://comfyui-wiki.com/en/tutorial/advanced/flux1-comfyui-guide-workflow-and-examples#comfy-org-fp8-checkpoint-version


## Generating embeddings and prompting

This project uses uv as the python environment manager.

Embeddings can be generated from the dummy "test_vault" directory by running
```sh
uv run src/generate_embeddings.py
```
Queries can be run either as standalone prompts or as chat with history via 
```sh
uv run src/query_with_context.py
# or
uv run src/chat_with_context.py
```
respectively.

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