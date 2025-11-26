import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 minutes for heavy analysis
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      throw new Error(error.response.data.detail || error.response.data.message || 'API Error')
    } else if (error.request) {
      throw new Error('Network error. Please check your connection.')
    } else {
      throw new Error(error.message || 'Unknown error occurred')
    }
  }
)

export default api
