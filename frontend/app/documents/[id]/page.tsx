"use client"

import { useState, useEffect } from "react"
import { FileText, AlignLeft, HelpCircle, Loader, ChevronDown, ChevronUp } from "lucide-react"

interface DocumentInfo {
  doc_id: number
  filename: string
  text_length: number
  num_chunks: number
}

interface SummaryResponse {
  doc_id: number
  summary: string
}

interface QueryResponse {
  doc_id: number
  query: string
  answer: string
  context_chunks: string[]
}

export default function DocumentPage({ params }: { params: { id: string } }) {
  const [document, setDocument] = useState<DocumentInfo | null>(null)
  const [summary, setSummary] = useState<string | null>(null)
  const [query, setQuery] = useState("")
  const [answer, setAnswer] = useState<string | null>(null)
  const [context, setContext] = useState<string[]>([])
  const [chunks, setChunks] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [summarizing, setSummarizing] = useState(false)
  const [querying, setQuerying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showChunks, setShowChunks] = useState(false)

  useEffect(() => {
    const fetchDocumentInfo = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/document/${params.id}`)
        if (!response.ok) {
          throw new Error("Failed to fetch document info")
        }
        const data = await response.json()
        setDocument(data)
      } catch (err) {
        setError("An error occurred while fetching document info.")
      } finally {
        setLoading(false)
      }
    }

    fetchDocumentInfo()
  }, [params.id])

  const handleSummarize = async () => {
    setSummarizing(true)
    try {
      const response = await fetch(`http://127.0.0.1:8000/document/${params.id}/summary`)
      if (!response.ok) {
        throw new Error("Failed to fetch summary")
      }
      const data: SummaryResponse = await response.json()
      setSummary(data.summary)
    } catch (err) {
      setError("An error occurred while fetching the summary.")
    } finally {
      setSummarizing(false)
    }
  }

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    setQuerying(true)
    try {
      const response = await fetch(`http://127.0.0.1:8000/document/${params.id}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      })
      if (!response.ok) {
        throw new Error("Failed to fetch answer")
      }
      const data: QueryResponse = await response.json()
      setAnswer(data.answer)
      setContext(data.context_chunks)
    } catch (err) {
      setError("An error occurred while fetching the answer.")
    } finally {
      setQuerying(false)
    }
  }

  const fetchChunks = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/document/${params.id}/chunks`)
      if (!response.ok) {
        throw new Error("Failed to fetch chunks")
      }
      const data = await response.json()
      setChunks(data.chunks)
    } catch (err) {
      setError("An error occurred while fetching the chunks.")
    }
  }

  const toggleChunks = () => {
    if (!showChunks && chunks.length === 0) {
      fetchChunks()
    }
    setShowChunks(!showChunks)
  }

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

  if (!document) {
    return <div className="text-center">Document not found.</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">{document.filename}</h1>
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4">Document Information</h2>
        <p className="flex items-center text-gray-600">
          <FileText className="mr-2" size={20} />
          {document.text_length} characters | {document.num_chunks} chunks
        </p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4">Summary</h2>
        {summary ? (
          <p className="text-gray-700">{summary}</p>
        ) : (
          <button
            onClick={handleSummarize}
            disabled={summarizing}
            className="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors duration-300 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {summarizing ? (
              <>
                <Loader className="inline-block mr-2 animate-spin" size={20} />
                Generating Summary...
              </>
            ) : (
              <>
                <AlignLeft className="inline-block mr-2" size={20} />
                Generate Summary
              </>
            )}
          </button>
        )}
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4">Ask a Question</h2>
        <form onSubmit={handleQuery}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question here"
            className="w-full p-2 border border-gray-300 rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={querying}
            className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition-colors duration-300 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {querying ? (
              <>
                <Loader className="inline-block mr-2 animate-spin" size={20} />
                Processing...
              </>
            ) : (
              <>
                <HelpCircle className="inline-block mr-2" size={20} />
                Ask Question
              </>
            )}
          </button>
        </form>
        {answer && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Answer:</h3>
            <p className="text-gray-700">{answer}</p>
            {context.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Context:</h4>
                {context.map((chunk, index) => (
                  <p key={index} className="text-sm text-gray-600 mb-2">
                    {chunk}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <button onClick={toggleChunks} className="flex items-center justify-between w-full text-left">
          <h2 className="text-xl font-semibold">Document Chunks</h2>
          {showChunks ? (
            <ChevronUp className="text-gray-500" size={20} />
          ) : (
            <ChevronDown className="text-gray-500" size={20} />
          )}
        </button>
        {showChunks && (
          <div className="mt-4">
            {chunks.length === 0 ? (
              <p className="text-gray-600">Loading chunks...</p>
            ) : (
              chunks.map((chunk, index) => (
                <div key={index} className="mb-4 p-2 bg-gray-100 rounded">
                  <p className="text-sm text-gray-700">{chunk}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}

