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
  - Summarization: `t5-small` (~300MB)
    ```python
    summarizer = pipeline(
        "summarization",
        model="t5-small",
        tokenizer="t5-small",
        framework="pt"
    )
    ```
  - Q&A: `distilbert-base-uncased-distilled-squad` (~250MB)
    ```python
    qa_model = pipeline(
        "question-answering", 
        model="distilbert-base-uncased-distilled-squad",
        framework="pt"
    )
    ```
  - Embeddings: `all-MiniLM-L6-v2` (~90MB)
    ```python
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    ```
  - Vector Search: FAISS

Total model size: ~640MB
## Setup & Installation

### Windows Environment Setup
1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
venv\Scripts\activate
```

3. Install required packages:
```bash
pip install fastapi uvicorn python-multipart PyPDF2 transformers sentence-transformers faiss-cpu torch numpy
```

# Run the server
```bash
uvicorn smartdoc_backend:app --reload
```
Server will be available at `http://127.0.0.1:8000`. If by chance it isn't that IP, check your CLI it will display the available IP it chose and port

> Chute (end) the virtual environment using `deactivate` command 

## API Endpoints

### Document Management

- `POST /upload` - Upload PDF/text documents
- `GET /documents` - List all documents
- `GET /document/{doc_id}` - Get document metadata

### AI Features

- `GET /document/{doc_id}/summary` - Generate document summary
- `POST /document/{doc_id}/query` - Ask questions about document content
- `GET /document/{doc_id}/chunks` - Get document chunks (debug)

## Usage Example

```python
import requests

# Upload a document
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://127.0.0.1:8000/upload', files=files)
doc_id = response.json()['doc_id']

# Get a summary
summary = requests.get(f'http://127.0.0.1:8000/document/{doc_id}/summary')

# Ask a question
query = {'query': 'What is this document about?'}
answer = requests.post(f'http://127.0.0.1:8000/document/{doc_id}/query', json=query)
```

## License
MIT License - See [LICENSE](LICENSE) for more details.
