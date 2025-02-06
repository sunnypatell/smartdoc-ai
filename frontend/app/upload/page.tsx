"use client"

import { useState } from "react"
import { Upload, CheckCircle, AlertCircle, Loader } from "lucide-react"
import Link from "next/link"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string; docId?: number } | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      })

      const result = await response.json()
      setUploadResult({
        success: response.ok,
        message: response.ok ? `Document uploaded successfully.` : "Upload failed.",
        docId: result.doc_id,
      })
    } catch (error) {
      setUploadResult({
        success: false,
        message: "An error occurred during upload.",
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-center">Upload Document</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md">
        <div className="mb-6">
          <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-2">
            Select a PDF or text file
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
            <div className="space-y-1 text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor="file"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                >
                  <span>Upload a file</span>
                  <input
                    id="file"
                    name="file"
                    type="file"
                    className="sr-only"
                    onChange={handleFileChange}
                    accept=".pdf,.txt"
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PDF or TXT up to 10MB</p>
            </div>
          </div>
        </div>
        <button
          type="submit"
          disabled={!file || uploading}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-300"
        >
          {uploading ? (
            <>
              <Loader className="inline-block mr-2 animate-spin" size={20} />
              Uploading...
            </>
          ) : (
            "Upload Document"
          )}
        </button>
      </form>
      {uploadResult && (
        <div
          className={`mt-4 p-4 rounded-md ${
            uploadResult.success ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          }`}
        >
          {uploadResult.success ? (
            <CheckCircle className="inline-block mr-2" size={20} />
          ) : (
            <AlertCircle className="inline-block mr-2" size={20} />
          )}
          {uploadResult.message}
          {uploadResult.success && uploadResult.docId && (
            <p className="mt-2">
              <Link href={`/documents/${uploadResult.docId}`} className="text-blue-500 hover:text-blue-600">
                View uploaded document
              </Link>
            </p>
          )}
        </div>
      )}
    </div>
  )
}

