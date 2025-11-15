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
    
    // Adversarial Attacks endpoints
    adversarialAttacks: {
      start: `${API_URL}/api/v1/test/adversarial-attacks/start`,
      status: (testId: string) => `${API_URL}/api/v1/test/adversarial-attacks/${testId}/status`,
      results: (testId: string) => `${API_URL}/api/v1/test/adversarial-attacks/${testId}/results`,
      download: (testId: string) => `${API_URL}/api/v1/test/adversarial-attacks/${testId}/download`,
    },
    
    // Firewall endpoints
    firewall: {
      overview: `${API_URL}/api/v1/firewall/overview`,
      stats: `${API_URL}/api/v1/firewall/stats`,
      evaluateInput: `${API_URL}/api/v1/firewall/evaluate/input`,
      evaluateOutput: `${API_URL}/api/v1/firewall/evaluate/output`,
      chat: `${API_URL}/api/v1/firewall/chat`,
      inputRules: `${API_URL}/api/v1/firewall/rules/input`,
      outputRules: `${API_URL}/api/v1/firewall/rules/output`,
      blockedInputs: `${API_URL}/api/v1/firewall/blocked/inputs`,
      blockedOutputs: `${API_URL}/api/v1/firewall/blocked/outputs`,
      threats: `${API_URL}/api/v1/firewall/threats`,
      patterns: `${API_URL}/api/v1/firewall/patterns`,
      incidents: `${API_URL}/api/v1/firewall/incidents`,
      incidentDetails: (id: string) => `${API_URL}/api/v1/firewall/incidents/${id}`,
      analytics: `${API_URL}/api/v1/firewall/analytics`,
      metrics: `${API_URL}/api/v1/firewall/metrics`,
    },
    
    // Analytics endpoints
    analytics: {
      summary: `${API_URL}/api/v1/analytics/summary`,
      test: (testId: string) => `${API_URL}/api/v1/analytics/test/${testId}`,
      module: (moduleType: string) => `${API_URL}/api/v1/analytics/module/${moduleType}`,
    },
  },
}

export default apiConfig

