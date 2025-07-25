import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
// Debug: 檢查API連接
console.log('🔧 DEBUG: FolderManagePage 載入，準備測試API連接...');

// 直接使用Railway API配置
const API_BASE_URL = 'https://sbstest-production.up.railway.app';
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 測試API連接
api.get('/api/health')
  .then(response => {
    console.log('✅ DEBUG: API連接成功！', response.data);
  })
  .catch(error => {
    console.error('❌ DEBUG: API連接失敗！', error);
  });

// 暫時使用 emoji 圖標，稍後添加 heroicons
const FolderIcon = ({ className, ...props }: any) => <span className={className} {...props}>📁</span>;
const VideoCameraIcon = ({ className, ...props }: any) => <span className={className} {...props}>🎥</span>;
const PlusIcon = ({ className, ...props }: any) => <span className={className} {...props}>➕</span>;
const TrashIcon = ({ className, ...props }: any) => <span className={className} {...props}>🗑️</span>;
const CloudArrowUpIcon = ({ className, ...props }: any) => <span className={className} {...props}>⬆️</span>;
const DocumentIcon = ({ className, ...props }: any) => <span className={className} {...props}>📄</span>;
const XMarkIcon = ({ className, ...props }: any) => <span className={className} {...props}>❌</span>;

interface Folder {
  name: string;
  path: string;
  video_count: number;
  total_size: number;
  created_time: number;
}

interface FileInfo {
  filename: string;
  size: number;
  path: string;
  created_time: number;
}

const FolderManagePage: React.FC = () => {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [folderFiles, setFolderFiles] = useState<FileInfo[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentUploadFile, setCurrentUploadFile] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 加載資料夾列表
  const loadFolders = async () => {
    try {
      setLoading(true);
      console.log('🔧 DEBUG: 開始載入資料夾列表...');
      
      const response = await api.get('/api/folders/');
      console.log('🔧 DEBUG: 資料夾API響應:', response.data);
      
      if (response.data.success) {
        setFolders(response.data.data);
        console.log('🔧 DEBUG: 資料夾列表載入完成');
      } else {
        console.error('❌ DEBUG: 載入資料夾失敗:', response.data.error);
      }
      
    } catch (error) {
      console.error('❌ DEBUG: 資料夾載入錯誤:', error);
      alert('無法連接到服務器，請檢查網絡連接');
    } finally {
      setLoading(false);
    }
  };

  // 創建新資料夾
  const createFolder = async () => {
    if (!newFolderName.trim()) return;
    
    try {
      setCreating(true);
      console.log('🔧 DEBUG: 創建資料夾:', newFolderName);
      
      const response = await api.post('/api/folders/create', {
          name: newFolderName.trim()
      });

      console.log('🔧 DEBUG: 創建資料夾響應:', response.data);
      
      if (response.data.success) {
        setNewFolderName('');
        setShowCreateModal(false);
        alert(response.data.message || '資料夾創建成功！');
        await loadFolders();
      } else {
        alert(response.data.error || '創建失敗');
      }
      
    } catch (error) {
      console.error('❌ DEBUG: 創建資料夾錯誤:', error);
      alert('Network error: Unable to connect to server');
    } finally {
      setCreating(false);
    }
  };

  // 上傳文件
  const uploadFiles = async () => {
    if (!selectedFiles || selectedFiles.length === 0 || !selectedFolder) {
      alert('Please select files and folder');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      
      console.log('🔧 DEBUG: Starting file upload to folder:', selectedFolder);
      console.log('🔧 DEBUG: File count:', selectedFiles.length);
      
      let totalSize = 0;
      let uploadedSize = 0;
      
      for (const file of selectedFiles) {
        totalSize += file.size;
      }
      
      console.log('🔧 DEBUG: Total file size:', formatFileSize(totalSize));
      
      // 檢查文件大小限制
      const maxFileSize = 100 * 1024 * 1024; // 100MB per file
      const maxTotalSize = 500 * 1024 * 1024; // 500MB total
      
      for (const file of selectedFiles) {
        if (file.size > maxFileSize) {
          alert(`File "${file.name}" is too large. Maximum file size is 100MB.`);
          return;
        }
      }
      
      if (totalSize > maxTotalSize) {
        alert(`Total file size is too large. Maximum total size is 500MB.`);
        return;
      }

      // 逐個上傳文件並跟蹤進度
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        setCurrentUploadFile(file.name);
        
        console.log(`🔧 DEBUG: Uploading file ${i + 1}/${selectedFiles.length}: ${file.name} (${formatFileSize(file.size)})`);
        
        const formData = new FormData();
        formData.append('files', file);

        // 創建XMLHttpRequest以跟蹤進度
        await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          
          // 進度回調
          xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
              const fileProgress = (uploadedSize + event.loaded) / totalSize * 100;
              setUploadProgress(Math.round(fileProgress));
            }
          });
          
          // 完成回調
          xhr.addEventListener('load', () => {
            uploadedSize += file.size;
            const overallProgress = uploadedSize / totalSize * 100;
            setUploadProgress(Math.round(overallProgress));
            
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(JSON.parse(xhr.responseText));
            } else {
              reject(new Error(`Upload failed: ${xhr.status}`));
            }
          });
          
          // 錯誤回調
          xhr.addEventListener('error', () => {
            reject(new Error('Upload failed: Network error'));
          });
          
          // 超時回調
          xhr.addEventListener('timeout', () => {
            reject(new Error('Upload failed: Timeout'));
          });
          
          // 設置請求
          xhr.open('POST', `https://sbstest-production.up.railway.app/api/folders/${selectedFolder}/upload`);
          xhr.timeout = 60000; // 60秒超時
          xhr.send(formData);
        });
      }

      console.log('✅ DEBUG: All files uploaded successfully');
      
      // 重新加載文件夾列表和文件列表
        await loadFolders();
      if (selectedFolder) {
        await loadFolderFiles(selectedFolder);
      }
      
      // 清空選擇
      setSelectedFiles(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      alert(`Successfully uploaded ${selectedFiles.length} files!`);
      
    } catch (error) {
      console.error('❌ DEBUG: Upload error:', error);
      
      let errorMessage = 'Upload failed: ';
      if (error instanceof Error) {
        if (error.message.includes('SSL') || error.message.includes('ERR_SSL_BAD_RECORD_MAC_ALERT')) {
          errorMessage += 'SSL connection error. This may be due to file size or network issues. Try uploading smaller files or check your network connection.';
        } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
          errorMessage += 'Upload timeout. The file may be too large or your connection is slow. Try uploading smaller files.';
        } else if (error.message.includes('Network')) {
          errorMessage += 'Network error. Please check your internet connection and try again.';
        } else {
          errorMessage += error.message;
        }
      } else {
        errorMessage += 'Unknown error occurred.';
      }
      
      alert(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
      setCurrentUploadFile('');
    }
  };

  // 載入資料夾文件
  const loadFolderFiles = async (folderName: string) => {
    try {
      console.log('🔧 DEBUG: 載入資料夾文件:', folderName);
      
      const response = await api.get(`/api/folders/${folderName}/files`);
      console.log('🔧 DEBUG: 文件列表響應:', response.data);
      
      if (response.data.success) {
        setFolderFiles(response.data.data);
      } else {
        console.error('❌ DEBUG: 載入文件列表失敗:', response.data.error);
      }
    } catch (error) {
      console.error('❌ DEBUG: 載入文件列表錯誤:', error);
    }
  };

  // 刪除資料夾
  const deleteFolder = async (folderName: string) => {
    if (!confirm(`確定要刪除資料夾 "${folderName}" 嗎？此操作不可撤銷。`)) return;

    try {
      console.log('🔧 DEBUG: 刪除資料夾:', folderName);

      const response = await api.delete(`/api/folders/${folderName}`);
      console.log('🔧 DEBUG: 刪除響應:', response.data);

      if (response.data.success) {
        if (selectedFolder === folderName) {
          setSelectedFolder('');
          setFolderFiles([]);
        }
        alert(response.data.message || '資料夾刪除成功！');
        await loadFolders();
      } else {
        alert(response.data.error || '刪除失敗');
      }
    } catch (error) {
      console.error('❌ DEBUG: 刪除資料夾錯誤:', error);
      alert('刪除失敗，請檢查網絡連接');
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 格式化日期
  const formatDate = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleString('zh-TW');
  };

  useEffect(() => {
    loadFolders();
  }, []);

  useEffect(() => {
    if (selectedFolder) {
      loadFolderFiles(selectedFolder);
    }
  }, [selectedFolder]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Folder Management</h1>
        <p className="mt-2 text-gray-600">Create folders and upload video files for comparison testing</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 資料夾列表 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">Folder List</h2>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                ➕ Create Folder
              </button>
            </div>
            
            <div className="p-4">
              {loading ? (
                <div className="text-center py-4">載入中...</div>
              ) : folders.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FolderIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>No folders created yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {folders.map((folder) => (
                    <div
                      key={folder.name}
                      className={`p-3 rounded-lg border-2 cursor-pointer transition-colors ${
                        selectedFolder === folder.name
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedFolder(folder.name)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <FolderIcon className="h-5 w-5 text-gray-500 mr-2" />
                          <div>
                            <p className="font-medium text-gray-900">{folder.name}</p>
                            <p className="text-sm text-gray-500">
                              {folder.video_count} 個視頻 • {formatFileSize(folder.total_size)}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteFolder(folder.name);
                          }}
                          className="p-1 text-gray-400 hover:text-red-500"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 文件管理區域 */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedFolder ? `${selectedFolder} 中的文件` : '請選擇資料夾'}
                </h2>
                {selectedFolder && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      <CloudArrowUpIcon className="h-4 w-4 mr-2" />
                      {uploading ? '上傳中...' : '上傳視頻'}
                    </button>
                    <button
                      onClick={async () => {
                        try {
                          // 模擬上傳成功
                          const folder = folders.find(f => f.name === selectedFolder);
                          if (folder) {
                            folder.video_count += 3; // 假設上傳了3個文件
                            folder.total_size += 50000000; // 假設50MB
                            setFolders([...folders]);
                            await loadFolderFiles(selectedFolder);
                            alert('模擬上傳成功！添加了3個測試文件');
                          }
                        } catch (error) {
                          console.error('模擬上傳錯誤:', error);
                        }
                      }}
                      className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      📝 測試上傳
                    </button>
                    <input
                      type="file"
                      ref={fileInputRef}
                      multiple
                      accept="video/*"
                      style={{ display: 'none' }}
                      onChange={(e) => {
                        if (e.target.files && e.target.files.length > 0) {
                          setSelectedFiles(Array.from(e.target.files));
                        }
                      }}
                    />
                  </div>
                )}
              </div>
            </div>

            <div className="p-4">
              {!selectedFolder ? (
                <div className="text-center py-12 text-gray-500">
                  <VideoCameraIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg">請先選擇一個資料夾</p>
                </div>
              ) : folderFiles.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <DocumentIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-lg">此資料夾中沒有視頻文件</p>
                  <p className="text-sm mt-2">點擊上方「上傳視頻」按鈕開始上傳</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {folderFiles.map((file) => (
                    <div
                      key={file.filename}
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                    >
                      <div className="flex items-center">
                        <VideoCameraIcon className="h-5 w-5 text-gray-500 mr-3" />
                        <div>
                          <p className="font-medium text-gray-900">{file.filename}</p>
                          <p className="text-sm text-gray-500">
                            {formatFileSize(file.size)} • {formatDate(file.created_time)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 創建資料夾模態框 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">Create New Folder</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Folder Name
                </label>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="Enter folder name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      createFolder();
                    }
                  }}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={createFolder}
                  disabled={!newFolderName.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 顯示已選文件 */}
      {selectedFiles && selectedFiles.length > 0 && (
        <div className="mt-4">
          <h4 className="text-md font-medium text-gray-700 mb-2">
            Selected Files ({selectedFiles.length}):
          </h4>
          <div className="max-h-32 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div key={index} className="text-sm text-gray-600 flex justify-between">
                <span>{file.name}</span>
                <span>{formatFileSize(file.size)}</span>
              </div>
            ))}
          </div>
          
          {/* 上傳按鈕 */}
          <button
            onClick={uploadFiles}
            disabled={uploading || !selectedFolder}
            className={`mt-3 w-full px-4 py-2 rounded text-white font-medium ${
              uploading || !selectedFolder
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? 'Uploading...' : 'Upload Files'}
          </button>
          
          {/* 進度條 */}
          {uploading && (
            <div className="mt-3">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Uploading: {currentUploadFile}</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FolderManagePage; 