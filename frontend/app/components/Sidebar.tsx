import Link from "next/link"
import { FileText, Home, Upload, Settings, HelpCircle } from "lucide-react"

const Sidebar = () => {
  return (
    <div className="bg-white w-64 h-full shadow-lg hidden sm:block">
      <nav className="mt-10">
        <Link href="/" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-800">
          <Home className="mr-3" size={20} />
          Home
        </Link>
        <Link
          href="/upload"
          className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-800"
        >
          <Upload className="mr-3" size={20} />
          Upload Document
        </Link>
        <Link
          href="/documents"
          className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-800"
        >
          <FileText className="mr-3" size={20} />
          Documents
        </Link>
        <Link
          href="/settings"
          className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-800"
        >
          <Settings className="mr-3" size={20} />
          Settings
        </Link>
        <Link href="/help" className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-gray-800">
          <HelpCircle className="mr-3" size={20} />
          Help
        </Link>
      </nav>
    </div>
  )
}

export default Sidebar

