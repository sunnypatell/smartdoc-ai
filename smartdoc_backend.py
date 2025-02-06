"""
SmartDoc – A Self‑Hosted AI Document Summarizer & Q&A Backend

This FastAPI app provides endpoints to:
  • Upload documents (PDF or plain text)
  • Retrieve a summary of the uploaded document (using recursive summarization for large texts)
  • Ask questions about the document’s content (retrieving more context from FAISS)
  • List documents and view their details
  • Retrieve the processed text chunks (for debugging or advanced UI use)

Dependencies and packages used (all run locally):
  - FastAPI, Uvicorn
  - Transformers (using T5-small for summarization and distilbert-base-uncased-distilled-squad for QA)
  - SentenceTransformer (all‑MiniLM‑L6‑v2 for embeddings)
  - PyPDF2 for PDF text extraction
  - FAISS (faiss‑cpu) for vector search
  - NumPy

Endpoints remain the same so you don’t need to update your frontend.
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
    description="A self‑hosted AI document summarizer and Q&A backend. Connect this API to your React/Next.js frontend.",
    version="1.0.0"
)

# Allow all origins for demo purposes (adjust for production if needed).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# In‑Memory Storage (For demo/portfolio purposes – in production, consider a persistent DB)
# ------------------------------------------------------------------------------
# 'documents' maps a document ID (int) to a dict with:
#   - filename: Original file name
#   - text: Full extracted text
#   - chunks: List of text chunks (for summarization and QA)
#   - embeddings: NumPy array of embeddings for each chunk
documents: Dict[int, Dict[str, Any]] = {}
# 'faiss_indexes' maps document ID to a FAISS index instance.
faiss_indexes: Dict[int, faiss.IndexFlatL2] = {}
doc_id_counter = 1  # A simple counter to assign document IDs

# ------------------------------------------------------------------------------
# Load AI Models at Startup (same dependencies as originally used)
# ------------------------------------------------------------------------------
print("Loading models... (this may take a few moments)")
try:
    # Summarization model: T5-small (you can swap to T5-base if you want improved results and have the CPU capacity)
    summarizer = pipeline(
        "summarization",
        model="t5-small",
        tokenizer="t5-small",
        framework="pt"
    )
    # Question Answering model: distilbert-base-uncased-distilled-squad
    qa_model = pipeline(
        "question-answering",
        model="distilbert-base-uncased-distilled-squad",
        framework="pt"
    )
    # Embedding model: SentenceTransformer using all-MiniLM-L6-v2
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
        # Assume UTF-8 encoded plain text file.
        try:
            content = file.file.read().decode("utf-8")
            file.file.seek(0)
            return content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text file reading error: {str(e)}")


def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split text into non-overlapping chunks based on character count.
    (For production, you might want token-based splitting.)
    """
    text = text.strip()
    if not text:
        return []
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def create_embeddings(chunks: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text chunks using SentenceTransformer.
    Returns a NumPy array.
    """
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True)
    return embeddings


def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    """
    Build a FAISS index from embeddings using L2 (Euclidean) distance.
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def recursive_summarize(text: str, threshold: int = 1000, max_length: int = 150, min_length: int = 40,
                        recursion_depth: int = 0, max_recursion: int = 3) -> str:
    """
    Recursively summarize the input text until it is below a specified threshold.
    
    If the text is shorter than 'threshold' characters or if maximum recursion depth is reached,
    the summarizer is applied directly.
    
    Otherwise, the text is split into chunks (here, of size 800 characters), each chunk is summarized,
    the summaries are concatenated, and the process repeats.
    """
    if len(text) < threshold or recursion_depth >= max_recursion:
        try:
            summary_output = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary_output[0]['summary_text']
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
    else:
        chunks = chunk_text(text, chunk_size=800)
        summaries = []
        for chunk in chunks:
            if chunk.strip():
                try:
                    chunk_summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
                    summaries.append(chunk_summary[0]['summary_text'])
                except Exception as e:
                    # Skip any chunk that fails summarization.
                    continue
        if not summaries:
            # Fallback: try summarizing the entire text directly.
            try:
                return summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
        combined = " ".join(summaries)
        # Recursively summarize the combined summaries.
        return recursive_summarize(combined, threshold=threshold, max_length=max_length, min_length=min_length,
                                   recursion_depth=recursion_depth + 1, max_recursion=max_recursion)

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
    Upload a document (PDF or plain text). The endpoint:
      1. Extracts text.
      2. Splits text into chunks.
      3. Computes embeddings for each chunk.
      4. Creates a FAISS index for fast semantic search.
      5. Stores document metadata, text, chunks, and embeddings.
    
    Frontend: Use a multipart/form-data POST request with the file field named "file".
    """
    global doc_id_counter

    text = extract_text(file)
    if not text:
        raise HTTPException(status_code=400, detail="No extractable text found.")

    chunks = chunk_text(text, chunk_size=500)
    if not chunks:
        raise HTTPException(status_code=400, detail="Document processing resulted in no content.")

    embeddings = create_embeddings(chunks)
    index = create_faiss_index(embeddings)

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
    Lists all uploaded documents with basic metadata.
    
    Frontend: Use a GET request to display a list of documents.
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
    Retrieves metadata for a specific document.
    
    Frontend: Use this to display document details.
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
    Generates a summary for the document identified by doc_id.
    
    Process:
      - For shorter documents, a direct summarization is performed.
      - For larger documents, a recursive summarization is applied so that
        the full context is taken into account.
    
    Frontend: Make a GET request to display the summary.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    text = documents[doc_id]["text"]
    summary = recursive_summarize(text, threshold=1000, max_length=150, min_length=40)
    return SummaryResponse(doc_id=doc_id, summary=summary)


@app.post("/document/{doc_id}/query", response_model=QueryResponse)
async def query_document(doc_id: int, query_request: QueryRequest):
    """
    POST /document/{doc_id}/query
    -----------------------------
    Answers a user’s question about the specified document.
    
    Process:
      1. Computes an embedding for the input query.
      2. Uses the FAISS index to retrieve the top-k most similar text chunks.
      3. Concatenates these chunks to form a context.
      4. Runs the QA model with the context and query to generate an answer.
    
    Frontend: Send a POST request with a JSON body { "query": "Your question here" }.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")

    query = query_request.query
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)

    # Increase 'k' to retrieve more context (here we use 7 chunks)
    index = faiss_indexes[doc_id]
    k = 7
    distances, indices = index.search(query_embedding, k)

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
    Retrieves the processed text chunks for the specified document.
    
    Frontend: Useful for debugging or advanced UI features.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"doc_id": doc_id, "chunks": documents[doc_id]["chunks"]}


# ------------------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
