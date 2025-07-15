import React from 'react';
import { AutoSaveStatusProps } from '../hooks/useAutoSave';

export function AutoSaveStatus({ hasUnsavedChanges, lastSaved, onSaveNow }: AutoSaveStatusProps) {
  const getStatusText = () => {
    if (hasUnsavedChanges) {
      return '저장되지 않은 변경사항';
    }
    if (lastSaved) {
      const now = new Date();
      const diffMs = now.getTime() - lastSaved.getTime();
      const diffMinutes = Math.floor(diffMs / 60000);
      
      if (diffMinutes < 1) {
        return '방금 저장됨';
      } else if (diffMinutes < 60) {
        return `${diffMinutes}분 전 저장됨`;
      } else {
        return lastSaved.toLocaleTimeString('ko-KR', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }) + '에 저장됨';
      }
    }
    return '저장 안됨';
  };

  const getStatusColor = () => {
    if (hasUnsavedChanges) return 'text-orange-600';
    if (lastSaved) return 'text-green-600';
    return 'text-gray-500';
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`flex items-center gap-1 ${getStatusColor()}`}>
        {hasUnsavedChanges ? (
          <span className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
        ) : (
          <span className="w-2 h-2 bg-green-500 rounded-full" />
        )}
        <span>{getStatusText()}</span>
      </div>
      
      {hasUnsavedChanges && onSaveNow && (
        <button
          onClick={onSaveNow}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          지금 저장
        </button>
      )}
    </div>
  );
}