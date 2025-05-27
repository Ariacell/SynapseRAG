import os
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance, CollectionStatus

# Configuration
DIRECTORY_PATH = "./test_vault"
COLLECTION_NAME = "markdown_embeddings"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Load an embedding model compatible with Mistral 7B (sentence-transformers version of Instructor, etc.)
# Mistral doesn't natively do embeddings, but use a compatible dense embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Create collection if it doesn't exist
if COLLECTION_NAME not in [col.name for col in client.get_collections().collections]:
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

# Function to load all Markdown files
def load_markdown_files(directory_path):
    md_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                md_files.append((full_path, content))
    return md_files

# Load markdown files
markdown_files = load_markdown_files(DIRECTORY_PATH)

# Generate and upload embeddings
points = []
for file_path, content in markdown_files:
    embedding = model.encode(content)
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding.tolist(),
        payload={"path": file_path, "content": content[:500]}  # Optional: truncate content for metadata
    )
    points.append(point)

# Upload in batches
client.upsert(collection_name=COLLECTION_NAME, points=points)

print(f"Uploaded {len(points)} documents to Qdrant collection '{COLLECTION_NAME}'.")
