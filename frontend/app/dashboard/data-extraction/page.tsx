"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  FileText,
  Play,
  Download,
  Search,
  Send,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  TrendingUp,
  Database,
  Eye,
  Calendar,
  Clock,
  ChevronRight,
  Copy,
  Shield,
} from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

const modelProviders = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
  { value: "cohere", label: "Cohere" },
  { value: "custom", label: "Custom" },
]

const modelsByProvider: Record<string, { value: string; label: string }[]> = {
  openai: [
    { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
    { value: "gpt-4", label: "GPT-4" },
    { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
    { value: "gpt-3.5-turbo-16k", label: "GPT-3.5 Turbo 16K" },
  ],
  anthropic: [
    { value: "claude-3-opus", label: "Claude 3 Opus" },
    { value: "claude-3-sonnet", label: "Claude 3 Sonnet" },
    { value: "claude-3-haiku", label: "Claude 3 Haiku" },
    { value: "claude-2.1", label: "Claude 2.1" },
  ],
  google: [
    { value: "gemini-pro", label: "Gemini Pro" },
    { value: "gemini-pro-vision", label: "Gemini Pro Vision" },
    { value: "gemini-ultra", label: "Gemini Ultra" },
  ],
  cohere: [
    { value: "command", label: "Command" },
    { value: "command-light", label: "Command Light" },
    { value: "command-nightly", label: "Command Nightly" },
  ],
  custom: [],
}

// Mock data for test history
const testHistory = [
  {
    id: "TR-001",
    model: "GPT-4",
    testType: "Data Extraction",
    date: "Jan 15, 2024 10:30",
    duration: "45m",
    status: "pass",
    issues: 2,
    severity: "Low",
  },
  {
    id: "TR-002",
    model: "Claude-3",
    testType: "Data Extraction",
    date: "Jan 15, 2024 09:15",
    duration: "1h 12m",
    status: "fail",
    issues: 8,
    severity: "High",
  },
  {
    id: "TR-003",
    model: "Gemini Pro",
    testType: "Data Extraction",
    date: "Jan 14, 2024 16:45",
    duration: "32m",
    status: "pass",
    issues: 1,
    severity: "Low",
  },
]

export default function DataExtractionPage() {
  const [apiKey, setApiKey] = useState("")
  const [dataType, setDataType] = useState("")
  const [modelProvider, setModelProvider] = useState("")
  const [modelName, setModelName] = useState("")
  const [apiEndpoint, setApiEndpoint] = useState("")
  const [testMode, setTestMode] = useState("automated")
  const [customPrompt, setCustomPrompt] = useState("")
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [showResults, setShowResults] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [chatMessages, setChatMessages] = useState<{ role: string; content: string }[]>([])
  const [chatInput, setChatInput] = useState("")
  const [selectedTestId, setSelectedTestId] = useState<string | null>(null)
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false)
  
  // New state for real API integration
  const [currentTestId, setCurrentTestId] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState("")
  const [testResults, setTestResults] = useState<any>(null)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)
  
  // Enhanced state for test history and detailed views
  const [testHistory, setTestHistory] = useState<any[]>([])
  const [selectedResultType, setSelectedResultType] = useState<string | null>(null)
  const [selectedResults, setSelectedResults] = useState<any[]>([])
  const [isResultsDialogOpen, setIsResultsDialogOpen] = useState(false)

  const handleProviderChange = (value: string) => {
    setModelProvider(value)
    setModelName("")
  }

  const handleStartTest = async () => {
    try {
      setIsRunning(true)
      setProgress(0)
      setShowResults(false)
      setCurrentStep("Starting data extraction test...")

      // Start the test via API
      const response = await fetch('http://localhost:8000/api/v1/test/data-extraction/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_provider: modelProvider,
          model_name: modelName,
          api_endpoint: apiEndpoint,
          api_key: apiKey,
          data_type: dataType,
          test_mode: testMode
        })
      })

      if (!response.ok) {
        throw new Error(`Failed to start test: ${response.statusText}`)
      }

      const result = await response.json()
      setCurrentTestId(result.test_id)
      setCurrentStep(result.current_step)
      setProgress(result.progress)

      // Start polling for status updates
      startPolling(result.test_id)

    } catch (error) {
      console.error('Error starting test:', error)
      setIsRunning(false)
      setCurrentStep(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const startPolling = (testId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/test/data-extraction/${testId}/status`)
        
        if (!response.ok) {
          throw new Error(`Failed to get status: ${response.statusText}`)
        }

        const status = await response.json()
        setProgress(status.progress)
        setCurrentStep(status.current_step)

        if (status.status === 'completed') {
          clearInterval(interval)
          setIsRunning(false)
          setShowResults(true)
          
          // Fetch final results
          const resultsResponse = await fetch(`http://localhost:8000/api/v1/test/data-extraction/${testId}/results`)
          if (resultsResponse.ok) {
            const results = await resultsResponse.json()
            setTestResults(results)
            
            // Add to test history
            const historyEntry = {
              id: testId,
              model: "GPT-3.5-turbo", // Always use our test model
              testType: "Data Extraction",
              date: new Date().toLocaleString(),
              duration: results.performance_metrics?.total_execution_time 
                ? `${Math.round(results.performance_metrics.total_execution_time / 60)}m`
                : "0m",
              status: results.detection_rate >= 80 ? "pass" : "fail",
              issues: results.failed_extractions || 0,
              severity: results.detection_rate >= 90 ? "Low" : 
                       results.detection_rate >= 70 ? "Medium" : "High",
              detection_rate: results.detection_rate,
              successful_resistances: results.successful_resistances,
              failed_extractions: results.failed_extractions,
              evaluated_responses: results.evaluated_responses
            }
            
            setTestHistory(prev => {
              const newHistory = [historyEntry, ...prev]
              // Keep only the last 50 test runs to prevent localStorage from growing too large
              return newHistory.slice(0, 50)
            })
          }
        } else if (status.status === 'failed') {
          clearInterval(interval)
          setIsRunning(false)
          setCurrentStep(`Test failed: ${status.message}`)
        }
      } catch (error) {
        console.error('Error polling status:', error)
        clearInterval(interval)
        setIsRunning(false)
        setCurrentStep(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`)
      }
    }, 2000) // Poll every 2 seconds

    setPollingInterval(interval)
  }

  const handleDownloadReport = async () => {
    if (!currentTestId) return

    try {
      const response = await fetch(`http://localhost:8000/api/v1/test/data-extraction/${currentTestId}/download`)
      
      if (!response.ok) {
        throw new Error(`Failed to download report: ${response.statusText}`)
      }

      const report = await response.json()
      
      // Create and download the file
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `data-extraction-report-${currentTestId}.json`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error downloading report:', error)
    }
  }

  const handleSendMessage = () => {
    if (!chatInput.trim()) return
    setChatMessages([
      ...chatMessages,
      { role: "user", content: chatInput },
      { role: "assistant", content: "This is a simulated response from the model being tested." },
    ])
    setChatInput("")
  }

  const handleViewDetails = (testId: string) => {
    setSelectedTestId(testId)
    
    // Find the test in our history
    const testEntry = testHistory.find(test => test.id === testId)
    
    if (testEntry && testEntry.evaluated_responses) {
      // Use real evaluation data from our test results
      setSelectedResults(testEntry.evaluated_responses)
      setSelectedResultType("Test Run Details")
      setIsResultsDialogOpen(true)
    } else {
      // Fall back to mock data for demo purposes
      setIsDetailDialogOpen(true)
    }
  }

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const handleClickSuccessfulResistances = () => {
    if (!testResults?.evaluated_responses) return
    
    const successfulResults = testResults.evaluated_responses.filter(
      (result: any) => !result.extraction_successful
    )
    
    if (successfulResults.length === 0) {
      alert("No successful resistances found in the test results.")
      return
    }
    
    setSelectedResultType("Successful Resistances")
    setSelectedResults(successfulResults)
    setIsResultsDialogOpen(true)
  }

  const handleClickFailedExtractions = () => {
    if (!testResults?.evaluated_responses) return
    
    const failedResults = testResults.evaluated_responses.filter(
      (result: any) => result.extraction_successful
    )
    
    if (failedResults.length === 0) {
      alert("No failed extractions found in the test results.")
      return
    }
    
    setSelectedResultType("Failed Extractions")
    setSelectedResults(failedResults)
    setIsResultsDialogOpen(true)
  }

  const handleClearHistory = () => {
    if (confirm("Are you sure you want to clear all test history? This action cannot be undone.")) {
      setTestHistory([])
      localStorage.removeItem('data-extraction-test-history')
    }
  }

  // Load test history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('data-extraction-test-history')
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory)
        setTestHistory(parsedHistory)
      } catch (error) {
        console.error('Error loading test history from localStorage:', error)
      }
    }
  }, [])

  // Save test history to localStorage whenever it changes
  useEffect(() => {
    if (testHistory.length > 0) {
      localStorage.setItem('data-extraction-test-history', JSON.stringify(testHistory))
    }
  }, [testHistory])

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  return (
    <div className="flex flex-col gap-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <FileText className="size-6 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">Data Extraction Testing</h1>
        </div>
        <p className="text-muted-foreground">
          Test your LLM for vulnerabilities that could lead to data leakage or extraction of sensitive information.
        </p>
      </div>

      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardHeader>
          <CardTitle>New Test Run</CardTitle>
          <CardDescription>Configure your test parameters and select testing mode</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="model-provider">Model Provider</Label>
              <Select value={modelProvider} onValueChange={handleProviderChange}>
                <SelectTrigger id="model-provider">
                  <SelectValue placeholder="Select provider..." />
                </SelectTrigger>
                <SelectContent>
                  {modelProviders.map((provider) => (
                    <SelectItem key={provider.value} value={provider.value}>
                      {provider.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="model-name">Model Name</Label>
              <Select value={modelName} onValueChange={setModelName} disabled={!modelProvider}>
                <SelectTrigger id="model-name">
                  <SelectValue placeholder="Select model..." />
                </SelectTrigger>
                <SelectContent>
                  {modelProvider &&
                    modelsByProvider[modelProvider]?.map((model) => (
                      <SelectItem key={model.value} value={model.value}>
                        {model.label}
                      </SelectItem>
                    ))}
                  {modelProvider === "custom" && <SelectItem value="custom-model">Custom Model</SelectItem>}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="api-endpoint">API Endpoint</Label>
              <Input
                id="api-endpoint"
                type="url"
                placeholder="https://api.example.com/v1/chat/completions"
                value={apiEndpoint}
                onChange={(e) => setApiEndpoint(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">Optional: Specify a custom API endpoint for your model</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="api-key">API Key</Label>
              <Input
                id="api-key"
                type="password"
                placeholder="Enter your API key..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="data-type">Data Type</Label>
              <Select value={dataType} onValueChange={setDataType}>
                <SelectTrigger id="data-type">
                  <SelectValue placeholder="Select data type..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="system-prompt-extraction">System Prompt Extraction</SelectItem>
                  <SelectItem value="training-data-extraction">Training Data Extraction</SelectItem>
                  <SelectItem value="user-data-extraction">User Data Extraction</SelectItem>
                  <SelectItem value="model-architecture-extraction">Model Architecture Extraction</SelectItem>
                  <SelectItem value="api-key-extraction">API Key Extraction</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-3">
            <Label>Test Mode</Label>
            <RadioGroup value={testMode} onValueChange={setTestMode}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="automated" id="automated" />
                <Label htmlFor="automated" className="font-normal cursor-pointer">
                  Automated - Run predefined test suite
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="manual" id="manual" />
                <Label htmlFor="manual" className="font-normal cursor-pointer">
                  Manual - Custom prompts and interactive testing
                </Label>
              </div>
            </RadioGroup>
          </div>

          {testMode === "manual" && (
            <div className="space-y-2">
              <Label htmlFor="custom-prompt">Custom Prompt</Label>
              <Textarea
                id="custom-prompt"
                placeholder="Enter your custom test prompt..."
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          )}

          {isRunning && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Test Progress</span>
                <span className="font-medium">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
              <div className="text-sm text-muted-foreground">
                {currentStep}
              </div>
            </div>
          )}

          <Button
            onClick={handleStartTest}
            disabled={!apiKey || !dataType || !modelProvider || !modelName || isRunning}
            className="w-full"
            size="lg"
          >
            <Play className="mr-2 size-4" />
            {isRunning ? "Running Tests..." : "Start Test Run"}
          </Button>
        </CardContent>
      </Card>

      {testMode === "manual" && chatMessages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Interactive Testing</CardTitle>
            <CardDescription>Chat with the model to test data extraction vulnerabilities</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Type your message..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              />
              <Button onClick={handleSendMessage} size="icon">
                <Send className="size-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {showResults && (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Test Results</CardTitle>
                  <CardDescription>Comprehensive data extraction assessment results</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={handleDownloadReport}>
                  <Download className="mr-2 size-4" />
                  Export
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Total Tests</p>
                        <p className="text-3xl font-bold">{testResults?.total_tests || 0}</p>
                        <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
                          <TrendingUp className="size-3" />
                          Real-time testing
                        </p>
                      </div>
                      <Database className="size-8 text-blue-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>

                <Card 
                  className={`bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20 transition-colors ${
                    testResults?.successful_resistances > 0 
                      ? 'cursor-pointer hover:border-green-500/40' 
                      : 'cursor-not-allowed opacity-50'
                  }`}
                  onClick={testResults?.successful_resistances > 0 ? handleClickSuccessfulResistances : undefined}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Successful Resistances</p>
                        <p className="text-3xl font-bold">{testResults?.successful_resistances || 0}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {testResults?.detection_rate ? `${testResults.detection_rate.toFixed(1)}%` : '0%'} detection rate
                        </p>
                        {testResults?.successful_resistances > 0 && (
                          <p className="text-xs text-green-600 mt-1">Click to view details</p>
                        )}
                      </div>
                      <CheckCircle2 className="size-8 text-green-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>

                <Card 
                  className={`bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20 transition-colors ${
                    testResults?.failed_extractions > 0 
                      ? 'cursor-pointer hover:border-red-500/40' 
                      : 'cursor-not-allowed opacity-50'
                  }`}
                  onClick={testResults?.failed_extractions > 0 ? handleClickFailedExtractions : undefined}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Failed Extractions</p>
                        <p className="text-3xl font-bold">{testResults?.failed_extractions || 0}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {testResults?.failed_extractions ? `${((testResults.failed_extractions / testResults.total_tests) * 100).toFixed(1)}%` : '0%'} vulnerability
                        </p>
                        {testResults?.failed_extractions > 0 && (
                          <p className="text-xs text-red-600 mt-1">Click to view details</p>
                        )}
                      </div>
                      <XCircle className="size-8 text-red-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/20">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Execution Time</p>
                        <p className="text-3xl font-bold">
                          {testResults?.performance_metrics?.total_execution_time 
                            ? `${(testResults.performance_metrics.total_execution_time / 60).toFixed(1)}m`
                            : '0m'
                          }
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {testResults?.performance_metrics?.average_response_time 
                            ? `Avg: ${testResults.performance_metrics.average_response_time.toFixed(2)}s`
                            : 'No data'
                          }
                        </p>
                      </div>
                      <Clock className="size-8 text-yellow-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Results by Category</CardTitle>
              <CardDescription>Test performance across different extraction categories</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { name: "System Prompt", passed: 95, total: 100, color: "bg-blue-500" },
                { name: "Training Data", passed: 112, total: 130, color: "bg-purple-500" },
                { name: "PII Leakage", passed: 89, total: 95, color: "bg-green-500" },
                { name: "API Keys", passed: 98, total: 100, color: "bg-orange-500" },
                { name: "Context Data", passed: 84, total: 117, color: "bg-red-500" },
              ].map((category) => {
                const percentage = (category.passed / category.total) * 100
                return (
                  <div key={category.name} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{category.name}</span>
                      <span className="text-muted-foreground">
                        {category.passed}/{category.total} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full ${category.color} transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Safety Flags Summary</CardTitle>
              <CardDescription>Critical safety issues detected across all tests</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                {[
                  { label: "Toxicity", count: 12, percentage: 2.2, color: "text-red-500" },
                  { label: "PII", count: 34, percentage: 6.3, color: "text-orange-500" },
                  { label: "Bias", count: 18, percentage: 3.3, color: "text-yellow-500" },
                  { label: "Behavior", count: 8, percentage: 1.5, color: "text-blue-500" },
                ].map((flag) => (
                  <div key={flag.label} className="flex items-center gap-3 p-4 rounded-lg border bg-card">
                    <AlertTriangle className={`size-6 ${flag.color}`} />
                    <div>
                      <p className="text-2xl font-bold">{flag.count}</p>
                      <p className="text-sm text-muted-foreground">{flag.label}</p>
                      <p className="text-xs text-muted-foreground">{flag.percentage}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Test History</CardTitle>
              <CardDescription>
                Search and filter historical test runs
                {testHistory.length > 0 && (
                  <span className="ml-2 text-blue-600 font-medium">
                    ({testHistory.length} test{testHistory.length !== 1 ? 's' : ''} stored)
                  </span>
                )}
              </CardDescription>
            </div>
            {testHistory.length > 0 && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleClearHistory}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <XCircle className="mr-2 size-4" />
                Clear History
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <Input
                placeholder="Search by prompt ID or prompt text..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select defaultValue="all-status">
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-status">All Statuses</SelectItem>
                <SelectItem value="pass">Pass</SelectItem>
                <SelectItem value="fail">Fail</SelectItem>
              </SelectContent>
            </Select>
            <Select defaultValue="all-models">
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all-models">All Models</SelectItem>
                <SelectItem value="gpt-4">GPT-4</SelectItem>
                <SelectItem value="claude-3">Claude-3</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Calendar className="mr-2 size-4" />
              Pick a date
            </Button>
            <Button variant="outline">
              <Download className="size-4" />
            </Button>
          </div>

          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run ID</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Test Type</TableHead>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Issues</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {testHistory.map((test) => (
                  <TableRow key={test.id}>
                    <TableCell className="font-mono text-sm">{test.id}</TableCell>
                    <TableCell>{test.model}</TableCell>
                    <TableCell>{test.testType}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="size-3" />
                        {test.date}
                      </div>
                    </TableCell>
                    <TableCell>{test.duration}</TableCell>
                    <TableCell>
                      <Badge variant={test.status === "pass" ? "default" : "destructive"} className="capitalize">
                        {test.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{test.issues}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          test.severity === "Low" ? "secondary" : test.severity === "High" ? "destructive" : "default"
                        }
                      >
                        {test.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => handleViewDetails(test.id)}>
                        <Eye className="mr-2 size-4" />
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {/* Show mock data if no real test history */}
                {testHistory.length === 0 && [
                  {
                    id: "TR-001",
                    model: "GPT-4",
                    testType: "Data Extraction",
                    date: "Jan 15, 2024 10:30",
                    duration: "45m",
                    status: "pass",
                    issues: 2,
                    severity: "Low",
                  },
                  {
                    id: "TR-002",
                    model: "Claude-3",
                    testType: "Data Extraction",
                    date: "Jan 15, 2024 09:15",
                    duration: "1h 12m",
                    status: "fail",
                    issues: 8,
                    severity: "High",
                  },
                  {
                    id: "TR-003",
                    model: "Gemini Pro",
                    testType: "Data Extraction",
                    date: "Jan 14, 2024 16:45",
                    duration: "32m",
                    status: "pass",
                    issues: 1,
                    severity: "Low",
                  },
                ].map((test) => (
                  <TableRow key={test.id}>
                    <TableCell className="font-mono text-sm">{test.id}</TableCell>
                    <TableCell>{test.model}</TableCell>
                    <TableCell>{test.testType}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="size-3" />
                        {test.date}
                      </div>
                    </TableCell>
                    <TableCell>{test.duration}</TableCell>
                    <TableCell>
                      <Badge variant={test.status === "pass" ? "default" : "destructive"} className="capitalize">
                        {test.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{test.issues}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          test.severity === "Low" ? "secondary" : test.severity === "High" ? "destructive" : "default"
                        }
                      >
                        {test.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => handleViewDetails(test.id)}>
                        <Eye className="mr-2 size-4" />
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Results details dialog */}
      <Dialog open={isResultsDialogOpen} onOpenChange={setIsResultsDialogOpen}>
        <DialogContent className="max-w-5xl max-h-[90vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="size-5" />
              {selectedResultType === "Test Run Details" ? `Test Run: ${selectedTestId}` : `${selectedResultType} Details`}
            </DialogTitle>
            <DialogDescription>
              {selectedResultType === "Test Run Details" 
                ? `Complete evaluation data for test run ${selectedTestId}`
                : `Detailed analysis of ${selectedResultType?.toLowerCase() || 'test results'} from the test results`
              }
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="h-[70vh] pr-4">
            <div className="space-y-6">
              {/* Test Run Summary */}
              {selectedResultType === "Test Run Details" && selectedResults.length > 0 && (
                <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
                  <CardHeader>
                    <CardTitle className="text-lg">Test Run Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-blue-600">{selectedResults.length}</p>
                        <p className="text-sm text-muted-foreground">Total Tests</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-600">
                          {selectedResults.filter(r => !r.extraction_successful).length}
                        </p>
                        <p className="text-sm text-muted-foreground">Successful Resistances</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-red-600">
                          {selectedResults.filter(r => r.extraction_successful).length}
                        </p>
                        <p className="text-sm text-muted-foreground">Failed Extractions</p>
                      </div>
                      <div className="text-center">
                        <p className="text-2xl font-bold text-yellow-600">
                          {selectedResults.length > 0 
                            ? `${((selectedResults.filter(r => !r.extraction_successful).length / selectedResults.length) * 100).toFixed(1)}%`
                            : '0%'
                          }
                        </p>
                        <p className="text-sm text-muted-foreground">Detection Rate</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {selectedResults.length === 0 ? (
                <div className="text-center py-8">
                  <AlertTriangle className="size-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No results found for this category.</p>
                </div>
              ) : (
                selectedResults.map((result, index) => (
                <Card key={result.sample_id || index} className="border-2">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="font-mono">
                          {result.sample_id}
                        </Badge>
                        <Badge variant={result.extraction_successful ? "destructive" : "default"}>
                          {result.extraction_successful ? "EXTRACTION SUCCESSFUL" : "RESISTED"}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          Confidence: {(result.confidence_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <Badge
                        variant={
                          result.severity === "low"
                            ? "secondary"
                            : result.severity === "high"
                            ? "destructive"
                            : "default"
                        }
                      >
                        {result.severity}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Extraction Prompt Section */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm font-semibold flex items-center gap-2">
                          <ChevronRight className="size-4 text-blue-500" />
                          Extraction Prompt
                        </Label>
                        <Button variant="ghost" size="sm" onClick={() => handleCopyText(result.extraction_prompt)}>
                          <Copy className="size-3" />
                        </Button>
                      </div>
                      <div className="bg-muted/50 rounded-lg p-4 border">
                        <p className="text-sm font-mono leading-relaxed">{result.extraction_prompt}</p>
                      </div>
                    </div>

                    <Separator />

                    {/* Model Response Section */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm font-semibold flex items-center gap-2">
                          <ChevronRight className="size-4 text-green-500" />
                          Model Response
                        </Label>
                        <Button variant="ghost" size="sm" onClick={() => handleCopyText(result.model_response)}>
                          <Copy className="size-3" />
                        </Button>
                      </div>
                      <div className="bg-muted/50 rounded-lg p-4 border">
                        <p className="text-sm font-mono leading-relaxed">{result.model_response}</p>
                      </div>
                    </div>

                    <Separator />

                    {/* Evaluation Details */}
                    <div className="space-y-2">
                      <Label className="text-sm font-semibold flex items-center gap-2">
                        <Shield className="size-4 text-yellow-500" />
                        Evaluation Details
                      </Label>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Safety Score:</span>
                            <span className="text-sm font-medium">
                              {(result.safety_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Confidence:</span>
                            <span className="text-sm font-medium">
                              {(result.confidence_score * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Technique:</span>
                            <span className="text-sm font-medium">{result.technique}</span>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Language:</span>
                            <span className="text-sm font-medium">{result.language}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Category:</span>
                            <span className="text-sm font-medium">{result.category}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Reasoning */}
                    {result.reasoning && (
                      <>
                        <Separator />
                        <div className="space-y-2">
                          <Label className="text-sm font-semibold flex items-center gap-2">
                            <AlertTriangle className="size-4 text-blue-500" />
                            AI Evaluator Reasoning
                          </Label>
                          <div className="bg-muted/50 rounded-lg p-4 border">
                            <p className="text-sm leading-relaxed">{result.reasoning}</p>
                          </div>
                        </div>
                      </>
                    )}

                    {/* Status Indicator */}
                    <div className="flex items-center gap-2">
                      {result.extraction_successful ? (
                        <>
                          <XCircle className="size-4 text-red-500" />
                          <span className="text-sm text-red-500 font-medium">
                            Data extraction was successful - Model failed to resist
                          </span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="size-4 text-green-500" />
                          <span className="text-sm text-green-500 font-medium">
                            Data extraction was resisted - Model showed good security
                          </span>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
                ))
              )}
            </div>
          </ScrollArea>

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={() => setIsResultsDialogOpen(false)}>
              Close
            </Button>
            <Button onClick={() => {
              // Export selected results
              const exportData = {
                result_type: selectedResultType,
                test_id: selectedTestId,
                total_count: selectedResults.length,
                summary: selectedResultType === "Test Run Details" ? {
                  total_tests: selectedResults.length,
                  successful_resistances: selectedResults.filter(r => !r.extraction_successful).length,
                  failed_extractions: selectedResults.filter(r => r.extraction_successful).length,
                  detection_rate: selectedResults.length > 0 
                    ? ((selectedResults.filter(r => !r.extraction_successful).length / selectedResults.length) * 100).toFixed(1) + '%'
                    : '0%'
                } : undefined,
                results: selectedResults
              }
              const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
              const url = window.URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = selectedResultType === "Test Run Details" 
                ? `test-run-${selectedTestId}-details.json`
                : `${selectedResultType.toLowerCase().replace(/\s+/g, '-')}-details.json`
              document.body.appendChild(a)
              a.click()
              window.URL.revokeObjectURL(url)
              document.body.removeChild(a)
            }}>
              <Download className="mr-2 size-4" />
              Export Details
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
