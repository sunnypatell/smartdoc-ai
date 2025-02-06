import Link from "next/link"
import { FileText, Search, Zap, Brain, Lock } from "lucide-react"
import type React from "react" // Added import for React

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <section className="pt-20 pb-32 px-4 text-center">
        <h1 className="text-5xl font-bold mb-4 text-blue-900">Welcome to SmartDoc</h1>
        <p className="text-xl mb-8 text-blue-800 max-w-2xl mx-auto">
          Unlock the power of your documents with AI-driven summarization and intelligent Q&A capabilities.
        </p>
        <Link
          href="/upload"
          className="bg-blue-600 text-white px-8 py-3 rounded-full text-lg font-semibold hover:bg-blue-700 transition-colors duration-300 inline-flex items-center"
        >
          <FileText className="mr-2" size={24} />
          Start Uploading
        </Link>
      </section>

      {/* Key Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center text-blue-900">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Zap className="w-12 h-12 text-yellow-500" />}
              title="Smart Summarization"
              description="Get concise, accurate summaries of your documents in seconds, powered by advanced AI."
            />
            <FeatureCard
              icon={<Search className="w-12 h-12 text-green-500" />}
              title="Intelligent Q&A"
              description="Ask questions about your documents and receive precise answers, eliminating hours of manual searching."
            />
            <FeatureCard
              icon={<Lock className="w-12 h-12 text-red-500" />}
              title="Secure & Private"
              description="Your documents are processed locally, ensuring complete privacy and security of your sensitive information."
            />
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-blue-50">
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center text-blue-900">How It Works</h2>
          <div className="space-y-8">
            <Step number={1} title="Upload Your Document">
              Simply upload your PDF or text file to our secure platform.
            </Step>
            <Step number={2} title="AI Processing">
              Our advanced AI analyzes and processes your document, extracting key information.
            </Step>
            <Step number={3} title="Get Insights">
              Receive a concise summary and start asking questions to dive deeper into your document's content.
            </Step>
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-20 bg-blue-900 text-white text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to Supercharge Your Document Analysis?</h2>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          Join the growing number of professionals using SmartDoc to save time and gain deeper insights from their
          documents.
        </p>
        <Link
          href="/upload"
          className="bg-white text-blue-900 px-8 py-3 rounded-full text-lg font-semibold hover:bg-blue-100 transition-colors duration-300 inline-flex items-center"
        >
          <Brain className="mr-2" size={24} />
          Try SmartDoc Now
        </Link>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-blue-50 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
      <div className="flex justify-center mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2 text-blue-900 text-center">{title}</h3>
      <p className="text-blue-800 text-center">{description}</p>
    </div>
  )
}

function Step({ number, title, children }: { number: number; title: string; children: React.ReactNode }) {
  return (
    <div className="flex items-start">
      <div className="bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center font-bold text-lg mr-4 flex-shrink-0">
        {number}
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2 text-blue-900">{title}</h3>
        <p className="text-blue-800">{children}</p>
      </div>
    </div>
  )
}

