import { apiCall } from '../api'

// fetch mock
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

describe('API Utils', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('makes GET requests correctly', async () => {
    const mockResponse = { data: 'test' }
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response)

    const result = await apiCall('GET', '/test')

    expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    expect(result).toEqual(mockResponse)
  })

  it('makes POST requests with data', async () => {
    const mockResponse = { success: true }
    const testData = { key: 'value' }
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response)

    const result = await apiCall('POST', '/test', testData)

    expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData),
    })
    expect(result).toEqual(mockResponse)
  })

  it('handles API errors correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Bad Request' }),
    } as Response)

    await expect(apiCall('GET', '/test')).rejects.toThrow('API 요청 실패: 400')
  })

  it('handles network errors', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    await expect(apiCall('GET', '/test')).rejects.toThrow('Network error')
  })
})