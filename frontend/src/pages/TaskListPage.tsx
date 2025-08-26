import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Play, BarChart3, Trash2, Clock, CheckCircle } from 'lucide-react'

interface Task {
  id: string;
  name: string;
  description?: string;
  folder_a: string;
  folder_b: string;
  is_blind: boolean;
  status: string;
  video_pairs_count: number;
  completed_pairs: number;
  created_time: number;
  updated_time: number;
}

const TaskListPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)

  // Load task list
  const loadTasks = async () => {
    try {
      setLoading(true)
      console.log('🔧 DEBUG: Loading task list...')
      
      const response = await fetch('https://sbstest-production.up.railway.app/api/tasks')
      console.log('🔧 DEBUG: API response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('🔧 DEBUG: Task data:', data)
        
        if (data.success && data.data) {
          setTasks(data.data)
          console.log('✅ DEBUG: Successfully loaded', data.data.length, 'tasks')
        } else {
          console.error('❌ DEBUG: API response format error:', data)
        }
      } else {
        console.error('❌ DEBUG: API request failed:', response.status)
      }
    } catch (error) {
      console.error('❌ DEBUG: Task loading error:', error)
    } finally {
      setLoading(false)
    }
  }

  // Delete task
  const deleteTask = async (taskId: string, taskName: string) => {
    if (!confirm(`Are you sure you want to delete task "${taskName}"? This action cannot be undone.`)) return

    try {
      console.log('🔧 DEBUG: Deleting task:', taskId)
      
      const response = await fetch(`https://sbstest-production.up.railway.app/api/tasks/${taskId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        await loadTasks()
        alert('Task deletion successful')
      } else {
        const error = await response.json()
        alert(error.detail || 'Deletion failed')
      }
    } catch (error) {
      console.error('❌ DEBUG: Task deletion error:', error)
      alert('Deletion failed')
    }
  }

  // Format date
  const formatDate = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleString('en-US')
  }

  // Get status display
  const getStatusDisplay = (status: string) => {
    const statusMap = {
      'created': { text: 'Created', color: 'bg-gray-100 text-gray-800' },
      'in_progress': { text: 'In Progress', color: 'bg-blue-100 text-blue-800' },
      'completed': { text: 'Completed', color: 'bg-green-100 text-green-800' },
      'paused': { text: 'Paused', color: 'bg-yellow-100 text-yellow-800' },
    }
    return statusMap[status as keyof typeof statusMap] || { text: status, color: 'bg-gray-100 text-gray-800' }
  }

  // Calculate progress percentage
  const getProgress = (completed: number, total: number): number => {
    return total > 0 ? Math.round((completed / total) * 100) : 0
  }

  useEffect(() => {
    loadTasks()
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Task List</h1>
          <p className="mt-2 text-gray-600">Manage your video comparison testing tasks</p>
        </div>
        <Link
          to="/tasks/create"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <span className="mr-2">➕</span>
          Create Task
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-md">
        {loading ? (
          <div className="p-8 text-center">
            <div className="text-gray-500">Loading...</div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-gray-500 mb-4">
              <span className="text-6xl">📋</span>
              <p className="text-lg mt-2">No tasks created yet</p>
              <p className="text-sm">Create your first video comparison testing task</p>
            </div>
            <Link
              to="/tasks/create"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <span className="mr-2">➕</span>
              Create Task
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Task Info
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Folders
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created Time
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tasks.map((task) => {
                  const statusInfo = getStatusDisplay(task.status)
                  const progress = getProgress(task.completed_pairs, task.video_pairs_count)
                  
                  return (
                    <tr key={task.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="max-w-xs">
                          <div className="text-sm font-medium text-gray-900 truncate" title={task.name}>
                            {task.name}
                          </div>
                          {task.description && (
                            <div className="text-sm text-gray-500">{task.description}</div>
                          )}
                          <div className="text-xs text-gray-400 mt-1">
                            {task.is_blind ? '🔒 Blind Mode' : '👁️ Non-blind'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <div className="flex items-center mb-1">
                            <span className="text-blue-600 mr-1">A:</span>
                            {task.folder_a}
                          </div>
                          <div className="flex items-center">
                            <span className="text-green-600 mr-1">B:</span>
                            {task.folder_b}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {task.completed_pairs}/{task.video_pairs_count} pairs
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${progress}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">{progress}%</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.color}`}>
                          {statusInfo.text}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(task.created_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end space-x-2">
                          <Link
                            to={`/tasks/${task.id}/test`}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Start Test
                          </Link>
                          <Link
                            to={`/tasks/${task.id}/results`}
                            className="text-green-600 hover:text-green-900"
                          >
                            View Results
                          </Link>
                          <button
                            onClick={() => deleteTask(task.id, task.name)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default TaskListPage 