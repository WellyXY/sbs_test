import React from 'react'
import { Link } from 'react-router-dom'

const HomePage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🎬 Video Blind Testing Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Professional video comparison and blind testing tool with intelligent matching and detailed analysis
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <Link
            to="/folders"
            className="bg-blue-500 hover:bg-blue-600 text-white p-6 rounded-lg shadow-md transition-colors"
          >
            <div className="text-3xl mb-2">📁</div>
            <h3 className="text-lg font-semibold mb-2">Folder Management</h3>
            <p className="text-blue-100">Create folders and upload video files</p>
          </Link>
          
          <Link
            to="/tasks"
            className="bg-green-500 hover:bg-green-600 text-white p-6 rounded-lg shadow-md transition-colors"
          >
            <div className="text-3xl mb-2">📋</div>
            <h3 className="text-lg font-semibold mb-2">Task Management</h3>
            <p className="text-green-100">Create and manage blind testing tasks</p>
          </Link>
        </div>
      </div>
    </div>
  )
}

export default HomePage 