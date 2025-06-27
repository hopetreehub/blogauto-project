import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// 임시 인증 토큰 (실제 환경에서는 보안 강화 필요)
const getAuthToken = () => {
  // 새로 생성한 유효한 토큰 사용
  return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBleGFtcGxlLmNvbSIsImV4cCI6MTc1MDg4NzQ0MywidHlwZSI6ImFjY2VzcyJ9.UOzsvXNrVchCAemcDJfC4oSQGWV1woEq83JRB-YHfIg';
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { endpoint, method = 'POST', data } = body;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // 인증이 필요한 엔드포인트인지 확인
    if (endpoint !== '/api/auth/login' && endpoint !== '/api/auth/register') {
      headers['Authorization'] = `Bearer ${getAuthToken()}`;
    }

    const fetchOptions: RequestInit = {
      method: method,
      headers,
    };

    // GET 요청이 아닌 경우에만 body 추가
    if (method !== 'GET' && data) {
      fetchOptions.body = JSON.stringify(data);
    }

    const response = await fetch(`${BACKEND_URL}${endpoint}`, fetchOptions);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API error: ${response.status} - ${errorText}`);
      return NextResponse.json(
        { error: `Backend API error: ${response.status}` },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('API Proxy Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const endpoint = searchParams.get('endpoint') || '/';

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // 인증이 필요한 엔드포인트인지 확인
    if (endpoint !== '/api/auth/login' && endpoint !== '/api/auth/register') {
      headers['Authorization'] = `Bearer ${getAuthToken()}`;
    }

    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: 'GET',
      headers,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend API error: ${response.status} - ${errorText}`);
      return NextResponse.json(
        { error: `Backend API error: ${response.status}` },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error('API Proxy Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}