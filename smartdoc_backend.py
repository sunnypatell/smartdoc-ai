'''
Author: @Sunny Patel
Github: @sunnypatell

2025 All Rights Reserved by @sunnypatell.
'''

"""
SmartDoc – A Self‑Hosted AI Document Summarizer & Q&A Backend

This FastAPI app provides endpoints to:
  • Upload documents (PDF or plain text)
  • Retrieve a summary of the uploaded document
  • Ask questions about the document’s content
  • List documents and view their details
  • Optionally retrieve the processed text chunks (for debugging or advanced UI)

All processing is done locally using open‑source models:
  - Summarization: t5‑small (via Hugging Face pipelines)
  - Question Answering: distilbert‑base‑uncased‑distilled‑squad
  - Embeddings: SentenceTransformer (all‑MiniLM‑L6‑v2)
  - Vector Search: FAISS (IndexFlatL2)

No external API keys or paid services are required, making it free to run and host.
This backend is designed to be connected to a separate React/Next.js frontend.
"""

import io
import os
from typing import List, Dict, Any

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import PyPDF2  # For PDF text extraction
import numpy as np

from transformers import pipeline  # For summarization and QA
from sentence_transformers import SentenceTransformer  # For computing embeddings
import faiss  # For vector (embedding) search

# ------------------------------------------------------------------------------
# Initialize FastAPI and Configure CORS (to allow calls from your React app)
# ------------------------------------------------------------------------------
app = FastAPI(
    title="SmartDoc Backend API",
    description="A self‑hosted AI document summarizer and Q&A backend. "
                "Connect this API to your React/Next.js frontend.",
    version="1.0.0"
)

# Allow all origins for demo purposes. Adjust for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# In‑Memory Storage (For demo/portfolio purposes. Replace with a persistent DB in production.)
# ------------------------------------------------------------------------------
# Documents storage: Maps a document ID (int) to a dictionary with keys:
#   - filename: Original file name
#   - text: Full extracted text
#   - chunks: List of text chunks (for summarization and QA)
#   - embeddings: Numpy array of embeddings for each chunk
documents: Dict[int, Dict[str, Any]] = {}
# FAISS indexes for each document: Maps document ID to a FAISS index instance.
faiss_indexes: Dict[int, faiss.IndexFlatL2] = {}
# A simple counter to assign document IDs.
doc_id_counter = 1

# ------------------------------------------------------------------------------
# Load AI Models at Startup (Lightweight models for CPU-only free hosting)
# ------------------------------------------------------------------------------
print("Loading models... (this may take a few moments)")
try:
    # Summarization model: Using t5-small (lightweight)
    summarizer = pipeline(
        "summarization",
        model="t5-small",
        tokenizer="t5-small",
        framework="pt"
    )
    # Question Answering model: Using a distilled BERT fine‑tuned on SQuAD
    qa_model = pipeline(
        "question-answering",
        model="distilbert-base-uncased-distilled-squad",
        framework="pt"
    )
    # Embedding model: SentenceTransformer for computing embeddings
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"Error loading models: {e}")
    raise

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def extract_text(file: UploadFile) -> str:
    """
    Extract text from an uploaded file.
    Supports PDF files (using PyPDF2) and plain text files.
    """
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file.file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            file.file.seek(0)  # Reset pointer for potential future use
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF processing error: {str(e)}")
    else:
        # For text-based files, assume UTF-8 encoding.
        try:
            content = file.file.read().decode("utf-8")
            file.file.seek(0)
            return content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text file reading error: {str(e)}")


def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split text into chunks. This simple splitter uses character counts.
    In production, consider using token‑based splitting.
    """
    text = text.strip()
    if not text:
        return []
    # Create overlapping or non-overlapping chunks as needed.
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks


def create_embeddings(chunks: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks using SentenceTransformer.
    Returns a numpy array of embeddings.
    """
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    return embeddings


def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """
    Build a FAISS index from the embeddings using L2 (Euclidean) distance.
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# ------------------------------------------------------------------------------
# Pydantic Models for Request & Response Schemas
# ------------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str

class UploadResponse(BaseModel):
    doc_id: int
    message: str

class SummaryResponse(BaseModel):
    doc_id: int
    summary: str

class QueryResponse(BaseModel):
    doc_id: int
    query: str
    answer: str
    context_chunks: List[str]

class DocumentInfo(BaseModel):
    doc_id: int
    filename: str
    text_length: int
    num_chunks: int

# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    POST /upload
    -----------
    Upload a document file (PDF or plain text). The API will:
      1. Extract text from the file.
      2. Split the text into manageable chunks.
      3. Compute embeddings for each chunk.
      4. Create a FAISS index for fast semantic search.
      5. Store the document metadata, text, chunks, and embeddings in memory.
    
    Returns:
      - doc_id: A unique identifier for the document.
      - message: Status message.
    
    **Frontend Integration:**
      - Use a multipart/form-data POST request with the file field named "file".
    """
    global doc_id_counter

    text = extract_text(file)
    if not text:
        raise HTTPException(status_code=400, detail="No extractable text found.")

    # Create chunks from the text.
    chunks = chunk_text(text, chunk_size=500)
    if not chunks:
        raise HTTPException(status_code=400, detail="Document processing resulted in no content.")

    # Compute embeddings for each chunk.
    embeddings = create_embeddings(chunks)

    # Build a FAISS index for these embeddings.
    index = create_faiss_index(embeddings)

    # Store the document and its metadata.
    doc_id = doc_id_counter
    documents[doc_id] = {
        "filename": file.filename,
        "text": text,
        "chunks": chunks,
        "embeddings": embeddings
    }
    faiss_indexes[doc_id] = index
    doc_id_counter += 1

    return UploadResponse(doc_id=doc_id, message="Document uploaded and processed successfully.")


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    GET /documents
    --------------
    List all uploaded documents with basic metadata.
    
    **Frontend Integration:**
      - Call this endpoint via a GET request to display a list of documents.
    """
    docs_info = []
    for doc_id, data in documents.items():
        docs_info.append(DocumentInfo(
            doc_id=doc_id,
            filename=data.get("filename", "Unknown"),
            text_length=len(data.get("text", "")),
            num_chunks=len(data.get("chunks", []))
        ))
    return docs_info


@app.get("/document/{doc_id}", response_model=DocumentInfo)
async def get_document_info(doc_id: int):
    """
    GET /document/{doc_id}
    ----------------------
    Retrieve metadata for a specific document (e.g., filename, text length, number of chunks).
    
    **Frontend Integration:**
      - Use this to display detailed info about a document.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    data = documents[doc_id]
    return DocumentInfo(
        doc_id=doc_id,
        filename=data.get("filename", "Unknown"),
        text_length=len(data.get("text", "")),
        num_chunks=len(data.get("chunks", []))
    )


@app.get("/document/{doc_id}/summary", response_model=SummaryResponse)
async def summarize_document(doc_id: int):
    """
    GET /document/{doc_id}/summary
    ------------------------------
    Generate a summary for the document identified by doc_id.
    
    **Process:**
      - For short documents (text length < 1000 characters), summarize the full text directly.
      - For longer documents, split the text into chunks, summarize each chunk, and then summarize the combined summaries.
    
    **Frontend Integration:**
      - Make a GET request to retrieve a summary and display it in the UI.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    text = documents[doc_id]["text"]

    try:
        if len(text) < 1000:
            # Direct summarization for shorter documents.
            summary_output = summarizer(text, max_length=150, min_length=40, do_sample=False)
            summary = summary_output[0]['summary_text']
        else:
            # For longer texts, first summarize each chunk.
            chunks = chunk_text(text, chunk_size=500)
            chunk_summaries = []
            for chunk in chunks:
                if chunk.strip():
                    chunk_summary = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
                    chunk_summaries.append(chunk_summary[0]['summary_text'])
            if not chunk_summaries:
                raise Exception("No chunk summaries produced.")
            combined_summary = " ".join(chunk_summaries)
            final_output = summarizer(combined_summary, max_length=150, min_length=40, do_sample=False)
            summary = final_output[0]['summary_text']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
    
    return SummaryResponse(doc_id=doc_id, summary=summary)


@app.post("/document/{doc_id}/query", response_model=QueryResponse)
async def query_document(doc_id: int, query_request: QueryRequest):
    """
    POST /document/{doc_id}/query
    -----------------------------
    Answer a user’s question regarding the specified document.
    
    **Process:**
      1. Compute an embedding for the input query.
      2. Use the FAISS index for the document to find the top‑k most similar text chunks.
      3. Concatenate these chunks to create a context.
      4. Run the QA model with the context and query to generate an answer.
    
    **Expected Request JSON:**
      { "query": "Your question here" }
    
    **Frontend Integration:**
      - Send a POST request with a JSON body containing the query.
      - Display the returned answer and (optionally) the context chunks.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")

    query = query_request.query
    # Compute the query's embedding.
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)

    # Retrieve the FAISS index for this document.
    index = faiss_indexes[doc_id]
    k = 3  # Number of chunks to retrieve.
    distances, indices = index.search(query_embedding, k)

    # Retrieve the corresponding text chunks.
    chunks = documents[doc_id]["chunks"]
    retrieved_chunks = []
    context = ""
    for idx in indices[0]:
        if idx < len(chunks):
            chunk_text_value = chunks[idx]
            retrieved_chunks.append(chunk_text_value)
            context += chunk_text_value + " "

    if not context:
        raise HTTPException(status_code=500, detail="Unable to retrieve context for the query.")

    # Prepare input for the QA model.
    qa_input = {
        "question": query,
        "context": context,
    }
    try:
        qa_result = qa_model(qa_input)
        answer = qa_result.get("answer", "No answer found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question Answering error: {str(e)}")

    return QueryResponse(
        doc_id=doc_id,
        query=query,
        answer=answer,
        context_chunks=retrieved_chunks
    )


@app.get("/document/{doc_id}/chunks")
async def get_document_chunks(doc_id: int):
    """
    GET /document/{doc_id}/chunks
    -----------------------------
    Retrieve the processed text chunks for the given document.
    Useful for debugging or for advanced UI elements.
    
    **Frontend Integration:**
      - Call via GET to display or inspect the chunk breakdown.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"doc_id": doc_id, "chunks": documents[doc_id]["chunks"]}

# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Run the server on host 127.0.0.1 and port 8000.
    uvicorn.run(app, host="0.0.0.0", port=8000)
