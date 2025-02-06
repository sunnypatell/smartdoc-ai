"use client"

import { useState, useEffect } from "react"
import { Loader } from "lucide-react"

interface ChunksResponse {
  doc_id: number
  chunks: string[]
}

export default function DocumentChunksPage({ params }: { params: { id: string } }) {
  const [chunks, setChunks] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchChunks = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/document/${params.id}/chunks`)
        if (!response.ok) {
          throw new Error("Failed to fetch document chunks")
        }
        const data: ChunksResponse = await response.json()
        setChunks(data.chunks)
      } catch (err) {
        setError("An error occurred while fetching document chunks.")
      } finally {
        setLoading(false)
      }
    }

    fetchChunks()
  }, [params.id])

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
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Document Chunks</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        {chunks.map((chunk, index) => (
          <div key={index} className="mb-4 p-2 bg-gray-100 rounded">
            <p className="text-sm text-gray-700">{chunk}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

