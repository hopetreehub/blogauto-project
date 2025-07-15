import { render, screen } from '@testing-library/react'
import Navigation from '../Navigation'

// Mock usePathname
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/dashboard'),
}))

describe('Navigation Component', () => {
  it('renders all navigation links', () => {
    render(<Navigation />)
    
    // 주요 네비게이션 링크들이 있는지 확인
    expect(screen.getByText(/대시보드/i)).toBeInTheDocument()
    expect(screen.getByText(/키워드/i)).toBeInTheDocument()
    expect(screen.getByText(/제목/i)).toBeInTheDocument()
    expect(screen.getByText(/콘텐츠/i)).toBeInTheDocument()
    expect(screen.getByText(/설정/i)).toBeInTheDocument()
  })

  it('renders the logo/title', () => {
    render(<Navigation />)
    
    const title = screen.getByText(/블로그 자동화/i)
    expect(title).toBeInTheDocument()
  })

  it('has proper navigation structure', () => {
    render(<Navigation />)
    
    const nav = screen.getByRole('navigation')
    expect(nav).toBeInTheDocument()
  })
})