import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

interface TaskStatistics {
  task_id: string
  task_name: string
  total_evaluations: number
  video_pairs_count: number
  completion_rate: number
  preferences: {
    a_better: number
    b_better: number
    tie: number
    a_better_percent: number
    b_better_percent: number
    tie_percent: number
  }
  folder_names: {
    folder_a: string
    folder_b: string
  }
}

const ResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const [statistics, setStatistics] = useState<TaskStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadStatistics = async () => {
    if (!taskId) return
    
    try {
      setLoading(true)
      console.log('🔧 DEBUG: Loading statistics data, task ID:', taskId)
      
      const response = await fetch(`https://sbstest-production.up.railway.app/api/statistics/${taskId}`)
      console.log('🔧 DEBUG: Statistics API response status:', response.status)
      
      if (response.ok) {
        const result = await response.json()
        console.log('🔧 DEBUG: Statistics data:', result)
        
        if (result.success && result.data) {
          setStatistics(result.data)
        } else {
          setError('Failed to load statistics data')
        }
      } else {
        setError('Statistics not found')
      }
    } catch (error) {
      console.error('❌ DEBUG: Statistics loading error:', error)
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  const resetResults = async () => {
    if (!taskId) return
    
    if (!confirm('Are you sure you want to reset all results for this task? This action cannot be undone.')) {
      return
    }
    
    try {
      console.log('🔧 DEBUG: Resetting results, task ID:', taskId)
      // This would call a reset API endpoint
      alert('Results reset functionality would be implemented here')
    } catch (error) {
      console.error('❌ DEBUG: Reset error:', error)
    }
  }

  useEffect(() => {
    loadStatistics()
  }, [taskId])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-lg">Loading statistics...</div>
        </div>
      </div>
    )
  }

  if (error || !statistics) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          <p>{error || 'Unable to load statistics'}</p>
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
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-3xl font-bold text-gray-900">Test Results</h1>
          <button
            onClick={() => navigate('/tasks')}
            className="text-gray-600 hover:text-gray-800"
          >
            ← Back to Task List
          </button>
        </div>
        <h2 className="text-xl text-gray-600">{statistics.task_name}</h2>
      </div>

      {/* Overall Statistics */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{statistics.total_evaluations}</div>
            <div className="text-sm text-gray-600">Total Evaluations</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{statistics.video_pairs_count}</div>
            <div className="text-sm text-gray-600">Video Pairs</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{statistics.completion_rate}%</div>
            <div className="text-sm text-gray-600">Completion Rate</div>
          </div>
        </div>
      </div>

      {/* Preference Results */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Preference Results</h3>
        <div className="space-y-4">
          {/* Folder A */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium">{statistics.folder_names.folder_a} (A) is Better</span>
              <span className="font-bold text-blue-600">
                {statistics.preferences.a_better} ({statistics.preferences.a_better_percent}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-blue-600 h-3 rounded-full transition-all"
                style={{ width: `${statistics.preferences.a_better_percent}%` }}
              ></div>
            </div>
          </div>

          {/* Folder B */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium">{statistics.folder_names.folder_b} (B) is Better</span>
              <span className="font-bold text-green-600">
                {statistics.preferences.b_better} ({statistics.preferences.b_better_percent}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-green-600 h-3 rounded-full transition-all"
                style={{ width: `${statistics.preferences.b_better_percent}%` }}
              ></div>
            </div>
          </div>

          {/* Tie */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium">About the Same</span>
              <span className="font-bold text-yellow-600">
                {statistics.preferences.tie} ({statistics.preferences.tie_percent}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-yellow-600 h-3 rounded-full transition-all"
                style={{ width: `${statistics.preferences.tie_percent}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => navigate(`/tasks/${taskId}/test`)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Test Again
        </button>
        <button
          onClick={resetResults}
          className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Reset Results
        </button>
      </div>
    </div>
  )
}

export default ResultsPage 