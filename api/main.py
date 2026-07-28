import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

from config.settings import settings
from pipeline.prompts.system_prompts import STUDENT_RAG_PROMPT, CITIZEN_AGENT_PROMPT

app = FastAPI(title=settings.app_name, version=settings.version)

# Initialize ChromaDB Client
chroma_client = chromadb.PersistentClient(path=settings.vectordb_dir)
try:
    collection = chroma_client.get_collection(name="legal_docs")
except Exception:
    collection = None

# Load Embedder & Groq
embedder = SentenceTransformer(settings.embedding_model)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None


class QueryRequest(BaseModel):
    query: str
    mode: str = "citizen"  # Options: "student" or "citizen"


@app.get("/")
def root():
    return {"status": "ok", "message": "Pakistan Legal Compliance API is active."}


@app.post("/query")
def query_legal_agent(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    if not groq_client:
        raise HTTPException(
            status_code=500, 
            detail="GROQ_API_KEY is not configured in your .env file."
        )

    if collection is None:
        raise HTTPException(
            status_code=500,
            detail="ChromaDB collection 'legal_docs' not found. Ensure you ran `python pipeline/ingestion/ingest.py` first."
        )

    # 1. Retrieve top-k context chunks from ChromaDB
    query_vector = embedder.encode([request.query]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=settings.top_k
    )

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not docs:
        context_text = "No legal context found."
    else:
        context_parts = []
        for doc, meta in zip(docs, metadatas):
            source = meta.get("source", "Unknown")
            page = meta.get("page_number", "?")
            context_parts.append(f"[Source: {source}, Page: {page}]\n{doc}")
        context_text = "\n\n---\n\n".join(context_parts)

    # 2. Select System Prompt based on Mode
    if request.mode == "student":
        system_instructions = STUDENT_RAG_PROMPT.format(context=context_text)
        temp = 0.1  # Highly deterministic for strict legal facts
    else:
        system_instructions = CITIZEN_AGENT_PROMPT.format(context=context_text)
        temp = 0.3  # Slight reasoning leeway for legal strategy synthesis

    # 3. Call LLM
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": request.query}
            ],
            model=settings.llm_model,
            temperature=temp
        )
        answer = chat_completion.choices[0].message.content
        return {"answer": answer, "sources": metadatas, "mode": request.mode}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API Error: {str(e)}")