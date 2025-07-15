import { NextRequest, NextResponse } from 'next/server'

// API 키를 서버 사이드에서 관리
const API_KEYS = {
  openai: process.env.OPENAI_API_KEY || '',
  gemini: process.env.GEMINI_API_KEY || '',
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { endpoint, ...data } = body

    // 백엔드 API 호출
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${endpoint}`
    
    // 헤더 설정 (API 키는 서버에서만 추가)
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    // 클라이언트에서 온 API 키 대신 서버 환경변수 사용
    if (API_KEYS.openai) {
      headers['X-OpenAI-Key'] = API_KEYS.openai
    }
    if (API_KEYS.gemini) {
      headers['X-Gemini-Key'] = API_KEYS.gemini
    }

    const response = await fetch(backendUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    })

    const result = await response.json()

    return NextResponse.json(result, { status: response.status })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const endpoint = searchParams.get('endpoint')

  if (!endpoint) {
    return NextResponse.json({ error: 'Endpoint required' }, { status: 400 })
  }

  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${endpoint}`
    
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const result = await response.json()

    return NextResponse.json(result, { status: response.status })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}