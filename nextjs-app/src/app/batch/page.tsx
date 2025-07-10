'use client';

import { useState } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';

export default function BatchPage() {
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const { toasts, success, error: toastError, removeToast } = useToast();

  const handleCsvUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      success('CSV 파일이 선택되었습니다.');
    } else {
      toastError('CSV 파일만 업로드 가능합니다.');
    }
  };

  const processBatch = async () => {
    if (!csvFile) {
      toastError('먼저 CSV 파일을 선택해주세요.');
      return;
    }

    setProcessing(true);
    
    // 시뮬레이션된 배치 처리
    try {
      await new Promise(resolve => setTimeout(resolve, 3000)); // 3초 대기
      success('배치 작업이 완료되었습니다!');
      setCsvFile(null);
    } catch (err) {
      toastError('배치 처리 중 오류가 발생했습니다.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">배치 작업</h1>
          <p className="text-gray-600 mt-2">CSV 파일을 업로드하여 대량 처리를 수행합니다</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">CSV 파일 업로드</h2>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            {csvFile ? (
              <div>
                <p className="text-sm text-gray-600 mb-2">선택된 파일:</p>
                <p className="font-medium">{csvFile.name}</p>
                <p className="text-sm text-gray-500">{(csvFile.size / 1024).toFixed(1)} KB</p>
              </div>
            ) : (
              <div>
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">
                  CSV 파일을 선택하거나 여기에 드래그하세요
                </p>
              </div>
            )}
            
            <input
              type="file"
              accept=".csv"
              onChange={handleCsvUpload}
              className="mt-4"
            />
          </div>

          <div className="mt-6">
            <button
              onClick={processBatch}
              disabled={!csvFile || processing}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? '처리 중...' : '배치 처리 시작'}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">CSV 파일 형식</h2>
          <p className="text-gray-600 mb-4">CSV 파일은 다음 형식을 따라야 합니다:</p>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <pre className="text-sm">
{`keyword,task_type
"AI 마케팅","keyword_analysis"
"블로그 SEO","title_generation"
"콘텐츠 전략","content_generation"`}
            </pre>
          </div>
          
          <div className="mt-4 text-sm text-gray-600">
            <p><strong>task_type 옵션:</strong></p>
            <ul className="list-disc list-inside mt-2">
              <li>keyword_analysis: 키워드 분석</li>
              <li>title_generation: 제목 생성</li>
              <li>content_generation: 콘텐츠 생성</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}