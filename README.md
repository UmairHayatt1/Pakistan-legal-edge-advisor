# ⚖️ Pakistani Legal AI Assistant (RAG Engine)

An enterprise-grade Retrieval-Augmented Generation (RAG) system built to query, analyze, and research Pakistani legal statutes, acts, and rules with page-level citation precision and domain-specific metadata filtering.

Powered by **LangChain**, **Groq (Llama 3.1 8B Instant)**, **Chroma DB**, and **Streamlit**.

---

## 🌟 Key Features

* **📄 Page-Level Citation Engine:** Automatically maps retrieved vector chunks back to their original document file names and exact page numbers (`[Doc: Punjab Finance Act 2024.pdf | Page: 12]`).
* **🎯 Dynamic Sector / Folder Filtering:** Automatically scans `data/books/` and builds metadata filters for fast retrieval across 10 specific legal sectors.
* **⚖️ Dual Research Modes:**
  * **Scholar / Strict RAG:** 100% grounded on retrieved context. Strictly answers using provided texts and cites page references. Returns *"Information not available in current sources"* if missing.
  * **General Research Mode:** Uses retrieved context as primary evidence, supplemented with standard legal principles where context is partial.
* **🛡️ Security & Topic Guardrails:** Built-in keyword guardrail that detects and restricts query execution on classified or sensitive security topics.
* **💬 Executive Streamlit UI:** Full chat interface featuring context expanders, full-text context viewing, and session history management.

---

## 📁 Repository Structure

```text
.
├── app.py                   # Streamlit web application interface
├── pipeline/
│   ├── __init__.py
│   └── rag_engine.py        # Core LegalRAGEngine class & LangChain pipelines
├── config/
│   ├── __init__.py
│   └── settings.py          # Environment settings loader
├── data/
│   └── books/               # Dataset directory structured by legal acts/sectors
│       ├── ARMED FORCES ACT/
│       ├── EDUCATION ACT/
│       ├── ELECTRONICS & MEDIA ACT/
│       ├── EXCISE AND TAX ACT/
│       ├── FINANCE ACT/
│       ├── HEALTHCARE ACT/
│       ├── MINORTIES ACT/
│       ├── PAKISTAN ACT/
│       ├── POLICE RULES/
│       └── VEHICLES ACT/
├── chroma_db/               # Persisted Chroma Vector DB
├── .env.example             # Environment variables template
├── requirements.txt         # Dependencies
└── README.md

---

# 📊 Indexed Dataset & Legal Coverage

The system indexes **44 Legal Statutes & Acts** distributed across **10 Legal Categories**.

| Legal Sector / Category | Document Count | Examples |
|---|---:|---|
| ARMED FORCES ACT | 4 | Army Act, Navy Rules, Air Force Statutes |
| EDUCATION ACT | 4 | University Acts, Education Board Regulations |
| ELECTRONICS & MEDIA ACT | 4 | PECA Act, PEMRA Rules |
| EXCISE AND TAX ACT | 4 | Punjab Excise Act, Sales Tax Provisions |
| FINANCE ACT | 4 | Annual Finance Acts, Federal Budget Statutes |
| HEALTHCARE ACT | 6 | Medical Council Ordinance, Healthcare Commission Acts |
| MINORITIES ACT | 3 | Minority Rights & Protection Acts |
| PAKISTAN ACT | 5 | Pakistan Penal Code, Criminal Procedure Code |
| POLICE RULES | 4 | Police Order 2002, Service Regulations |
| VEHICLES ACT | 5 | Motor Vehicles Ordinance, Traffic Laws |
| **TOTAL** | **44 Documents** | Full PDF text extracted page-by-page |

---

# 🏗️ System Architecture

## 1. Offline Data Ingestion Pipeline

```mermaid
graph TD

PDFs["data/books/ PDF Dataset<br/>(44 Files across 10 Sector Folders)"]

PDFLoader["pypdf Loader<br/>(Extracts Text + Page Metadata)"]

Splitter["RecursiveCharacterTextSplitter<br/>(Chunk Size: 800, Overlap: 150)"]

EmbedModel["Embedding Model<br/>(BAAI/bge-small-en-v1.5)"]

ChromaDB[("Chroma DB Vector Store<br/>(./chroma_db)")]

PDFs --> PDFLoader
PDFLoader --> Splitter
Splitter --> EmbedModel
EmbedModel --> ChromaDB

 
