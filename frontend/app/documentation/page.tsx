"use client"

import { Code, FileText, HelpCircle, Zap } from "lucide-react"

export default function DeveloperPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-6">SmartDoc Developer Documentation</h1>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Overview</h2>
        <p className="mb-4">
          SmartDoc is an AI-powered document summarizer and Q&A system developed by Sunny Patel. It demonstrates the
          integration of advanced NLP techniques with a modern web frontend.
        </p>
        <p>
          This project is intended for demonstration purposes and showcases skills in both backend Python development
          and frontend React/Next.js implementation.
        </p>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Tech Stack</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-xl font-medium mb-2">Backend</h3>
            <ul className="list-disc pl-5">
              <li>Python</li>
              <li>FastAPI</li>
              <li>Hugging Face Transformers</li>
              <li>SentenceTransformer</li>
              <li>FAISS</li>
            </ul>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2">Frontend</h3>
            <ul className="list-disc pl-5">
              <li>React</li>
              <li>Next.js</li>
              <li>Tailwind CSS</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Key Features</h2>
        <ul className="space-y-4">
          <li className="flex items-start">
            <FileText className="mr-2 mt-1 text-blue-500" size={20} />
            <div>
              <h3 className="font-semibold">Document Upload and Processing</h3>
              <p>Support for PDF and plain text files, with automatic text extraction and chunking.</p>
            </div>
          </li>
          <li className="flex items-start">
            <Zap className="mr-2 mt-1 text-yellow-500" size={20} />
            <div>
              <h3 className="font-semibold">AI-Powered Summarization</h3>
              <p>Generate concise summaries of uploaded documents using advanced language models.</p>
            </div>
          </li>
          <li className="flex items-start">
            <HelpCircle className="mr-2 mt-1 text-green-500" size={20} />
            <div>
              <h3 className="font-semibold">Question Answering</h3>
              <p>Ask questions about document content and receive AI-generated answers.</p>
            </div>
          </li>
          <li className="flex items-start">
            <Code className="mr-2 mt-1 text-purple-500" size={20} />
            <div>
              <h3 className="font-semibold">Vector Search</h3>
              <p>Efficient similarity search using FAISS for fast and accurate information retrieval.</p>
            </div>
          </li>
        </ul>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">API Documentation</h2>
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-medium mb-2">Upload Document</h3>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
              <code>{`POST /upload
Content-Type: multipart/form-data

Parameters:
- file: File (PDF or TXT)

Response:
{
  "doc_id": number,
  "message": string
}`}</code>
            </pre>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2">Get Document Summary</h3>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
              <code>{`GET /document/{doc_id}/summary

Response:
{
  "doc_id": number,
  "summary": string
}`}</code>
            </pre>
          </div>
          <div>
            <h3 className="text-xl font-medium mb-2">Query Document</h3>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
              <code>{`POST /document/{doc_id}/query
Content-Type: application/json

Request Body:
{
  "query": string
}

Response:
{
  "answer": string,
  "context_chunks": string[]
}`}</code>
            </pre>
          </div>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Frontend Integration</h2>
        <p className="mb-4">
          The frontend is built with Next.js and uses React hooks to manage state and interact with the backend API.
          Here's an example of how to use the upload functionality:
        </p>
        <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto">
          <code>{`import { useState } from 'react'

export default function UploadComponent() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("http://0.0.0.0:8000/upload", {
        method: "POST",
        body: formData,
      })
      const result = await response.json()
      console.log(result)
    } catch (error) {
      console.error("Upload failed:", error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        accept=".pdf,.txt"
      />
      <button type="submit" disabled={!file || uploading}>
        {uploading ? "Uploading..." : "Upload"}
      </button>
    </form>
  )
}`}</code>
        </pre>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
        <p className="mb-4">To run this project locally, follow these steps:</p>
        <ol className="list-decimal pl-5 space-y-2">
          <li>Clone the repository from GitHub (link to be added).</li>
          <li>
            Install backend dependencies:{" "}
            <code className="bg-gray-100 px-2 py-1 rounded">pip install -r requirements.txt</code>
          </li>
          <li>
            Start the backend server: <code className="bg-gray-100 px-2 py-1 rounded">python main.py</code>
          </li>
          <li>
            Install frontend dependencies: <code className="bg-gray-100 px-2 py-1 rounded">npm install</code>
          </li>
          <li>
            Start the frontend development server: <code className="bg-gray-100 px-2 py-1 rounded">npm run dev</code>
          </li>
          <li>
            Open your browser and navigate to{" "}
            <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:3000</code>
          </li>
        </ol>
      </section>
    </div>
  )
}

