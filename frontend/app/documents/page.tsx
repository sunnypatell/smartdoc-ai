"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { FileText, Eye, Loader, Search } from "lucide-react"

interface Document {
  doc_id: number
  filename: string
  text_length: number
  num_chunks: number
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch("http://0.0.0.0:8000/documents")
        if (!response.ok) {
          throw new Error("Failed to fetch documents")
        }
        const data = await response.json()
        setDocuments(data)
        setFilteredDocuments(data)
      } catch (err) {
        setError("An error occurred while fetching documents.")
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [])

  useEffect(() => {
    const filtered = documents.filter((doc) => doc.filename.toLowerCase().includes(searchTerm.toLowerCase()))
    setFilteredDocuments(filtered)
  }, [searchTerm, documents])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="animate-spin text-blue-500" size={48} />
      </div>
    )
  }

  if (error) {
    return <div className="text-center text-red-500">{error}</div>
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center">Your Documents</h1>
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Search className="absolute right-3 top-2.5 text-gray-400" size={20} />
        </div>
      </div>
      {filteredDocuments.length === 0 ? (
        <div className="text-center text-gray-500">
          <p className="mb-4">No documents found.</p>
          <Link
            href="/upload"
            className="inline-block bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors duration-300"
          >
            Upload a Document
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((doc) => (
            <div
              key={doc.doc_id}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <FileText className="text-blue-500" size={24} />
                <Link href={`/documents/${doc.doc_id}`} className="text-blue-500 hover:text-blue-600">
                  <Eye className="inline-block mr-1" size={20} />
                  View
                </Link>
              </div>
              <h2 className="text-xl font-semibold mb-2 truncate">{doc.filename}</h2>
              <div className="text-sm text-gray-600">
                <p>{doc.text_length} characters</p>
                <p>{doc.num_chunks} chunks</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

