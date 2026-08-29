import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for request ID
api.interceptors.request.use(config => {
  const requestId = crypto.randomUUID()
  config.headers['X-Request-ID'] = requestId
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.data?.error) {
      // Error is already formatted by backend
      return Promise.reject(error)
    }
    // Network or unexpected error
    const message = error.message || 'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

export { api }