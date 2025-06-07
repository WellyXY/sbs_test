// 任務相關類型
export interface Task {
  id: string
  name: string
  status: 'pending' | 'in_progress' | 'completed'
  created_at: string
  updated_at: string
  folder_a_path: string
  folder_b_path: string
  video_pairs: VideoPair[]
  total_pairs: number
  completed_pairs: number
}

// 視頻對類型
export interface VideoPair {
  id: string
  task_id: string
  video_a_path: string
  video_b_path: string
  video_a_name: string
  video_b_name: string
  is_evaluated: boolean
  evaluation?: Evaluation
}

// 評估結果類型
export interface Evaluation {
  id: string
  video_pair_id: string
  user_id?: string
  choice: 'A' | 'B' | 'tie' | null
  score_a: number
  score_b: number
  comments: string
  created_at: string
  is_blind: boolean
  randomized_order: boolean
}

// 用戶類型
export interface User {
  id: string
  name: string
  email?: string
  created_at: string
}

// API 響應類型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

// 文件夾選擇類型
export interface FolderSelection {
  path: string
  name: string
  video_count: number
  video_files: string[]
}

// 播放器狀態類型
export interface PlayerState {
  playing: boolean
  currentTime: number
  duration: number
  volume: number
  muted: boolean
  playbackRate: number
}

// 盲測設置類型
export interface BlindTestSettings {
  is_blind: boolean
  randomize_order: boolean
  show_progress: boolean
  auto_advance: boolean
}

// 統計數據類型
export interface Statistics {
  total_evaluations: number
  preference_a: number
  preference_b: number
  ties: number
  average_score_a: number
  average_score_b: number
  completion_rate: number
} 