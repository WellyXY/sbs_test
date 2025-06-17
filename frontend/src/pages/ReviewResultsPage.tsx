import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, ArrowLeft } from 'lucide-react'

interface DetailedResult {
  pair_index: number
  pair_id: string
  video_a_path: string
  video_b_path: string
  video_a_name: string
  video_b_name: string
  left_folder: string
  right_folder: string
  is_swapped: boolean
  user_choice: 'A' | 'B' | 'tie' | null
  actual_chosen_folder: string | null
  evaluation_id: string | null
  evaluation_timestamp: string | null
  is_evaluated: boolean
}

interface DetailedResultsData {
  task_id: string
  task_name: string
  folder_a: string
  folder_b: string
  total_pairs: number
  evaluated_pairs: number
  completion_rate: number
  results: DetailedResult[]
}

const ReviewResultsPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  
  const [data, setData] = useState<DetailedResultsData | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const videoARef = useRef<HTMLVideoElement>(null)
  const videoBRef = useRef<HTMLVideoElement>(null)

  // Extract prompt from filename
  const extractPrompt = (filename: string): string => {
    let name = filename.replace(/\.(mp4|mov|avi|mkv|webm|flv|wmv|m4v|3gp|ts)$/i, '')
    name = name.replace(/^[a-f0-9]{8}_/i, '')
    name = name.replace(/_seed\d+.*$/i, '')
    name = name.replace(/_share$/i, '')
    name = name.replace(/_compressed$/i, '')
    name = name.replace(/_enhanced$/i, '')
    name = name.replace(/_final$/i, '')
    name = name.replace(/_/g, ' ').replace(/\s+/g, ' ').trim()
    return name.charAt(0).toUpperCase() + name.slice(1)
  }

  // Load detailed results
  const loadDetailedResults = async () => {
    if (!taskId) return
    
    try {
      setLoading(true)
      console.log('🔧 DEBUG: Loading detailed results, Task ID:', taskId)
      
      // First check evaluation data
      const evalResponse = await fetch(`https://sbstest-production.up.railway.app/api/evaluations/`)
      if (evalResponse.ok) {
        const evalResult = await evalResponse.json()
        console.log('🔧 DEBUG: All evaluation data:', evalResult)
        
        // Filter evaluations for current task
        const taskEvaluations = evalResult.data.filter((e: any) => e.video_pair_id.startsWith(taskId))
        console.log('🔧 DEBUG: Current task evaluations:', taskEvaluations)
      }
      
      const response = await fetch(`https://sbstest-production.up.railway.app/api/tasks/${taskId}/detailed-results`)
      console.log('🔧 DEBUG: Detailed results API response status:', response.status)
      
      if (response.ok) {
        const result = await response.json()
        console.log('🔧 DEBUG: Detailed results data:', result)
        
        if (result.success && result.data) {
          console.log('🔧 DEBUG: Setting detailed results data:', result.data)
          console.log('🔧 DEBUG: First result item:', result.data.results[0])
          setData(result.data)
        } else {
          setError('Unable to load detailed results')
        }
      } else {
        setError('Failed to load detailed results')
      }
    } catch (error) {
      console.error('❌ DEBUG: Detailed results loading error:', error)
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  // Get video URL
  const getVideoUrl = (path: string) => {
    if (!path.startsWith('uploads/')) {
      return `https://sbstest-production.up.railway.app/uploads/${path}`
    }
    return `https://sbstest-production.up.railway.app/${path}`
  }

  // Auto-play setup
  const setupAutoPlay = () => {
    setTimeout(() => {
      if (videoARef.current && videoBRef.current) {
        videoARef.current.loop = true
        videoBRef.current.loop = true
        videoARef.current.play().catch(() => {})
        videoBRef.current.play().catch(() => {})
      }
    }, 200)
  }

  // Sync time
  const handleTimeUpdate = (sourceVideo: HTMLVideoElement, targetVideo: HTMLVideoElement) => {
    const timeDiff = Math.abs(sourceVideo.currentTime - targetVideo.currentTime)
    if (timeDiff > 0.2) {
      targetVideo.currentTime = sourceVideo.currentTime
    }
  }

  // Navigation
  const goToPrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  const goToNext = () => {
    if (data && currentIndex < data.results.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const goToIndex = (index: number) => {
    if (data && index >= 0 && index < data.results.length) {
      setCurrentIndex(index)
    }
  }

  // Get choice color and text
  const getChoiceDisplay = (result: DetailedResult) => {
    console.log('🔧 DEBUG: getChoiceDisplay input:', {
      is_evaluated: result.is_evaluated,
      user_choice: result.user_choice,
      left_folder: result.left_folder,
      right_folder: result.right_folder,
      actual_chosen_folder: result.actual_chosen_folder
    })

    if (!result.is_evaluated || !result.user_choice) {
      return { text: 'Not evaluated', color: 'text-gray-500' }
    }

    if (result.user_choice === 'tie') {
      return { text: 'Tie (No preference)', color: 'text-yellow-600' }
    }

    const choiceText = result.user_choice === 'A' ? `Left (${result.left_folder})` : `Right (${result.right_folder})`
    
    if (result.actual_chosen_folder === data?.folder_a) {
      return { text: choiceText, color: 'text-blue-600' }
    } else {
      return { text: choiceText, color: 'text-green-600' }
    }
  }

  useEffect(() => {
    loadDetailedResults()
  }, [taskId])

  useEffect(() => {
    setupAutoPlay()
  }, [currentIndex])

  useEffect(() => {
    const videoA = videoARef.current
    const videoB = videoBRef.current

    if (videoA && videoB) {
      const syncAtoB = () => handleTimeUpdate(videoA, videoB)
      const syncBtoA = () => handleTimeUpdate(videoB, videoA)

      videoA.addEventListener('timeupdate', syncAtoB)
      videoB.addEventListener('timeupdate', syncBtoA)

      return () => {
        videoA.removeEventListener('timeupdate', syncAtoB)
        videoB.removeEventListener('timeupdate', syncBtoA)
      }
    }
  }, [currentIndex])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          <p>{error || 'Unable to load detailed results'}</p>
          <button 
            onClick={() => navigate(-1)}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  const currentResult = data.results[currentIndex]

  if (!currentResult) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">
          <p>No test results found</p>
          <button 
            onClick={() => navigate(-1)}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  const choiceDisplay = getChoiceDisplay(currentResult)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-700"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Results
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Review Test Results</h1>
        </div>
        <p className="text-gray-600">{data.task_name}</p>
      </div>

      {/* Progress */}
      <div className="mb-8 bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <span className="text-lg font-medium">Progress: {currentIndex + 1} / {data.total_pairs}</span>
          <span className="text-sm text-gray-500">Completion Rate: {data.evaluated_pairs} / {data.total_pairs} ({data.completion_rate}%)</span>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
            style={{ width: `${((currentIndex + 1) / data.total_pairs) * 100}%` }}
          ></div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button 
            onClick={goToPrevious}
            disabled={currentIndex === 0}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5" />
            Previous
          </button>

          {/* Page numbers */}
          <div className="flex gap-2">
            {data.results.map((_, index) => (
              <button
                key={index}
                onClick={() => goToIndex(index)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                  index === currentIndex
                    ? 'bg-blue-600 text-white'
                    : index < data.evaluated_pairs
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>

          <button 
            onClick={goToNext}
            disabled={currentIndex === data.total_pairs - 1}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Your Choice */}
      <div className="mb-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Your Choice</h2>
        <div className={`text-lg font-medium ${choiceDisplay.color}`}>
          {choiceDisplay.text}
        </div>
        <div className="text-sm text-gray-500 mt-2">
          Actual folder chosen: {currentResult.actual_chosen_folder || 'None'}
        </div>
      </div>

      {/* Video Pair */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">Video Pair #{currentResult.pair_index}</h3>
        <div className="text-sm text-gray-500 mb-6">
          Prompt: {extractPrompt(currentResult.video_a_name)}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Video (A) */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium">Left (A)</h4>
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                {currentResult.left_folder}
              </span>
            </div>
            <div className="aspect-video bg-black rounded-lg overflow-hidden">
              <video 
                ref={videoARef}
                controls 
                className="w-full h-full"
                src={getVideoUrl(currentResult.video_a_path)}
              >
                Your browser does not support the video tag.
              </video>
            </div>
            <p className="mt-2 text-sm text-gray-600">{currentResult.video_a_name}</p>
          </div>

          {/* Right Video (B) */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium">Right (B)</h4>
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                {currentResult.right_folder}
              </span>
            </div>
            <div className="aspect-video bg-black rounded-lg overflow-hidden">
              <video 
                ref={videoBRef}
                controls 
                className="w-full h-full"
                src={getVideoUrl(currentResult.video_b_path)}
              >
                Your browser does not support the video tag.
              </video>
            </div>
            <p className="mt-2 text-sm text-gray-600">{currentResult.video_b_name}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReviewResultsPage 