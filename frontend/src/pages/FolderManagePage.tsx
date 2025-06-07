import React, { useState, useEffect, useRef } from 'react';
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
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [folderFiles, setFolderFiles] = useState<FileInfo[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 加載資料夾列表
  const loadFolders = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/folders/');
      if (response.ok) {
        const data = await response.json();
        setFolders(data);
      } else {
        console.error('Failed to load folders');
      }
    } catch (error) {
      console.error('Folder loading error:', error);
    } finally {
      setLoading(false);
    }
  };

  // 創建新資料夾
  const createFolder = async () => {
    if (!newFolderName.trim()) return;
    
    try {
      setCreating(true);
      console.log('Creating folder:', newFolderName);
      
      const response = await fetch('/api/folders/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newFolderName.trim()
        }),
      });

      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Creation successful:', data);
        setNewFolderName('');
        setShowCreateModal(false);
        alert('Folder created successfully!');
        await loadFolders();
      } else {
        const error = await response.json();
        console.error('Creation failed:', error);
        alert(error.detail || 'Failed to create folder');
      }
    } catch (error) {
      console.error('Folder creation error:', error);
      alert('Network error: Unable to connect to server');
    } finally {
      setCreating(false);
    }
  };

  // 上傳文件
  const uploadFiles = async (files: FileList) => {
    if (!selectedFolder || files.length === 0) return;

    try {
      setUploading(true);
      const formData = new FormData();
      
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }

      const response = await fetch(`/api/folders/${selectedFolder}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        await loadFolders();
        await loadFolderFiles(selectedFolder);
      } else {
        const error = await response.json();
        alert(error.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  // 載入資料夾文件
  const loadFolderFiles = async (folderName: string) => {
    try {
      const response = await fetch(`/api/folders/${folderName}/files`);
      if (response.ok) {
        const data = await response.json();
        setFolderFiles(data);
      }
    } catch (error) {
      console.error('載入文件列表錯誤:', error);
    }
  };

  // 刪除資料夾
  const deleteFolder = async (folderName: string) => {
    if (!confirm(`確定要刪除資料夾 "${folderName}" 嗎？此操作不可撤銷。`)) return;

    try {
      const response = await fetch(`/api/folders/${folderName}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        if (selectedFolder === folderName) {
          setSelectedFolder(null);
          setFolderFiles([]);
        }
        await loadFolders();
      } else {
        const error = await response.json();
        alert(error.detail || '刪除失敗');
      }
    } catch (error) {
      console.error('刪除資料夾錯誤:', error);
      alert('刪除失敗');
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
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
        <h1 className="text-3xl font-bold text-gray-900">資料夾管理</h1>
        <p className="mt-2 text-gray-600">創建資料夾並上傳視頻文件，用於對比測試</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 資料夾列表 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">資料夾列表</h2>
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                新建
              </button>
            </div>
            
            <div className="p-4">
              {loading ? (
                <div className="text-center py-4">載入中...</div>
              ) : folders.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FolderIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>尚未創建任何資料夾</p>
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
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      accept="video/*"
                      onChange={(e) => e.target.files && uploadFiles(e.target.files)}
                      className="hidden"
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploading}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      <CloudArrowUpIcon className="h-4 w-4 mr-1" />
                      {uploading ? '上傳中...' : '上傳視頻'}
                    </button>
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
                <h3 className="text-lg font-medium text-gray-900">創建新資料夾</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  資料夾名稱
                </label>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="輸入資料夾名稱"
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
                  取消
                </button>
                <button
                  onClick={createFolder}
                  disabled={!newFolderName.trim()}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  創建
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FolderManagePage; 