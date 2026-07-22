import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import chromadb
from config.settings import settings

chroma_client = chromadb.PersistentClient(path=settings.vectordb_dir)
collection = chroma_client.get_collection(name="legal_docs")

# Search ChromaDB documents using keyword matching
results = collection.get(
    where_document={"$contains": "465"}
)

print(f"\n🔍 Found {len(results['documents'])} chunks containing '465':\n")

for doc, meta in zip(results["documents"][:3], results["metadatas"][:3]):
    print(f"📄 Source: {meta.get('source')} (Page {meta.get('page_number')})")
    print(f"Snippet: {doc[:200]}...\n" + "-"*40)