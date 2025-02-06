"use client"

import { useState } from "react"
import { Github, Linkedin, Globe } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"

const Footer = () => {
  const [showTosDialog, setShowTosDialog] = useState(false)

  return (
    <footer className="bg-white shadow-md mt-auto">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap justify-between items-start">
          <div className="w-full md:w-1/3 mb-4 md:mb-0">
            <p className="text-center md:text-left text-sm text-gray-500">
              Built with Next.js 13, FastAPI, and Transformer models
            </p>
            <p className="text-center md:text-left text-sm text-gray-500 mt-2">A portfolio demonstration project</p>
          </div>

          <div className="w-full md:w-1/3 text-center mt-4 md:mt-0">
            <p className="text-sm">&copy; 2024 Sunny Patel</p>
            <p className="text-sm text-gray-600 mt-1">sunnypatel124555@gmail.com</p>
            <p className="text-sm text-gray-500 mt-2">This project is protected by copyright.</p>
            <Button
              variant="link"
              className="mt-2 text-blue-600 hover:text-blue-800"
              onClick={() => setShowTosDialog(true)}
            >
              Terms of Service
            </Button>
          </div>

          <div className="w-full md:w-1/3 text-center md:text-right mt-4 md:mt-0">
            <div className="flex justify-center md:justify-end space-x-4">
              <Button variant="ghost" size="icon" asChild>
                <a
                  href="https://github.com/sunnypatell"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600"
                >
                  <Github className="h-5 w-5" />
                  <span className="sr-only">GitHub</span>
                </a>
              </Button>
              <Button variant="ghost" size="icon" asChild>
                <a
                  href="https://www.linkedin.com/in/sunny-patel-30b460204/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600"
                >
                  <Linkedin className="h-5 w-5" />
                  <span className="sr-only">LinkedIn</span>
                </a>
              </Button>
              <Button variant="ghost" size="icon" asChild>
                <a
                  href="https://www.sunnypatel.net"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-blue-600"
                >
                  <Globe className="h-5 w-5" />
                  <span className="sr-only">Portfolio</span>
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <Dialog open={showTosDialog} onOpenChange={setShowTosDialog}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Terms of Service & Project Information</DialogTitle>
          </DialogHeader>
          <ScrollArea className="h-[400px] w-full rounded-md border p-4">
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Project Overview</h2>
              <p>
                SmartDoc is a technical demonstration project developed by Sunny Patel. It showcases the implementation
                of modern web technologies and machine learning models in a document processing application.
              </p>

              <h2 className="text-xl font-bold">Technical Stack</h2>
              <ul className="list-disc list-inside">
                <li>Frontend: Next.js 13 with React Server Components and TypeScript</li>
                <li>Backend: FastAPI with Python 3.10+</li>
                <li>ML Components: Transformer models for text processing and embeddings</li>
                <li>Vector Search: FAISS for similarity search operations</li>
                <li>Document Processing: PyPDF2 and custom text extraction pipeline</li>
              </ul>

              <h2 className="text-xl font-bold">Local Development Setup</h2>
              <p>
                This application is designed for local deployment only. It requires both the frontend and backend
                services to be running locally. The project serves as a portfolio demonstration and is not intended for
                production deployment.
              </p>

              <h2 className="text-xl font-bold">Usage Limitations</h2>
              <ul className="list-disc list-inside">
                <li>Development and demonstration purposes only</li>
                <li>Local deployment required - no cloud infrastructure</li>
                <li>Limited to processing demonstration documents</li>
                <li>No persistent storage implementation</li>
              </ul>

              <h2 className="text-xl font-bold">Intellectual Property</h2>
              <p>
                This project, including its architecture, implementation, and documentation, is the intellectual
                property of Sunny Patel. The codebase demonstrates full-stack development capabilities and serves as a
                portfolio piece.
              </p>

              <h2 className="text-xl font-bold">Contact Information</h2>
              <p>
                For technical discussions or inquiries about this implementation, contact:
                <br />
                Sunny Patel
                <br />
                Email: sunnypatel124555@gmail.com
              </p>

              <h2 className="text-xl font-bold">Copyright Notice</h2>
              <p>
                © 2024 Sunny Patel. All rights reserved. This demonstration project is protected by copyright. The
                implementation details, architecture, and code structure are provided for demonstration purposes. Any
                reproduction or distribution requires explicit permission from the author.
              </p>
            </div>
          </ScrollArea>
          <DialogFooter>
            <Button onClick={() => setShowTosDialog(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </footer>
  )
}

export default Footer

