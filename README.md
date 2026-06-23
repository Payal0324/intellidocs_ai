# 📚 IntelliDocs AI – Intelligent Multi-PDF Conversational Knowledge Assistant using RAG

---

## 🚀 Project Overview

**IntelliDocs AI** is an AI-powered document intelligence system that allows users to upload multiple PDF files and interact with them through natural language conversations.

Instead of manually searching through long documents, users can ask questions and get **accurate, context-aware answers powered by Retrieval-Augmented Generation (RAG)**.

The system transforms static PDFs into a **smart conversational knowledge assistant** similar to ChatGPT, but grounded only on user-provided documents.

---

## 📁 Project Structure
```bash
IntelliDocs_AI/
│
├── LICENSE
├── README.md
├── requirements.txt
│
├── backend/
│   ├── __init__.py
│   │
│   ├── ai_pipeline/
│   │   ├── embedding_generator.py      # Generates vector embeddings from text chunks
│   │   ├── pdf_processor.py            # Extracts and processes PDF text
│   │   ├── rag_pipeline.py             # Core RAG logic (retrieval + LLM response)
│   │   ├── summarizer.py               # Generates document summaries
│   │   ├── vector_store_manager.py     # FAISS index management (store & search)
│   │
│   ├── api/
│   │   └── __init__.py                 # API layer (future FastAPI extensibility)
│   │
│   ├── config/
│   │   └── __init__.py                 # Configuration settings (API keys, constants)
│   │
│   ├── database/
│   │   ├── manager.py                  # SQLite database operations (chat + metadata)
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py                 # Business logic layer (orchestration)
│   │
│   └── utils/
│       └── __init__.py                 # Utility/helper functions
│
├── frontend/
│   ├── app.py                          # Main Streamlit application (UI entry point)
│   ├── __init__.py
│   │
│   ├── pages/
│   │   └── (multi-page Streamlit UI screens)
│   │
│   └── static/
│       └── (CSS, images, icons for UI styling)
│
├── data/
│   ├── uploaded_pdfs/                  # Stores user-uploaded PDF files
│   └── faiss_index/                    # Persistent FAISS vector index storage
│
├── docs/
│   └── (project documentation, diagrams, reports)
│
└── tests/
    ├── ai_pipeline/
    │   └── test_ai_pipeline.py        # Unit tests for RAG pipeline
    │
    ├── backend/
    │   └── test_backend.py            # Backend service tests
    │
    └── frontend/
        └── test_frontend.py           # UI/Streamlit tests
```

---


## 🧰 Tech Stack

### 🔹 Programming Language
- Python (Core backend + AI pipeline)

### 🔹 Frontend
- Streamlit (Interactive web UI)
- HTML/CSS (Custom UI styling within Streamlit)

### 🔹 AI / Machine Learning
- Sentence Transformers (Text Embeddings)
- Google Gemini API (Large Language Model for response generation)
- LangChain (RAG orchestration support)

### 🔹 Vector Database
- FAISS (Facebook AI Similarity Search) for fast semantic retrieval

### 🔹 PDF Processing
- PyMuPDF / PyPDF2 (Text extraction from PDF documents)

### 🔹 Database
- SQLite (Chat history, document metadata storage)

### 🔹 Backend Architecture
- Modular Python-based backend (AI pipeline + services layer)

### 🔹 Testing
- Pytest (Unit testing for backend, frontend, and AI pipeline modules)

---
## ✨ Key Features

### 📄 Multi-PDF Intelligence
- Upload and process multiple PDF files
- Merge knowledge from different documents
- Handle large document collections efficiently

### 💬 Conversational AI Chat
- Chat-style interface (like ChatGPT)
- Context-aware follow-up questions
- Persistent conversation flow

### 🔍 RAG-Based Question Answering
- Semantic search using embeddings
- Retrieves most relevant document chunks
- Generates accurate answers using LLM (Gemini)

### 📌 Source Citations
- Each answer includes:
  - Source document name
  - Page reference (if available)
  - Relevant extracted text chunks
- Ensures transparency and trust

### 📊 Document Summarization
- Auto-generate document summaries
- Extract key points and concepts
- Quick overview of long PDFs

### 📁 Document Management
- Upload, view, and delete PDFs
- Organize multiple documents easily

---

## 🧠 System Architecture

IntelliDocs AI is built using a modular RAG pipeline:

### 1. Frontend (Streamlit UI)
- Interactive web interface
- Chat system for Q&A
- Document upload and summary pages

### 2. Backend (Python Logic Layer)
- Handles document processing
- Manages RAG pipeline execution
- Coordinates AI components

### 3. AI Pipeline
- **PDF Processor** → Extracts text from PDFs
- **Text Chunker** → Splits text into manageable chunks
- **Embedding Model** → Converts text into vector embeddings
- **FAISS Vector Store** → Stores and retrieves embeddings
- **LLM (Gemini API)** → Generates intelligent answers

### 4. Database (SQLite)
- Stores chat history
- Stores uploaded document metadata
- Maintains session information

### 🔷 High-Level Architecture

```
                ┌──────────────────────────┐
                │      Streamlit UI        │
                │   (Frontend Layer)       │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │     Backend Layer        │
                │ (Orchestration Engine)   │
                └──────────┬───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌────────────────┐  ┌────────────────┐
│ PDF Processor│  │ Embedding Gen   │  │ Summarizer     │
└──────┬───────┘  └──────┬─────────┘  └──────┬─────────┘
       ▼                 ▼                  ▼
        ┌────────────────────────────────────────┐
        │        Vector Store (FAISS)           │
        │   Semantic Search & Retrieval Layer   │
        └──────────────────┬─────────────────────┘
                           ▼
                ┌──────────────────────────┐
                │     RAG Pipeline         │
                │ (Context + Prompt Build) │
                └──────────┬───────────────┘
                           ▼
                ┌──────────────────────────┐
                │   Gemini LLM (AI Engine) │
                └──────────┬───────────────┘
                           ▼
                ┌──────────────────────────┐
                │   Final Answer + Sources │
                └──────────────────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │   SQLite Database        │
                │ (Chat History Storage)   │
                └──────────────────────────┘
```

---

## 🔄 Workflow

### 📥 Document Processing Workflow
```text
User Uploads PDF
        ↓
PDF Text Extraction (PyMuPDF / PyPDF2)
        ↓
Text Chunking (Fixed-size overlapping chunks)
        ↓
Embedding Generation (Sentence Transformers)
        ↓
Vector Storage (FAISS Index)
        ↓
Metadata Storage (SQLite)
```

### ❓ Question Answering Workflow
```text
User Query
        ↓
Query Embedding Generation
        ↓
FAISS Similarity Search (Top-K Relevant Chunks)
        ↓
Context Preparation (Retrieved Text + Metadata)
        ↓
Prompt Construction
        ↓
Gemini LLM Processing
        ↓
Final Answer Generation
        ↓
Source Citation Display (Document + Page Info)
        ↓
Chat History Storage (SQLite)
```

---

### 🎯 Key Highlights
✔ End-to-end Retrieval-Augmented Generation (RAG) system  
✔ Multi-PDF conversational AI assistant  
✔ Semantic search using vector embeddings  
✔ FAISS-based fast similarity retrieval  
✔ Google Gemini LLM integration for responses  
✔ Source-grounded answers with citations  
✔ Full-stack Streamlit web application  
✔ Modular backend architecture (AI pipeline + services + DB)  
✔ Scalable design for future API or cloud deployment  
✔ Real-world enterprise-style document intelligence system  

---


### 🚀 Future Enhancements
- 🔐 User authentication (Login/Signup system)  
- 🌐 Multi-language support for global usage  
- 🎙️ Voice-based question input and responses  
- 📄 OCR support for scanned or image-based PDFs  
- ⚡ Hybrid search (Keyword + Semantic search)  
- 📊 Analytics dashboard for document insights  
- 🤖 Agent-based RAG system for complex reasoning tasks  
- ☁️ Cloud deployment with scalable backend (AWS/GCP/Azure)  
- 📱 Mobile-friendly responsive UI  
- 💾 Cloud database integration instead of local SQLite

---
