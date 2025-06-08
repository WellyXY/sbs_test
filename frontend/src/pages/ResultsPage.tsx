import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

interface TaskStatistics {
  task_id: string
  task_name: string
  folder_a: string
  folder_b: string
  total_pairs: number
  evaluated_pairs: number
  completion_rate: number
  a_wins: number
  b_wins: number
  ties: number
  a_win_percentage: number
  b_win_percentage: number
  tie_percentage: number
  evaluations: any[]
}

const ResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  
  const [statistics, setStatistics] = useState<TaskStatistics | null>(null)
  const [loading, setLoading] = useState(true)

  const loadStatistics = async () => {
    if (!taskId) return
    
    try {
      setLoading(true)
      console.log('🔧 DEBUG: 載入統計數據，任務ID:', taskId)
      
      const response = await fetch(`https://sbstest-production.up.railway.app/api/statistics/${taskId}`)
      console.log('🔧 DEBUG: 統計API響應狀態:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('🔧 DEBUG: 統計數據:', data)
        setStatistics(data)
      } else {
        console.error('❌ DEBUG: 載入統計失敗:', response.status)
        alert('載入統計數據失敗')
        navigate('/tasks')
      }
    } catch (error) {
      console.error('❌ DEBUG: 統計載入錯誤:', error)
      alert('網絡錯誤')
      navigate('/tasks')
    } finally {
      setLoading(false)
    }
  }

  const resetResults = async () => {
    if (!taskId) return
    
    const confirmReset = window.confirm('Are you sure you want to reset all test results for this task? This action cannot be undone.')
    if (!confirmReset) return
    
    try {
      console.log('🔧 DEBUG: 重置結果，任務ID:', taskId)
      
      const response = await fetch(`https://sbstest-production.up.railway.app/api/evaluations/reset/${taskId}`, {
        method: 'POST'
      })
      
      if (response.ok) {
        alert('Test results have been reset successfully')
        loadStatistics() // Reload statistics
      } else {
        alert('Failed to reset results')
      }
    } catch (error) {
      console.error('Reset error:', error)
      alert('Network error during reset')
    }
  }

  useEffect(() => {
    loadStatistics()
  }, [taskId])

  const getWinnerText = () => {
    if (!statistics) return ''
    
    if (statistics.a_wins > statistics.b_wins) {
      return `Folder "${statistics.folder_a}" wins!`
    } else if (statistics.b_wins > statistics.a_wins) {
      return `Folder "${statistics.folder_b}" wins!`
    } else {
      return 'It\'s a tie! Both folders performed equally'
    }
  }

  const getWinnerClass = () => {
    if (!statistics) return 'text-gray-600'
    
    if (statistics.a_wins > statistics.b_wins) {
      return 'text-blue-600'
    } else if (statistics.b_wins > statistics.a_wins) {
      return 'text-green-600'
    } else {
      return 'text-yellow-600'
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-lg">Loading statistics...</div>
        </div>
      </div>
    )
  }

  if (!statistics) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">
          <p>Unable to load statistics</p>
          <button 
            onClick={() => navigate('/tasks')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Back to Task List
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Title */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Test Results</h1>
          <h2 className="text-xl text-gray-600">{statistics.task_name}</h2>
        </div>
        <div className="space-x-4">
          <button
            onClick={() => navigate(`/tasks/${taskId}/test`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Continue Testing
          </button>
          <button
            onClick={resetResults}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Reset Results
          </button>
          <button
            onClick={() => navigate('/tasks')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Back to Task List
          </button>
        </div>
      </div>

      {/* Winner Announcement */}
      <div className="mb-8">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-6xl mb-4">🏆</div>
          <h2 className={`text-3xl font-bold mb-4 ${getWinnerClass()}`}>
            {getWinnerText()}
          </h2>
          <div className="text-gray-600">
            Based on {statistics.evaluated_pairs} evaluation results
          </div>
        </div>
      </div>

      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-sm text-gray-600 mb-1">Completion Rate</div>
          <div className="text-2xl font-bold text-gray-900">
            {statistics.completion_rate}%
          </div>
          <div className="text-sm text-gray-500">
            {statistics.evaluated_pairs} / {statistics.total_pairs}
          </div>
        </div>
        
        <div className="bg-blue-50 rounded-lg shadow-md p-6">
          <div className="text-sm text-blue-600 mb-1">{statistics.folder_a} wins</div>
          <div className="text-2xl font-bold text-blue-900">
            {statistics.a_wins} times
          </div>
          <div className="text-sm text-blue-600">
            {statistics.a_win_percentage}%
          </div>
        </div>
        
        <div className="bg-green-50 rounded-lg shadow-md p-6">
          <div className="text-sm text-green-600 mb-1">{statistics.folder_b} wins</div>
          <div className="text-2xl font-bold text-green-900">
            {statistics.b_wins} times
          </div>
          <div className="text-sm text-green-600">
            {statistics.b_win_percentage}%
          </div>
        </div>
        
        <div className="bg-yellow-50 rounded-lg shadow-md p-6">
          <div className="text-sm text-yellow-600 mb-1">Ties</div>
          <div className="text-2xl font-bold text-yellow-900">
            {statistics.ties} times
          </div>
          <div className="text-sm text-yellow-600">
            {statistics.tie_percentage}%
          </div>
        </div>
      </div>

      {/* Visualization Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Results Distribution Pie Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Evaluation Results Distribution</h3>
          <div className="flex justify-center">
            <div className="relative w-64 h-64">
              {/* Simple CSS Pie Chart */}
              <div 
                className="absolute inset-0 rounded-full border-8"
                style={{
                  background: `conic-gradient(
                    #3b82f6 0deg ${statistics.a_win_percentage * 3.6}deg,
                    #10b981 ${statistics.a_win_percentage * 3.6}deg ${(statistics.a_win_percentage + statistics.b_win_percentage) * 3.6}deg,
                    #f59e0b ${(statistics.a_win_percentage + statistics.b_win_percentage) * 3.6}deg 360deg
                  )`
                }}
              ></div>
              <div className="absolute inset-8 bg-white rounded-full flex items-center justify-center">
                <div className="text-center">
                  <div className="text-2xl font-bold">{statistics.evaluated_pairs}</div>
                  <div className="text-sm text-gray-600">Evaluations</div>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 space-y-2">
            <div className="flex items-center">
              <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
              <span className="text-sm">{statistics.folder_a}: {statistics.a_win_percentage}%</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
              <span className="text-sm">{statistics.folder_b}: {statistics.b_win_percentage}%</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
              <span className="text-sm">Ties: {statistics.tie_percentage}%</span>
            </div>
          </div>
        </div>

        {/* Comparison Bar Chart */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Win Count Comparison</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>{statistics.folder_a}</span>
                <span>{statistics.a_wins} times</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6">
                <div 
                  className="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-2"
                  style={{ width: `${statistics.a_win_percentage}%` }}
                >
                  {statistics.a_win_percentage > 20 && (
                    <span className="text-white text-xs font-semibold">
                      {statistics.a_win_percentage}%
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>{statistics.folder_b}</span>
                <span>{statistics.b_wins} times</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6">
                <div 
                  className="bg-green-500 h-6 rounded-full flex items-center justify-end pr-2"
                  style={{ width: `${statistics.b_win_percentage}%` }}
                >
                  {statistics.b_win_percentage > 20 && (
                    <span className="text-white text-xs font-semibold">
                      {statistics.b_win_percentage}%
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Ties</span>
                <span>{statistics.ties} times</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-6">
                <div 
                  className="bg-yellow-500 h-6 rounded-full flex items-center justify-end pr-2"
                  style={{ width: `${statistics.tie_percentage}%` }}
                >
                  {statistics.tie_percentage > 20 && (
                    <span className="text-white text-xs font-semibold">
                      {statistics.tie_percentage}%
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Information */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Test Details</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Task ID</div>
            <div className="font-mono text-xs">{statistics.task_id}</div>
          </div>
          <div>
            <div className="text-gray-600">Folder A</div>
            <div className="font-semibold">{statistics.folder_a}</div>
          </div>
          <div>
            <div className="text-gray-600">Folder B</div>
            <div className="font-semibold">{statistics.folder_b}</div>
          </div>
          <div>
            <div className="text-gray-600">Total Video Pairs</div>
            <div className="font-semibold">{statistics.total_pairs}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResultsPage 