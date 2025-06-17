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
      console.log('🔧 DEBUG: 載入詳細結果，任務ID:', taskId)
      
      // 先檢查評估數據
      const evalResponse = await fetch(`https://sbstest-production.up.railway.app/api/evaluations/`)
      if (evalResponse.ok) {
        const evalResult = await evalResponse.json()
        console.log('🔧 DEBUG: 所有評估數據:', evalResult)
        
        // 過濾出當前任務的評估
        const taskEvaluations = evalResult.data.filter((e: any) => e.video_pair_id.startsWith(taskId))
        console.log('🔧 DEBUG: 當前任務的評估:', taskEvaluations)
      }
      
      const response = await fetch(`https://sbstest-production.up.railway.app/api/tasks/${taskId}/detailed-results`)
      console.log('🔧 DEBUG: 詳細結果API響應狀態:', response.status)
      
      if (response.ok) {
        const result = await response.json()
        console.log('🔧 DEBUG: 詳細結果數據:', result)
        
        if (result.success && result.data) {
          console.log('🔧 DEBUG: 設置詳細結果數據:', result.data)
          console.log('🔧 DEBUG: 第一個結果項目:', result.data.results[0])
          setData(result.data)
        } else {
          setError('無法載入詳細結果')
        }
      } else {
        setError('載入詳細結果失敗')
      }
    } catch (error) {
      console.error('❌ DEBUG: 詳細結果載入錯誤:', error)
      setError('網絡錯誤')
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
      return { text: '未評估', color: 'text-gray-500', bgColor: 'bg-gray-100' }
    }

    if (result.user_choice === 'tie') {
      return { text: '平手', color: 'text-yellow-700', bgColor: 'bg-yellow-100' }
    }

    const choiceText = result.user_choice === 'A' ? `選擇左側 (${result.left_folder})` : `選擇右側 (${result.right_folder})`
    
    if (result.actual_chosen_folder === data?.folder_a) {
      return { text: choiceText, color: 'text-blue-700', bgColor: 'bg-blue-100' }
    } else {
      return { text: choiceText, color: 'text-green-700', bgColor: 'bg-green-100' }
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
          <div className="text-lg">載入詳細結果中...</div>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          <p>{error || '無法載入詳細結果'}</p>
          <button 
            onClick={() => navigate(`/tasks/${taskId}/results`)}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            返回結果頁面
          </button>
        </div>
      </div>
    )
  }

  const currentResult = data.results[currentIndex]

  if (!currentResult) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center text-red-600">
          <p>沒有找到結果數據</p>
          <button 
            onClick={() => navigate(`/tasks/${taskId}/results`)}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            返回結果頁面
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
        <div className="flex justify-between items-center mb-2">
          <h1 className="text-3xl font-bold text-gray-900">查看測試結果</h1>
          <button
            onClick={() => navigate(`/tasks/${taskId}/results`)}
            className="flex items-center text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-5 h-5 mr-1" />
            返回結果頁面
          </button>
        </div>
        <h2 className="text-xl text-gray-600">{data.task_name}</h2>
      </div>

      {/* Progress */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">進度: {currentIndex + 1} / {data.total_pairs}</h3>
          <div className="text-sm text-gray-500">
            評估完成: {data.evaluated_pairs} / {data.total_pairs} ({data.completion_rate}%)
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${((currentIndex + 1) / data.total_pairs) * 100}%` }}
          ></div>
        </div>

        {/* Navigation buttons */}
        <div className="flex justify-between items-center">
          <button
            onClick={goToPrevious}
            disabled={currentIndex === 0}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            上一個
          </button>

          <div className="flex space-x-2">
            {data.results.map((_, index) => (
              <button
                key={index}
                onClick={() => goToIndex(index)}
                className={`w-8 h-8 rounded-full text-sm font-medium ${
                  index === currentIndex 
                    ? 'bg-blue-600 text-white' 
                    : data.results[index].is_evaluated
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
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一個
            <ChevronRight className="w-5 h-5 ml-1" />
          </button>
        </div>
      </div>

      {/* Choice result */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">您的選擇</h3>
        <div className={`inline-flex items-center px-4 py-2 rounded-lg ${choiceDisplay.bgColor}`}>
          <span className={`font-medium ${choiceDisplay.color}`}>
            {choiceDisplay.text}
          </span>
        </div>
        {currentResult.is_evaluated && currentResult.user_choice !== 'tie' && (
          <div className="mt-2 text-sm text-gray-600">
            實際選擇的資料夾: <span className="font-medium">{currentResult.actual_chosen_folder}</span>
          </div>
        )}
      </div>

      {/* Video comparison */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold">視頻對比 #{currentResult.pair_index}</h3>
          <p className="text-sm text-gray-600 mt-1">
            提示詞: {extractPrompt(currentResult.video_a_name)}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Video A */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h4 className="font-medium text-gray-900">左側 (A)</h4>
              <span className="text-sm px-2 py-1 bg-blue-100 text-blue-700 rounded">
                {currentResult.left_folder}
              </span>
            </div>
            <div className="aspect-video bg-black rounded-lg overflow-hidden">
              <video
                ref={videoARef}
                className="w-full h-full object-contain"
                controls
                muted
                playsInline
                src={getVideoUrl(currentResult.video_a_path)}
                onError={(e) => {
                  console.error('Video A load error:', e)
                }}
              >
                您的瀏覽器不支持視頻播放
              </video>
            </div>
            <p className="text-xs text-gray-500 break-all">
              {currentResult.video_a_name}
            </p>
          </div>

          {/* Video B */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h4 className="font-medium text-gray-900">右側 (B)</h4>
              <span className="text-sm px-2 py-1 bg-green-100 text-green-700 rounded">
                {currentResult.right_folder}
              </span>
            </div>
            <div className="aspect-video bg-black rounded-lg overflow-hidden">
              <video
                ref={videoBRef}
                className="w-full h-full object-contain"
                controls
                muted
                playsInline
                src={getVideoUrl(currentResult.video_b_path)}
                onError={(e) => {
                  console.error('Video B load error:', e)
                }}
              >
                您的瀏覽器不支持視頻播放
              </video>
            </div>
            <p className="text-xs text-gray-500 break-all">
              {currentResult.video_b_name}
            </p>
          </div>
        </div>

        {/* Metadata */}
        {currentResult.evaluation_timestamp && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              評估時間: {new Date(currentResult.evaluation_timestamp).toLocaleString('zh-TW')}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ReviewResultsPage 