import os
from pathlib import Path
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from config.settings import settings

def run_ingestion():
    # Base directory for books
    books_dir = Path(settings.base_dir) / "data" / "books"
    chroma_db_dir = settings.vectordb_dir

    print(f"🔍 Scanning books directory: {books_dir}")
    raw_documents = []

    # Iterate through each sector subfolder
    for sector_folder in books_dir.iterdir():
        if sector_folder.is_dir():
            sector_name = sector_folder.name  # e.g., "ARMED FORCES ACT"
            pdf_files = list(sector_folder.glob("*.pdf"))
            
            print(f"📁 Sector: [{sector_name}] - Found {len(pdf_files)} PDFs")
            
            for pdf_path in pdf_files:
                try:
                    reader = PdfReader(str(pdf_path))
                    for page_num, page in enumerate(reader.pages, 1):
                        text = page.extract_text()
                        if text and text.strip():
                            # Attach metadata (Source file + Sector name + Page number)
                            doc = Document(
                                page_content=text,
                                metadata={
                                    "source": pdf_path.name,
                                    "sector": sector_name,
                                    "page": page_num
                                }
                            )
                            raw_documents.append(doc)
                except Exception as e:
                    print(f"⚠️ Error processing {pdf_path.name}: {e}")

    print(f"\n📄 Total raw pages extracted: {len(raw_documents)}")

    # Chunk the documents while retaining metadata
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    chunked_docs = text_splitter.split_documents(raw_documents)
    print(f"✂️ Total chunks created: {len(chunked_docs)}")

    # Initialize Embedding Model
    print(f"⚙️ Loading embedding model ({settings.embedding_model})...")
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

    # Rebuild Chroma Vector Store
    print("💾 Storing vector embeddings into ChromaDB...")
    vector_db = Chroma.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        persist_directory=str(chroma_db_dir)
    )
    
    print("\n✅ Multi-sector indexing complete! Vector database is ready.")

if __name__ == "__main__":
    run_ingestion()