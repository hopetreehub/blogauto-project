'use client';

import { useState, useEffect } from 'react';

interface BatchTask {
  task_id: string;
  task_type: string;
  status: string;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export default function BatchPage() {
  const [tasks, setTasks] = useState<BatchTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // 새 작업 생성 폼
  const [taskType, setTaskType] = useState('keyword_analysis');
  const [keywords, setKeywords] = useState('');
  const [titlesPerKeyword, setTitlesPerKeyword] = useState(3);
  const [contentPerKeyword, setContentPerKeyword] = useState(1);

  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          endpoint: '/api/batch/tasks',
          method: 'GET'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (err) {
      console.error('작업 목록 조회 실패:', err);
    }
  };

  const submitBatchTask = async () => {
    if (!keywords.trim()) {
      setError('키워드를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k);
      
      let endpoint = '/api/batch/submit';
      let data: any = {
        task_type: taskType,
        parameters: {}
      };

      if (taskType === 'keyword_analysis') {
        data.parameters = {
          keywords: keywordList,
          country: 'KR'
        };
      } else if (taskType === 'batch_workflow') {
        endpoint = '/api/batch/workflow';
        data = {
          keywords: keywordList,
          titles_per_keyword: titlesPerKeyword,
          content_per_keyword: contentPerKeyword
        };
      }

      const response = await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          endpoint,
          method: 'POST',
          data
        })
      });

      if (!response.ok) {
        throw new Error('배치 작업 제출에 실패했습니다.');
      }

      const result = await response.json();
      setKeywords('');
      fetchTasks(); // 작업 목록 새로고침
      
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const cancelTask = async (taskId: string) => {
    try {
      await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          endpoint: `/api/batch/cancel/${taskId}`,
          method: 'DELETE'
        })
      });
      
      fetchTasks(); // 작업 목록 새로고침
    } catch (err) {
      console.error('작업 취소 실패:', err);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000); // 5초마다 새로고침
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'running': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '완료';
      case 'running': return '실행 중';
      case 'failed': return '실패';
      case 'cancelled': return '취소됨';
      case 'pending': return '대기 중';
      default: return status;
    }
  };

  const getTaskTypeText = (taskType: string) => {
    switch (taskType) {
      case 'keyword_analysis': return '키워드 분석';
      case 'title_generation': return '제목 생성';
      case 'content_generation': return '콘텐츠 생성';
      case 'batch_workflow': return '전체 워크플로우';
      default: return taskType;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">배치 작업 관리</h1>
          <p className="text-gray-600 mt-2">대량의 키워드나 콘텐츠를 한 번에 처리할 수 있습니다</p>
        </div>

        {/* 새 작업 생성 */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">새 배치 작업 생성</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                작업 유형
              </label>
              <select
                value={taskType}
                onChange={(e) => setTaskType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="keyword_analysis">키워드 분석만</option>
                <option value="batch_workflow">전체 워크플로우 (키워드→제목→콘텐츠)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                키워드 목록 <span className="text-red-500">*</span>
              </label>
              <textarea
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="키워드를 쉼표로 구분해서 입력하세요&#10;예: AI 마케팅, 블로그 최적화, SEO 전략"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {taskType === 'batch_workflow' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  키워드당 제목 생성 수
                </label>
                <input
                  type="number"
                  value={titlesPerKeyword}
                  onChange={(e) => setTitlesPerKeyword(parseInt(e.target.value) || 3)}
                  min="1"
                  max="10"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  키워드당 콘텐츠 생성 수
                </label>
                <input
                  type="number"
                  value={contentPerKeyword}
                  onChange={(e) => setContentPerKeyword(parseInt(e.target.value) || 1)}
                  min="1"
                  max="5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          <button
            onClick={submitBatchTask}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading && (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {loading ? '작업 생성 중...' : '배치 작업 시작'}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
              {error}
            </div>
          )}
        </div>

        {/* 작업 목록 */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">작업 목록</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    작업 ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    유형
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    진행률
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    생성 시간
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    액션
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tasks.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      아직 배치 작업이 없습니다.
                    </td>
                  </tr>
                ) : (
                  tasks.map((task) => (
                    <tr key={task.task_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                        {task.task_id.substring(0, 8)}...
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {getTaskTypeText(task.task_type)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(task.status)}`}>
                          {getStatusText(task.status)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${task.progress}%` }}
                            ></div>
                          </div>
                          <span>{task.progress}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(task.created_at).toLocaleString('ko-KR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(task.status === 'pending' || task.status === 'running') && (
                          <button
                            onClick={() => cancelTask(task.task_id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            취소
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}