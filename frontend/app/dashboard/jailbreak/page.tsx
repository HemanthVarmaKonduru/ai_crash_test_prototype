"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Shield,
  Play,
  Download,
  Search,
  Send,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  TrendingUp,
  Eye,
  Calendar,
  Clock,
} from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

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

const testHistory = [
  {
    id: "TR-001",
    model: "GPT-4",
    testType: "Jailbreak Detection",
    date: "Jan 15, 2024 10:30",
    duration: "45m",
    status: "pass",
    issues: 2,
    severity: "Low",
  },
  {
    id: "TR-002",
    model: "Claude-3",
    testType: "Jailbreak Detection",
    date: "Jan 15, 2024 09:15",
    duration: "1h 12m",
    status: "fail",
    issues: 8,
    severity: "High",
  },
]

export default function JailbreakPage() {
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

  const handleProviderChange = (value: string) => {
    setModelProvider(value)
    setModelName("")
  }

  const handleStartTest = async () => {
    setIsRunning(true)
    setProgress(0)
    setShowResults(false)

    for (let i = 0; i <= 100; i += 10) {
      await new Promise((resolve) => setTimeout(resolve, 500))
      setProgress(i)
    }

    setIsRunning(false)
    setShowResults(true)
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

  return (
    <div className="flex flex-col gap-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Shield className="size-6 text-primary" />
          <h1 className="text-3xl font-bold tracking-tight">Jailbreak Detection</h1>
        </div>
        <p className="text-muted-foreground">
          Test your LLM's defenses against jailbreak attempts that try to bypass safety guardrails.
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
                  <SelectItem value="dan">DAN (Do Anything Now)</SelectItem>
                  <SelectItem value="hypothetical">Hypothetical Scenarios</SelectItem>
                  <SelectItem value="translation">Translation Attacks</SelectItem>
                  <SelectItem value="code-completion">Code Completion Exploits</SelectItem>
                  <SelectItem value="role-play">Role-Play Jailbreaks</SelectItem>
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
            <CardDescription>Chat with the model to test jailbreak vulnerabilities</CardDescription>
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
                  <CardDescription>Comprehensive jailbreak detection assessment results</CardDescription>
                </div>
                <Button variant="outline" size="sm">
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
                        <p className="text-3xl font-bold">856</p>
                        <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
                          <TrendingUp className="size-3" />
                          +8% from last month
                        </p>
                      </div>
                      <Shield className="size-8 text-blue-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Passed</p>
                        <p className="text-3xl font-bold">678</p>
                        <p className="text-xs text-muted-foreground mt-1">79.2%</p>
                      </div>
                      <CheckCircle2 className="size-8 text-green-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Failed</p>
                        <p className="text-3xl font-bold">134</p>
                        <p className="text-xs text-muted-foreground mt-1">15.7%</p>
                      </div>
                      <XCircle className="size-8 text-red-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/20">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Unknown</p>
                        <p className="text-3xl font-bold">44</p>
                        <p className="text-xs text-muted-foreground mt-1">5.1%</p>
                      </div>
                      <AlertTriangle className="size-8 text-yellow-500 opacity-50" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Results by Category</CardTitle>
              <CardDescription>Test performance across different jailbreak categories</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { name: "Role-Play", passed: 112, total: 140, color: "bg-blue-500" },
                { name: "Context Manipulation", passed: 98, total: 130, color: "bg-purple-500" },
                { name: "Encoding", passed: 145, total: 160, color: "bg-green-500" },
                { name: "Technical Exploits", passed: 89, total: 120, color: "bg-orange-500" },
                { name: "Social Engineering", passed: 134, total: 156, color: "bg-red-500" },
                { name: "Multi-Step Attacks", passed: 100, total: 150, color: "bg-teal-500" },
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
                  { label: "Toxicity", count: 32, percentage: 3.7, color: "text-red-500" },
                  { label: "PII", count: 18, percentage: 2.1, color: "text-orange-500" },
                  { label: "Bias", count: 54, percentage: 6.3, color: "text-yellow-500" },
                  { label: "Behavior", count: 30, percentage: 3.5, color: "text-blue-500" },
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
          <CardTitle>Test History</CardTitle>
          <CardDescription>Search and filter historical test runs</CardDescription>
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
                      <Button variant="ghost" size="sm">
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
    </div>
  )
}
