import { create } from 'zustand'
import { Task, VideoPair, Evaluation, BlindTestSettings } from '../types'

interface TaskState {
  // 當前任務相關
  tasks: Task[]
  currentTask: Task | null
  currentVideoPair: VideoPair | null
  currentPairIndex: number
  
  // 盲測設置
  blindTestSettings: BlindTestSettings
  
  // 加載狀態
  isLoading: boolean
  error: string | null
  
  // Actions
  setTasks: (tasks: Task[]) => void
  setCurrentTask: (task: Task | null) => void
  setCurrentVideoPair: (pair: VideoPair | null) => void
  setCurrentPairIndex: (index: number) => void
  setBlindTestSettings: (settings: BlindTestSettings) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  
  // 任務操作
  addTask: (task: Task) => void
  updateTask: (taskId: string, updates: Partial<Task>) => void
  deleteTask: (taskId: string) => void
  
  // 評估操作
  submitEvaluation: (evaluation: Evaluation) => void
  nextVideoPair: () => void
  previousVideoPair: () => void
  
  // 重置狀態
  reset: () => void
}

export const useTaskStore = create<TaskState>((set, get) => ({
  // 初始狀態
  tasks: [],
  currentTask: null,
  currentVideoPair: null,
  currentPairIndex: 0,
  blindTestSettings: {
    is_blind: true,
    randomize_order: true,
    show_progress: true,
    auto_advance: false,
  },
  isLoading: false,
  error: null,

  // 基本設置方法
  setTasks: (tasks) => set({ tasks }),
  setCurrentTask: (task) => set({ currentTask: task, currentPairIndex: 0 }),
  setCurrentVideoPair: (pair) => set({ currentVideoPair: pair }),
  setCurrentPairIndex: (index) => set({ currentPairIndex: index }),
  setBlindTestSettings: (settings) => set({ blindTestSettings: settings }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),

  // 任務操作
  addTask: (task) => set((state) => ({ tasks: [...state.tasks, task] })),
  
  updateTask: (taskId, updates) => set((state) => ({
    tasks: state.tasks.map(task => 
      task.id === taskId ? { ...task, ...updates } : task
    ),
    currentTask: state.currentTask?.id === taskId 
      ? { ...state.currentTask, ...updates } 
      : state.currentTask
  })),
  
  deleteTask: (taskId) => set((state) => ({
    tasks: state.tasks.filter(task => task.id !== taskId),
    currentTask: state.currentTask?.id === taskId ? null : state.currentTask
  })),

  // 評估操作
  submitEvaluation: (evaluation) => {
    const { currentTask, currentPairIndex } = get()
    if (!currentTask) return

    // 更新當前視頻對的評估狀態
    const updatedVideoPairs = currentTask.video_pairs.map((pair, index) => 
      index === currentPairIndex 
        ? { ...pair, is_evaluated: true, evaluation }
        : pair
    )

    // 計算完成的對數
    const completedPairs = updatedVideoPairs.filter(pair => pair.is_evaluated).length

    // 更新任務
    const updatedTask = {
      ...currentTask,
      video_pairs: updatedVideoPairs,
      completed_pairs: completedPairs,
      status: completedPairs === currentTask.total_pairs ? 'completed' as const : 'in_progress' as const
    }

    set((state) => ({
      tasks: state.tasks.map(task => 
        task.id === currentTask.id ? updatedTask : task
      ),
      currentTask: updatedTask,
      currentVideoPair: updatedVideoPairs[currentPairIndex]
    }))
  },

  nextVideoPair: () => {
    const { currentTask, currentPairIndex } = get()
    if (!currentTask || currentPairIndex >= currentTask.video_pairs.length - 1) return

    const nextIndex = currentPairIndex + 1
    set({
      currentPairIndex: nextIndex,
      currentVideoPair: currentTask.video_pairs[nextIndex]
    })
  },

  previousVideoPair: () => {
    const { currentTask, currentPairIndex } = get()
    if (!currentTask || currentPairIndex <= 0) return

    const prevIndex = currentPairIndex - 1
    set({
      currentPairIndex: prevIndex,
      currentVideoPair: currentTask.video_pairs[prevIndex]
    })
  },

  // 重置狀態
  reset: () => set({
    tasks: [],
    currentTask: null,
    currentVideoPair: null,
    currentPairIndex: 0,
    isLoading: false,
    error: null,
  }),
})) 