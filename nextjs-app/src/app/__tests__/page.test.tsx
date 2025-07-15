import { render, screen } from '@testing-library/react'
import Home from '../page'

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />)
    
    const heading = screen.getByRole('heading', {
      name: /블로그 자동화 프로세스/i,
    })
    
    expect(heading).toBeInTheDocument()
  })

  it('renders the start button', () => {
    render(<Home />)
    
    const startButton = screen.getByRole('link', {
      name: /시작하기/i,
    })
    
    expect(startButton).toBeInTheDocument()
    expect(startButton).toHaveAttribute('href', '/dashboard')
  })

  it('renders feature cards', () => {
    render(<Home />)
    
    // 4개의 주요 기능 카드가 있는지 확인
    expect(screen.getByText('키워드 분석')).toBeInTheDocument()
    expect(screen.getByText('제목 생성')).toBeInTheDocument()
    expect(screen.getByText('콘텐츠 생성')).toBeInTheDocument()
    expect(screen.getByText('자동 포스팅')).toBeInTheDocument()
  })

  it('has proper meta information', () => {
    render(<Home />)
    
    const description = screen.getByText(/AI 기반 키워드 분석부터 콘텐츠 생성/i)
    expect(description).toBeInTheDocument()
  })
})