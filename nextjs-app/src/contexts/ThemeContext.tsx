'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

export type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  actualTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'blogauto-theme'
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(defaultTheme)
  const [actualTheme, setActualTheme] = useState<'light' | 'dark'>('light')

  // 시스템 테마 감지
  const getSystemTheme = (): 'light' | 'dark' => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return 'light'
  }

  // 실제 적용할 테마 계산
  const calculateActualTheme = (currentTheme: Theme): 'light' | 'dark' => {
    if (currentTheme === 'system') {
      return getSystemTheme()
    }
    return currentTheme
  }

  // 테마 초기화
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const savedTheme = localStorage.getItem(storageKey) as Theme | null
        if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
          setTheme(savedTheme)
        }
      } catch (error) {
        console.warn('테마 설정을 불러올 수 없습니다:', error)
      }
    }
  }, [storageKey])

  // 테마 변경 시 DOM 업데이트
  useEffect(() => {
    const newActualTheme = calculateActualTheme(theme)
    setActualTheme(newActualTheme)

    if (typeof window !== 'undefined') {
      const root = window.document.documentElement
      
      // 기존 테마 클래스 제거
      root.classList.remove('light', 'dark')
      
      // 새 테마 클래스 추가
      root.classList.add(newActualTheme)
      
      // CSS 변수 업데이트
      if (newActualTheme === 'dark') {
        root.style.colorScheme = 'dark'
      } else {
        root.style.colorScheme = 'light'
      }
    }
  }, [theme])

  // 시스템 테마 변경 감지
  useEffect(() => {
    if (typeof window === 'undefined') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (theme === 'system') {
        const newActualTheme = getSystemTheme()
        setActualTheme(newActualTheme)
        
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        root.classList.add(newActualTheme)
        root.style.colorScheme = newActualTheme
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme)
    
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(storageKey, newTheme)
      } catch (error) {
        console.warn('테마 설정을 저장할 수 없습니다:', error)
      }
    }
  }

  const toggleTheme = () => {
    if (theme === 'light') {
      handleSetTheme('dark')
    } else if (theme === 'dark') {
      handleSetTheme('system')
    } else {
      handleSetTheme('light')
    }
  }

  const value: ThemeContextType = {
    theme,
    actualTheme,
    setTheme: handleSetTheme,
    toggleTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme은 ThemeProvider 내에서 사용해야 합니다')
  }
  return context
}