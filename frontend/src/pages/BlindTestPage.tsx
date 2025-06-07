import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

interface VideoPair {
  id: string
  task_id: string
  video_a_path: string
  video_b_path: string
  video_a_name: string
  video_b_name: string
  is_evaluated: boolean
  evaluation?: any
}

interface Task {
  id: string
  name: string
  status: string
  folder_a: string
  folder_b: string
  video_pairs_count: number
  is_blind: boolean
  video_pairs?: VideoPair[]
}

const BlindTestPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  
  const [task, setTask] = useState<Task | null>(null)
  const [currentPairIndex, setCurrentPairIndex] = useState(0)
  const [currentPair, setCurrentPair] = useState<VideoPair | null>(null)
  const [choice, setChoice] = useState<'A' | 'B' | 'tie' | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  
  const videoARef = useRef<HTMLVideoElement>(null)
  const videoBRef = useRef<HTMLVideoElement>(null)

  // Extract prompt from filename
  const extractPrompt = (filename: string): string => {
    // Remove file extension
    let name = filename.replace(/\.(mp4|mov|avi|mkv|webm|flv|wmv|m4v|3gp|ts)$/i, '')
    
    // Remove common prefixes
    name = name.replace(/^[a-f0-9]{8}_/i, '') // Remove 8-character hex prefix
    
    // Remove common suffixes
    name = name.replace(/_seed\d+.*$/i, '') // Remove _seed and everything after
    name = name.replace(/_share$/i, '') // Remove _share
    name = name.replace(/_compressed$/i, '') // Remove _compressed
    name = name.replace(/_enhanced$/i, '') // Remove _enhanced
    name = name.replace(/_final$/i, '') // Remove _final
    
    // Replace underscores with spaces and clean up
    name = name.replace(/_/g, ' ').replace(/\s+/g, ' ').trim()
    
    // Capitalize first letter
    return name.charAt(0).toUpperCase() + name.slice(1)
  }

  // Load task data
  const loadTask = async () => {
    if (!taskId) return
    
    try {
      setLoading(true)
      const response = await fetch(`/api/tasks/${taskId}`)
      
      if (response.ok) {
        const taskData = await response.json()
        setTask(taskData)
        
        if (taskData.video_pairs && taskData.video_pairs.length > 0) {
          setCurrentPair(taskData.video_pairs[0])
        }
      } else {
        alert('Failed to load task')
        navigate('/tasks')
      }
    } catch (error) {
      console.error('Task loading error:', error)
      alert('Network error')
      navigate('/tasks')
    } finally {
      setLoading(false)
    }
  }

  // Auto-play and loop setup
  const setupAutoPlay = () => {
    setTimeout(() => {
      if (videoARef.current && videoBRef.current) {
        // Set loop
        videoARef.current.loop = true
        videoBRef.current.loop = true
        
        // Try auto-play
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

  // Submit evaluation with automatic navigation
  const submitEvaluation = async (selectedChoice: 'A' | 'B' | 'tie') => {
    if (!currentPair || submitting) {
      return
    }

    try {
      setSubmitting(true)
      console.log('Submitting evaluation:', { video_pair_id: currentPair.id, choice: selectedChoice })
      
      const response = await fetch('/api/evaluations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_pair_id: currentPair.id,
          choice: selectedChoice,
          is_blind: task?.is_blind || false
        }),
      })

      console.log('Response status:', response.status)
      
      if (response.ok) {
        const responseData = await response.json()
        console.log('Evaluation submitted successfully:', responseData)
        
        // Check if there's a next pair
        if (task && task.video_pairs && currentPairIndex < task.video_pairs.length - 1) {
          console.log('Moving to next pair automatically')
          // Immediately go to next pair
          const nextIndex = currentPairIndex + 1
          setCurrentPairIndex(nextIndex)
          setCurrentPair(task.video_pairs[nextIndex])
          setChoice(null)
          // Setup auto-play for new videos
          setTimeout(setupAutoPlay, 300)
        } else {
          console.log('Test completed, redirecting to results')
          // Test completed, go to results page
          navigate(`/tasks/${taskId}/results`)
        }
      } else {
        const errorData = await response.json()
        console.error('Evaluation submission failed:', errorData)
        alert(`Evaluation submission failed: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Evaluation submission error:', error)
      alert('Network error: Unable to submit evaluation')
    } finally {
      setSubmitting(false)
    }
  }

  // Handle evaluation button clicks
  const handleEvaluationClick = (selectedChoice: 'A' | 'B' | 'tie') => {
    submitEvaluation(selectedChoice)
  }

  // Go to next pair
  const goToNextPair = () => {
    if (!task || !task.video_pairs) {
      console.log('Cannot navigate: task or video_pairs not available')
      return
    }
    
    const nextIndex = currentPairIndex + 1
    console.log('Attempting to go to next pair:', { currentIndex: currentPairIndex, nextIndex, totalPairs: task.video_pairs.length })
    
    if (nextIndex < task.video_pairs.length) {
      console.log('Navigating to next pair:', task.video_pairs[nextIndex])
      setCurrentPairIndex(nextIndex)
      setCurrentPair(task.video_pairs[nextIndex])
      setChoice(null)
      
      // Setup auto-play for new videos
      setTimeout(setupAutoPlay, 300)
    } else {
      console.log('Already at last pair, cannot navigate further')
    }
  }

  // Go to previous pair
  const goToPreviousPair = () => {
    if (!task || !task.video_pairs) return
    
    const prevIndex = currentPairIndex - 1
    if (prevIndex >= 0) {
      setCurrentPairIndex(prevIndex)
      setCurrentPair(task.video_pairs[prevIndex])
      setChoice(null)
      
      // Setup auto-play for new videos
      setTimeout(setupAutoPlay, 300)
    }
  }

  // Get video URL
  const getVideoUrl = (path: string) => {
    return `http://localhost:8000/${path}`
  }

  useEffect(() => {
    loadTask()
  }, [taskId])

  // Setup auto-play when current pair changes
  useEffect(() => {
    if (currentPair) {
      console.log('Current pair changed:', currentPair)
      setupAutoPlay()
    }
  }, [currentPair])

  // Video sync event handling
  useEffect(() => {
    const videoA = videoARef.current
    const videoB = videoBRef.current
    
    if (!videoA || !videoB || !currentPair) return

    const syncAtoB = () => handleTimeUpdate(videoA, videoB)
    const syncBtoA = () => handleTimeUpdate(videoB, videoA)
    
    videoA.addEventListener('timeupdate', syncAtoB)
    videoB.addEventListener('timeupdate', syncBtoA)
    
    return () => {
      videoA.removeEventListener('timeupdate', syncAtoB)
      videoB.removeEventListener('timeupdate', syncBtoA)
    }
  }, [currentPair])

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    )
  }

  if (!task || !currentPair) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">
          <p>Unable to load test data</p>
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

  const promptText = extractPrompt(currentPair.video_a_name)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Title and Progress */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-3xl font-bold text-gray-900">{task.name}</h1>
          <button
            onClick={() => navigate('/tasks')}
            className="text-gray-600 hover:text-gray-800"
          >
            ← Back to Task List
          </button>
        </div>
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {task.is_blind ? '🔒 Blind Test Mode' : '👁️ Non-blind Mode'}
          </div>
          <div className="text-sm text-gray-600">
            Pair {currentPairIndex + 1} / {task.video_pairs_count}
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${((currentPairIndex + 1) / task.video_pairs_count) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Prompt Display */}
      <div className="mb-6 text-center">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-blue-900 mb-2">Prompt</h2>
          <p className="text-blue-800 text-base leading-relaxed">{promptText}</p>
        </div>
      </div>

      {/* Video Player Area */}
      <div className="bg-gray-900 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="relative">
            <div className="text-white text-center mb-2 font-medium">
              Video A
            </div>
            <video
              key={`video-a-${currentPair.id}`}
              ref={videoARef}
              className="w-full h-80 bg-black rounded"
              controls
              muted
              playsInline
              src={getVideoUrl(currentPair.video_a_path)}
            >
              Your browser does not support video playback
            </video>
          </div>
          
          <div className="relative">
            <div className="text-white text-center mb-2 font-medium">
              Video B
            </div>
            <video
              key={`video-b-${currentPair.id}`}
              ref={videoBRef}
              className="w-full h-80 bg-black rounded"
              controls
              muted
              playsInline
              src={getVideoUrl(currentPair.video_b_path)}
            >
              Your browser does not support video playback
            </video>
          </div>
        </div>
      </div>

      {/* Evaluation Area */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-6 text-center">Please select which video you think has better quality</h3>
        
        <div className="space-y-6">
          <div className="flex justify-center space-x-6">
            <button
              onClick={() => handleEvaluationClick('A')}
              disabled={submitting}
              className={`px-8 py-4 rounded-lg font-medium text-lg transition-all ${
                submitting
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg'
              }`}
            >
              {submitting ? 'Submitting...' : 'A is Better'}
            </button>
            <button
              onClick={() => handleEvaluationClick('tie')}
              disabled={submitting}
              className={`px-8 py-4 rounded-lg font-medium text-lg transition-all ${
                submitting
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-yellow-500 text-white hover:bg-yellow-600 hover:shadow-lg'
              }`}
            >
              {submitting ? 'Submitting...' : 'About the Same'}
            </button>
            <button
              onClick={() => handleEvaluationClick('B')}
              disabled={submitting}
              className={`px-8 py-4 rounded-lg font-medium text-lg transition-all ${
                submitting
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700 hover:shadow-lg'
              }`}
            >
              {submitting ? 'Submitting...' : 'B is Better'}
            </button>
          </div>

          <div className="flex justify-center items-center pt-6">
            <button
              onClick={goToPreviousPair}
              disabled={currentPairIndex === 0 || submitting}
              className={`px-6 py-3 rounded-lg font-medium ${
                currentPairIndex === 0 || submitting
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              ← Previous Pair
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BlindTestPage 