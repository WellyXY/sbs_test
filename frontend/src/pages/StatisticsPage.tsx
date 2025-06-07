import React from 'react'

const StatisticsPage: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">任務統計</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">總評估數</h3>
          <p className="text-3xl font-bold text-primary-600">50</p>
        </div>
        
        <div className="card text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">A 較好</h3>
          <p className="text-3xl font-bold text-green-600">30</p>
        </div>
        
        <div className="card text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">B 較好</h3>
          <p className="text-3xl font-bold text-blue-600">20</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">詳細統計</h3>
        <p className="text-gray-600">統計圖表和詳細數據將在此顯示</p>
      </div>
    </div>
  )
}

export default StatisticsPage 