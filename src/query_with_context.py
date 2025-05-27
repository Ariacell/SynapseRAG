from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, SearchRequest
import textwrap
import requests

# Settings
COLLECTION_NAME = "markdown_embeddings"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
TOP_K = 5
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "mistral"

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def retrieve_context(query: str, top_k: int = TOP_K):
    """Retrieve top-K context chunks from Qdrant"""
    query_vector = model.encode(query).tolist()
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return [hit.payload["content"] for hit in hits]

def build_prompt(query: str, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = textwrap.dedent(f"""
    You are an AI assistant. Use the following context to answer the question.

    Context:
    {context}

    Question: {query}
    Answer:
    """)
    return prompt


def ask_ollama(prompt: str):
    """Send the prompt to Mistral running on Ollama"""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["response"]

if __name__ == "__main__":
    query = input("Enter your question: ")
    context = retrieve_context(query)
    prompt = build_prompt(query, context)

    print("\n🧾 Prompt to Mistral:\n")
    print(prompt)

    answer = ask_ollama(prompt)
    print("\n🧠 Mistral's Response:\n")
    print(answer)
    # You'd pass `prompt` to a Mistral model endpoint (e.g., via Hugging Face or local deployment)
