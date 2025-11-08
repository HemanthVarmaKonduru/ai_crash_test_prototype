/**
 * API Configuration
 * 
 * Centralized API endpoint configuration.
 * Uses environment variables with fallback to localhost for development.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiConfig = {
  baseUrl: API_URL,
  endpoints: {
    // Auth endpoints
    login: `${API_URL}/api/v1/auth/login`,
    logout: `${API_URL}/api/v1/auth/logout`,
    verify: `${API_URL}/api/v1/auth/verify`,
    
    // Prompt Injection endpoints
    promptInjection: {
      start: `${API_URL}/api/v1/test/prompt-injection/start`,
      status: (testId: string) => `${API_URL}/api/v1/test/prompt-injection/${testId}/status`,
      results: (testId: string) => `${API_URL}/api/v1/test/prompt-injection/${testId}/results`,
      download: (testId: string) => `${API_URL}/api/v1/test/prompt-injection/${testId}/download`,
    },
    
    // Jailbreak endpoints
    jailbreak: {
      start: `${API_URL}/api/v1/test/jailbreak/start`,
      status: (testId: string) => `${API_URL}/api/v1/test/jailbreak/${testId}/status`,
      results: (testId: string) => `${API_URL}/api/v1/test/jailbreak/${testId}/results`,
      download: (testId: string) => `${API_URL}/api/v1/test/jailbreak/${testId}/download`,
    },
    
    // Data Extraction endpoints
    dataExtraction: {
      start: `${API_URL}/api/v1/test/data-extraction/start`,
      status: (testId: string) => `${API_URL}/api/v1/test/data-extraction/${testId}/status`,
      results: (testId: string) => `${API_URL}/api/v1/test/data-extraction/${testId}/results`,
      download: (testId: string) => `${API_URL}/api/v1/test/data-extraction/${testId}/download`,
    },
  },
}

export default apiConfig

