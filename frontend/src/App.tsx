// import React from 'react'  // React 17+ 不需要顯式導入
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import TaskListPage from './pages/TaskListPage'
import CreateTaskPage from './pages/CreateTaskPage'
import BlindTestPage from './pages/BlindTestPage'
import StatisticsPage from './pages/StatisticsPage'
import ResultsPage from './pages/ResultsPage'
import FolderManagePage from './pages/FolderManagePage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/folders" element={<FolderManagePage />} />
            <Route path="/tasks" element={<TaskListPage />} />
            <Route path="/tasks/create" element={<CreateTaskPage />} />
            <Route path="/tasks/:taskId/test" element={<BlindTestPage />} />
            <Route path="/tasks/:taskId/results" element={<ResultsPage />} />
            <Route path="/tasks/:taskId/statistics" element={<StatisticsPage />} />
          </Routes>
        </Layout>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              style: {
                background: '#059669',
              },
            },
            error: {
              duration: 4000,
              style: {
                background: '#dc2626',
              },
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App 