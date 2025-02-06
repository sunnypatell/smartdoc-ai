# SmartDoc AI

A self-hosted AI document summarizer and Q&A backend that processes documents locally without requiring external API keys or paid services.

## Features

- 🔎 Document upload and text extraction (PDF/TXT) 
- 📝 Automatic document summarization
- ❓ Question answering system
- 🔍 Semantic search using FAISS
- 💻 Local processing with no external APIs
- ⚡ FastAPI backend ready for React frontend

## Tech Stack

- Backend Framework: FastAPI
- AI Models:
  - Summarization: `t5-small`
  - Q&A: `distilbert-base-uncased-distilled-squad`
  - Embeddings: `all-MiniLM-L6-v2`
  - Vector Search: FAISS

## Installation

```bash
# Install required packages
pip install fastapi uvicorn python-multipart PyPDF2 transformers sentence-transformers faiss-cpu torch
```

# Run the server
```
python smartdoc_backend.py
```
Server will be available at `http://localhost:8000`
