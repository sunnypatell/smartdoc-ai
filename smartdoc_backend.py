'''
Author: @Sunny Patel
Github: @sunnypatell

2025 All Rights Reserved by @sunnypatell.
'''

"""
SmartDoc – A Self‑Hosted AI Document Summarizer & Q&A Backend

This FastAPI app provides endpoints to:
  • Upload documents (PDF or plain text)
  • Retrieve a summary of the uploaded document (using recursive summarization with a high‑quality model)
  • Answer questions about the document’s content (with increased context retrieval)
  • List documents and view their details
  • Retrieve the processed text chunks (for debugging or advanced UI use)

Dependencies (all run locally):
  - FastAPI, Uvicorn
  - Transformers (using heavy models for quality)
  - SentenceTransformer (for embeddings)
  - PyPDF2 for PDF text extraction
  - FAISS (faiss‑cpu) for vector search
  - NumPy

All endpoints remain unchanged so your React/Next.js frontend needs no updates.
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
# Initialize FastAPI and Configure CORS
# ------------------------------------------------------------------------------
app = FastAPI(
    title="SmartDoc Backend API",
    description="A self‑hosted AI document summarizer and Q&A backend. Connect this API to your React/Next.js frontend.",
    version="1.0.0"
)

# Allow all origins for demo purposes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# In‑Memory Storage (For demo/portfolio; in production use a persistent DB)
# ------------------------------------------------------------------------------
# 'documents' maps document IDs to a dict with:
#   - filename: original file name
#   - text: full extracted text
#   - chunks: list of text chunks (for summarization and QA)
#   - embeddings: NumPy array of embeddings for each chunk
documents: Dict[int, Dict[str, Any]] = {}
# 'faiss_indexes' maps document ID to a FAISS index instance.
faiss_indexes: Dict[int, faiss.IndexFlatL2] = {}
doc_id_counter = 1  # Simple counter for document IDs

# ------------------------------------------------------------------------------
# Load AI Models at Startup
# ------------------------------------------------------------------------------
print("Loading models... (this may take a few moments)")
try:
    # Use a more powerful summarization model:
    # google/flan-t5-xl is instruction-tuned and produces richer summaries.
    summarizer = pipeline(
        "summarization",
        model="google/flan-t5-xl",
        tokenizer="google/flan-t5-xl",
        framework="pt"
    )
    # For question answering, we choose a larger model for better accuracy.
    qa_model = pipeline(
        "question-answering",
        model="deepset/roberta-large-squad2",
        framework="pt"
    )
    # For embeddings, we switch to a more accurate model.
    embedding_model = SentenceTransformer("all-mpnet-base-v2")
except Exception as e:
    print(f"Error loading models: {e}")
    raise

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------

def extract_text(file: UploadFile) -> str:
    """
    Extract text from an uploaded file.
    Supports PDF (via PyPDF2) and plain text files.
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
            file.file.seek(0)
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF processing error: {str(e)}")
    else:
        try:
            content = file.file.read().decode("utf-8")
            file.file.seek(0)
            return content
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text file reading error: {str(e)}")


def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split text into non-overlapping chunks based on character count.
    (For production, consider token-based splitting.)
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
    Build a FAISS index from the embeddings using L2 (Euclidean) distance.
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index


def recursive_summarize(text: str,
                        threshold: int = 800,
                        max_length: int = 300,
                        min_length: int = 150,
                        recursion_depth: int = 0,
                        max_recursion: int = 2) -> str:
    """
    Recursively summarize the input text until it is below a specified threshold.
    
    If the text appears to be a resume/CV, a custom prompt is added to extract key details.
    
    Parameters:
      - threshold: Character length below which direct summarization is applied.
      - max_length/min_length: Control the summary output length.
      - recursion_depth: Current recursion level.
      - max_recursion: Maximum allowed recursion depth.
    """
    # For resumes/CVs, add a prompt to extract key details.
    lower_text = text.lower()
    if "resume" in lower_text or "curriculum vitae" in lower_text or "cv" in lower_text:
        prompt_prefix = "Summarize this resume with key details on education, experience, skills, certifications, and projects: "
    else:
        prompt_prefix = "summarize: "
    
    if len(text) < threshold or recursion_depth >= max_recursion:
        try:
            summary_output = summarizer(prompt_prefix + text, max_length=max_length, min_length=min_length, do_sample=False)
            return summary_output[0]['summary_text']
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
    else:
        # Split text into larger chunks to preserve context.
        chunks = chunk_text(text, chunk_size=800)
        summaries = []
        for chunk in chunks:
            if chunk.strip():
                try:
                    chunk_summary = summarizer(prompt_prefix + chunk, max_length=max_length, min_length=min_length, do_sample=False)
                    summaries.append(chunk_summary[0]['summary_text'])
                except Exception as e:
                    continue  # Skip failed chunks.
        if not summaries:
            try:
                return summarizer(prompt_prefix + text, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")
        combined = " ".join(summaries)
        # Recursively summarize the combined summaries.
        return recursive_summarize(combined,
                                   threshold=threshold,
                                   max_length=max_length,
                                   min_length=min_length,
                                   recursion_depth=recursion_depth + 1,
                                   max_recursion=max_recursion)

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
# API Endpoints (Endpoints remain unchanged)
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
    List all uploaded documents with basic metadata.
    
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
    Retrieve metadata for a specific document.
    
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
    Generate a summary for the document identified by doc_id.
    
    Process:
      - For shorter documents, direct summarization is applied.
      - For larger documents, recursive summarization is used to capture full context.
    
    Frontend: Make a GET request to display the summary.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    text = documents[doc_id]["text"]
    summary = recursive_summarize(text,
                                  threshold=800,
                                  max_length=300,
                                  min_length=150)
    return SummaryResponse(doc_id=doc_id, summary=summary)


@app.post("/document/{doc_id}/query", response_model=QueryResponse)
async def query_document(doc_id: int, query_request: QueryRequest):
    """
    POST /document/{doc_id}/query
    -----------------------------
    Answer a user’s question about the specified document.
    
    Process:
      1. Compute an embedding for the query.
      2. Use the FAISS index to retrieve the top-k similar text chunks.
      3. Concatenate these chunks to form context.
      4. Run the QA model with the context and query to generate an answer.
    
    Frontend: Send a POST request with JSON body { "query": "Your question here" }.
    """
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found.")

    query = query_request.query
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)

    # Retrieve more context by increasing k (here, 7 chunks).
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
    Retrieve the processed text chunks for the specified document.
    
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
