import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Folder {
  name: string;
  path: string;
  video_count: number;
  total_size: number;
  created_time: number;
}

const CreateTaskPage: React.FC = () => {
  const navigate = useNavigate();
  const [folders, setFolders] = useState<Folder[]>([]);
  const [taskName, setTaskName] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [folderA, setFolderA] = useState('');
  const [folderB, setFolderB] = useState('');
  const [isBlind, setIsBlind] = useState(true);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);

  // Load folder list
  const loadFolders = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/folders/')
      if (response.ok) {
        const data = await response.json()
        // API returns array directly, not wrapped in folders property
        setFolders(Array.isArray(data) ? data : [])
      } else {
        alert('Failed to load folders');
      }
    } catch (error) {
      console.error('Folder loading error:', error);
      alert('Failed to load folders');
    } finally {
      setLoading(false)
    }
  }

  // Create task
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!taskName.trim()) {
      alert('Please enter task name');
      return
    }
    
    if (!folderA || !folderB) {
      alert('Please select two folders');
      return
    }
    
    if (folderA === folderB) {
      alert('Please select two different folders');
      return
    }

    try {
      setLoading(true)
      const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: taskName,
          folder_a: folderA,
          folder_b: folderB,
          is_blind: isBlind,
          description: taskDescription || undefined
        }),
      })

      if (response.ok) {
        const task = await response.json()
        alert(`Task created successfully! Matched ${task.video_pairs_count} video pairs`);
        navigate('/tasks')
      } else {
        const error = await response.json()
        alert(error.detail || 'Failed to create task');
      }
    } catch (error) {
      console.error('Task creation error:', error);
      alert('Network error: Unable to connect to server');
    } finally {
      setLoading(false)
    }
  }

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  useEffect(() => {
    loadFolders();
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create New Task</h1>
        <p className="mt-2 text-gray-600">Select two folders for video pair comparison test</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        {/* Basic information */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Task Information</h2>
          
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Task Name *
              </label>
              <input
                type="text"
                value={taskName}
                onChange={(e) => setTaskName(e.target.value)}
                placeholder="Enter task name"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Task Description
              </label>
              <textarea
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                placeholder="Enter task description (optional)"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={isBlind}
                  onChange={(e) => setIsBlind(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Enable Blind Test Mode (Recommended)</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">
                In blind mode, videos will be randomly arranged to avoid subjective bias
              </p>
            </div>
          </div>
        </div>

        {/* Folder selection */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Folder</h2>
          
          {loading ? (
            <div className="text-center py-4">Loading folders...</div>
          ) : !folders || folders.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="mb-4">No folders have been created yet</p>
              <button
                onClick={() => navigate('/folders')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Go to Folder Management →
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* A group folder selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  A Group Folder (Original/Baseline) *
                </label>
                <select
                  value={folderA}
                  onChange={(e) => setFolderA(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select folder</option>
                  {folders && folders.map((folder) => (
                    <option key={folder.name} value={folder.name}>
                      {folder.name} ({folder.video_count} videos)
                    </option>
                  ))}
                </select>
                {folderA && (
                  <div className="mt-2 p-3 bg-blue-50 rounded-md">
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">📁</span>
                      <div>
                        <p className="font-medium text-gray-900">{folderA}</p>
                        <p className="text-sm text-gray-500">
                          {folders.find(f => f.name === folderA)?.video_count} videos • 
                          {formatFileSize(folders.find(f => f.name === folderA)?.total_size || 0)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* B group folder selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  B Group Folder (Processed/Comparison) *
                </label>
                <select
                  value={folderB}
                  onChange={(e) => setFolderB(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select folder</option>
                  {folders && folders.map((folder) => (
                    <option key={folder.name} value={folder.name} disabled={folder.name === folderA}>
                      {folder.name} ({folder.video_count} videos)
                    </option>
                  ))}
                </select>
                {folderB && (
                  <div className="mt-2 p-3 bg-green-50 rounded-md">
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">📁</span>
                      <div>
                        <p className="font-medium text-gray-900">{folderB}</p>
                        <p className="text-sm text-gray-500">
                          {folders.find(f => f.name === folderB)?.video_count} videos • 
                          {formatFileSize(folders.find(f => f.name === folderB)?.total_size || 0)}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Hint information */}
        {folderA && folderB && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <h3 className="text-sm font-medium text-yellow-800 mb-2">💡 Hint</h3>
            <p className="text-sm text-yellow-700">
              The system will automatically match videos with similar file names in the two folders. It's recommended to use meaningful file names,
              such as: <code>video1.mp4</code> and <code>video1_compressed.mp4</code>
            </p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex justify-end space-x-4">
          <button
            onClick={() => navigate('/tasks')}
            className="px-6 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={creating || !taskName.trim() || !folderA || !folderB}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {creating ? 'Creating...' : 'Create Task'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateTaskPage; 