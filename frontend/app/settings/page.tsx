"use client"

import { useState } from "react"
import { Sun, Moon } from "lucide-react"

const Settings = () => {
  const [theme, setTheme] = useState("light")
  const [fontSize, setFontSize] = useState("medium")

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light")
    // In a real application, you would apply the theme change here
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">UI Customization</h2>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Theme</label>
          <button
            onClick={toggleTheme}
            className="flex items-center justify-center w-16 h-8 rounded-full bg-background"
          >
            {theme === "light" ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Font Size</label>
          <select
            value={fontSize}
            onChange={(e) => setFontSize(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export default Settings

