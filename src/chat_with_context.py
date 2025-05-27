import requests
import textwrap

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchRequest

# Constants
COLLECTION_NAME = "markdown_embeddings"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
TOP_K = 5
MAX_TURNS = 10  # Limit history length
MAX_CONTEXT_CHARS = 2000  # Optional: prevent overly long prompts

# Initialize embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Simple memory for conversation (in-memory, append-only)
chat_history = []

def retrieve_context(query: str, top_k: int = TOP_K):
    """Retrieve top-K context chunks from Qdrant"""
    query_vector = model.encode(query).tolist()
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return [hit.payload["content"] for hit in hits]

def build_conversational_prompt(context_chunks, chat_history, user_query):
    """Builds the full prompt with chat history and current question"""
    context = "\n\n".join(context_chunks)[:MAX_CONTEXT_CHARS]
    
    history_text = ""
    for i, (user_q, ai_resp) in enumerate(chat_history[-MAX_TURNS:]):
        history_text += f"User: {user_q}\nAssistant: {ai_resp}\n"

    prompt = textwrap.dedent(f"""
    You are a helpful AI assistant. You will be provided with context and a conversation history.
    Answer the user's new question using both.

    Context:
    {context}

    Conversation history:
    {history_text}

    User: {user_query}
    Assistant:
    """)
    return prompt

def ask_ollama(prompt: str):
    """Send prompt to Ollama's Mistral model"""
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })
    response.raise_for_status()
    return response.json()["response"]

def chat_loop():
    print("🧠 Mistral Chat (Ctrl+C to exit)")
    try:
        while True:
            user_query = input("\nYou: ")
            context = retrieve_context(user_query)
            prompt = build_conversational_prompt(context, chat_history, user_query)
            answer = ask_ollama(prompt)
            
            chat_history.append((user_query, answer))
            print(f"\nMistral: {answer}")
    except KeyboardInterrupt:
        print("\n👋 Conversation ended.")

if __name__ == "__main__":
    chat_loop()
