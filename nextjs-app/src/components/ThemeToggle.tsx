'use client'

import React from 'react'
import { useTheme } from '@/contexts/ThemeContext'
import { AccessibleButton } from './AccessibleButton'

// 테마 아이콘들
const SunIcon: React.FC<{ className?: string; size?: number }> = ({ className = '', size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2"/>
    <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42m12.72-12.72l1.42-1.42" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const MoonIcon: React.FC<{ className?: string; size?: number }> = ({ className = '', size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const SystemIcon: React.FC<{ className?: string; size?: number }> = ({ className = '', size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" stroke="currentColor" strokeWidth="2"/>
    <line x1="8" y1="21" x2="16" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

interface ThemeToggleProps {
  variant?: 'icon' | 'dropdown' | 'buttons'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  variant = 'icon', 
  size = 'md',
  className = '' 
}) => {
  const { theme, actualTheme, setTheme, toggleTheme } = useTheme()

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return <SunIcon size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
      case 'dark':
        return <MoonIcon size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
      case 'system':
        return <SystemIcon size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
      default:
        return <SunIcon size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />
    }
  }

  const getThemeLabel = () => {
    switch (theme) {
      case 'light':
        return '라이트 모드'
      case 'dark':
        return '다크 모드'
      case 'system':
        return '시스템 설정'
      default:
        return '라이트 모드'
    }
  }

  if (variant === 'icon') {
    return (
      <AccessibleButton
        onClick={toggleTheme}
        variant="ghost"
        size={size}
        icon={getThemeIcon()}
        ariaLabel={`현재 ${getThemeLabel()}, 클릭하여 테마 변경`}
        className={`transition-colors duration-200 ${className}`}
        title={`현재: ${getThemeLabel()}`}
      />
    )
  }

  if (variant === 'dropdown') {
    return (
      <div className={`relative ${className}`}>
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value as any)}
          className="appearance-none bg-transparent border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
          aria-label="테마 선택"
        >
          <option value="light">🌞 라이트</option>
          <option value="dark">🌙 다크</option>
          <option value="system">💻 시스템</option>
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    )
  }

  if (variant === 'buttons') {
    return (
      <div className={`flex rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden ${className}`}>
        <AccessibleButton
          onClick={() => setTheme('light')}
          variant={theme === 'light' ? 'primary' : 'ghost'}
          size={size}
          icon={<SunIcon size={16} />}
          ariaLabel="라이트 모드로 전환"
          className="rounded-none border-r border-gray-200 dark:border-gray-700"
        />
        <AccessibleButton
          onClick={() => setTheme('dark')}
          variant={theme === 'dark' ? 'primary' : 'ghost'}
          size={size}
          icon={<MoonIcon size={16} />}
          ariaLabel="다크 모드로 전환"
          className="rounded-none border-r border-gray-200 dark:border-gray-700"
        />
        <AccessibleButton
          onClick={() => setTheme('system')}
          variant={theme === 'system' ? 'primary' : 'ghost'}
          size={size}
          icon={<SystemIcon size={16} />}
          ariaLabel="시스템 설정 따르기"
          className="rounded-none"
        />
      </div>
    )
  }

  return null
}

// 간단한 테마 표시 컴포넌트
export const ThemeIndicator: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, actualTheme } = useTheme()
  
  return (
    <div className={`flex items-center text-xs text-gray-500 dark:text-gray-400 ${className}`}>
      {getThemeIcon()}
      <span className="ml-1">
        {theme === 'system' ? `시스템 (${actualTheme === 'dark' ? '다크' : '라이트'})` : getThemeLabel()}
      </span>
    </div>
  )
}

// 헬퍼 함수들을 컴포넌트 외부로 이동
function getThemeIcon() {
  return <SunIcon size={16} />
}

function getThemeLabel() {
  return '라이트 모드'
}