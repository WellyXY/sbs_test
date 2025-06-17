// API配置文件 - 根據部署環境自動選擇正確的API URL

// 檢查當前域名來決定API URL
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // 如果在Vercel上運行，使用Railway後端
    if (hostname.includes('vercel.app')) {
      return 'https://sbstest-production.up.railway.app';
    }
    
    // 如果在localhost運行，使用本地後端
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    
    // 默認使用Railway後端
    return 'https://sbstest-production.up.railway.app';
  }
  
  // 服務端渲染時的默認值
  return 'https://sbstest-production.up.railway.app';
};

export const API_BASE_URL = getApiUrl();

// 導出常用的API端點
export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/health`,
  TASKS: `${API_BASE_URL}/api/tasks`,
  EVALUATIONS: `${API_BASE_URL}/api/evaluations`,
  FOLDERS: `${API_BASE_URL}/api/folders`,
  STATISTICS: `${API_BASE_URL}/api/statistics`,
  DEBUG: `${API_BASE_URL}/api/debug`
} as const;

// 輔助函數：構建完整的文件URL
export const buildFileUrl = (path: string): string => {
  if (path.startsWith('http')) {
    return path; // 如果已經是完整URL，直接返回
  }
  
  // 確保路徑以正確的格式開始
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  if (cleanPath.startsWith('uploads/')) {
    return `${API_BASE_URL}/${cleanPath}`;
  } else {
    return `${API_BASE_URL}/uploads/${cleanPath}`;
  }
};

// 調試函數：輸出當前配置
export const logApiConfig = () => {
  if (typeof window !== 'undefined') {
    console.log('🔧 API Configuration:', {
      hostname: window.location.hostname,
      apiUrl: API_BASE_URL,
      endpoints: API_ENDPOINTS
    });
  }
}; 