import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore  # ✅ Correct updated import
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

load_dotenv()

QDRANT_COLLECTION_NAME = "docs_index"

def get_qdrant_client():
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),#, "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY")#, None)
    )

def get_vector_store(collection_name=QDRANT_COLLECTION_NAME):
    client = get_qdrant_client()
    embeddings = OpenAIEmbeddings()
    
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )

def create_qdrant_collection(collection_name=QDRANT_COLLECTION_NAME, vector_size=1536):
    client = get_qdrant_client()

    if collection_name not in [col.name for col in client.get_collections().collections]:
        print(f"🆕 Creating new Qdrant collection `{collection_name}`...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
    else:
        print(f"ℹ️ Qdrant collection `{collection_name}` already exists.")
