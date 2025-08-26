import axios from 'axios'
import { Task, VideoPair, Evaluation, FolderSelection, ApiResponse } from '../types'

// API 基本配置 - 强制HTTPS
const API_BASE_URL = 'https://sbstest-production.up.railway.app'
console.log('🔧 DEBUG: API_BASE_URL =', API_BASE_URL)
console.log('🔧 DEBUG: ENV =', import.meta.env.VITE_API_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  // 强制HTTPS，禁用HTTP重定向
  maxRedirects: 0,
})

// 請求攔截器
api.interceptors.request.use((config) => {
  console.log(`API 請求: ${config.method?.toUpperCase()} ${config.url}`)
  return config
})

// 響應攔截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 錯誤:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// 任務相關 API
export const taskApi = {
  // 獲取所有任務
  async getTasks(): Promise<Task[]> {
    const response = await api.get<ApiResponse<Task[]>>('/tasks')
    return response.data.data
  },

  // 獲取單個任務
  async getTask(taskId: string): Promise<Task> {
    const response = await api.get<ApiResponse<Task>>(`/tasks/${taskId}`)
    return response.data.data
  },

  // 創建新任務
  async createTask(data: {
    name: string
    folder_a_path: string
    folder_b_path: string
  }): Promise<Task> {
    const response = await api.post<ApiResponse<Task>>('/tasks', data)
    return response.data.data
  },

  // 更新任務
  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    const response = await api.put<ApiResponse<Task>>(`/tasks/${taskId}`, updates)
    return response.data.data
  },

  // 刪除任務
  async deleteTask(taskId: string): Promise<void> {
    await api.delete(`/tasks/${taskId}`)
  },

  // 獲取任務的視頻對
  async getVideoPairs(taskId: string): Promise<VideoPair[]> {
    const response = await api.get<ApiResponse<VideoPair[]>>(`/tasks/${taskId}/video-pairs`)
    return response.data.data
  },
}

// 文件夾相關 API
export const folderApi = {
  // 掃描文件夾中的視頻文件
  async scanFolder(folderPath: string): Promise<FolderSelection> {
    const response = await api.post<ApiResponse<FolderSelection>>('/folders/scan', {
      path: folderPath
    })
    return response.data.data
  },

  // 匹配兩個文件夾中的視頻文件
  async matchVideos(folderAPath: string, folderBPath: string): Promise<{
    matched_pairs: Array<{
      video_a: string
      video_b: string
      name: string
    }>
    unmatched_a: string[]
    unmatched_b: string[]
  }> {
    const response = await api.post('/folders/match', {
      folder_a_path: folderAPath,
      folder_b_path: folderBPath
    })
    return response.data.data
  },
}

// 評估相關 API
export const evaluationApi = {
  // 提交評估結果
  async submitEvaluation(data: {
    video_pair_id: string
    choice: 'A' | 'B' | 'tie' | null
    score_a: number
    score_b: number
    comments: string
    is_blind: boolean
    randomized_order: boolean
  }): Promise<Evaluation> {
    const response = await api.post<ApiResponse<Evaluation>>('/evaluations', data)
    return response.data.data
  },

  // 獲取任務的評估統計
  async getTaskStatistics(taskId: string): Promise<{
    total_evaluations: number
    preference_a: number
    preference_b: number
    ties: number
    average_score_a: number
    average_score_b: number
    completion_rate: number
  }> {
    const response = await api.get(`/tasks/${taskId}/statistics`)
    return response.data.data
  },

  // 導出評估結果
  async exportResults(taskId: string, format: 'csv' | 'excel'): Promise<Blob> {
    const response = await api.get(`/tasks/${taskId}/export?format=${format}`, {
      responseType: 'blob'
    })
    return response.data
  },
}

// 系統相關 API
export const systemApi = {
  // 檢查系統狀態
  async getHealth(): Promise<{ status: string; version: string }> {
    const response = await api.get<{ status: string; version: string }>('/health')
    return response.data
  },

  // 獲取支持的視頻格式
  async getSupportedFormats(): Promise<string[]> {
    const response = await api.get<ApiResponse<string[]>>('/api/formats')
    return response.data.data
  },
} 