import os
import hashlib
from langchain_community.document_loaders import DirectoryLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from qdrant_utils import get_vector_store, create_qdrant_collection

def hash_text(text: str) -> str:
    """Generate a unique hash for a given text block."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def embed_and_store_documents(folder_path="POC_UsingQdrant_Chatbot/data/my_docs", collection_name="docs_index"):
    # Create or connect to Qdrant collection
    create_qdrant_collection(collection_name)
    vectorstore = get_vector_store(collection_name)

    # Load all .docx documents recursively from folder

    loader = DirectoryLoader(
        folder_path,
        glob="**/*.docx",
        loader_cls=UnstructuredWordDocumentLoader
    )
    docs = loader.load()

    # Split into manageable chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    new_docs = []
    existing_hashes = set()

    # Try to retrieve existing content hashes from Qdrant
    try:
        existing_docs = vectorstore.similarity_search("placeholder", k=10000)
        for d in existing_docs:
            hash_val = d.metadata.get("content_hash")
            if hash_val:
                existing_hashes.add(hash_val)
    except Exception as e:
        print("⚠️  Warning: Could not prefetch existing documents from Qdrant:", e)

    # Deduplicate based on content hash
    for chunk in chunks:
        content_hash = hash_text(chunk.page_content)
        if content_hash in existing_hashes:
            continue  # Already indexed
        chunk.metadata["content_hash"] = content_hash
        new_docs.append(Document(page_content=chunk.page_content, metadata=chunk.metadata))

    # Store only new documents
    if new_docs:
        vectorstore.add_documents(new_docs)
        print(f"✅ Embedded and stored {len(new_docs)} new chunks to `{collection_name}`.")
    else:
        print("ℹ️  No new documents to embed. All content already exists in the vector store.")
