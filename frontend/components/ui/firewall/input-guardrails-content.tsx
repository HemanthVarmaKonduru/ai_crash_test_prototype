"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ShieldCheck, Clock, CheckCircle2, Eye, Search, Loader2, AlertCircle } from "lucide-react"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { evaluateInput, type BlockedInput, type FirewallStats } from "@/lib/firewall-api"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"

// Local storage key for blocked inputs
const BLOCKED_INPUTS_STORAGE_KEY = "firewall_blocked_inputs"
const STATS_STORAGE_KEY = "firewall_stats"

// Helper to format threat type for display
const formatThreatType = (threatType: string): string => {
  return threatType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

export function InputGuardrailsContent() {
  const [searchQuery, setSearchQuery] = useState("")
  const [promptInjectionEnabled, setPromptInjectionEnabled] = useState(true)
  const [promptInjectionThreshold, setPromptInjectionThreshold] = useState([95])
  const [jailbreakEnabled, setJailbreakEnabled] = useState(true)
  const [jailbreakThreshold, setJailbreakThreshold] = useState([95])
  const [piiEnabled, setPiiEnabled] = useState(true)
  const [rateLimitEnabled, setRateLimitEnabled] = useState(true)
  
  // API integration state
  const [blockedInputs, setBlockedInputs] = useState<BlockedInput[]>([])
  const [stats, setStats] = useState<FirewallStats>({
    blockedToday: 0,
    allowedToday: 0,
    pendingQueue: 0,
    latencyAverage: 0,
    latencyP95: 0,
    blockRate: 0,
    falsePositives: 0,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Test input state
  const [testInput, setTestInput] = useState("")
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const [showTestDialog, setShowTestDialog] = useState(false)
  
  // View details state
  const [selectedInput, setSelectedInput] = useState<BlockedInput | null>(null)
  const [showDetailsDialog, setShowDetailsDialog] = useState(false)

  // Load blocked inputs from localStorage on mount and listen for updates
  useEffect(() => {
    const loadData = () => {
      try {
        const stored = localStorage.getItem(BLOCKED_INPUTS_STORAGE_KEY)
        if (stored) {
          const parsed = JSON.parse(stored)
          setBlockedInputs(parsed)
        }
        
        const storedStats = localStorage.getItem(STATS_STORAGE_KEY)
        if (storedStats) {
          const parsedStats = JSON.parse(storedStats)
          setStats(parsedStats)
        }
      } catch (err) {
        console.error("Error loading stored data:", err)
      }
    }
    
    // Load on mount
    loadData()
    
    // Listen for storage events (from chat module or other tabs)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === BLOCKED_INPUTS_STORAGE_KEY && e.newValue) {
        try {
          const parsed = JSON.parse(e.newValue)
          setBlockedInputs(parsed)
        } catch (err) {
          console.error("Error parsing blocked inputs from storage event:", err)
        }
      }
      if (e.key === STATS_STORAGE_KEY && e.newValue) {
        try {
          const parsed = JSON.parse(e.newValue)
          setStats(parsed)
        } catch (err) {
          console.error("Error parsing stats from storage event:", err)
        }
      }
    }
    
    // Also listen for custom events (for same-tab updates)
    const handleCustomStorageUpdate = () => {
      loadData()
    }
    
    window.addEventListener('storage', handleStorageChange)
    window.addEventListener('firewall-storage-update', handleCustomStorageUpdate)
    
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('firewall-storage-update', handleCustomStorageUpdate)
    }
  }, [])

  // Save blocked inputs to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(BLOCKED_INPUTS_STORAGE_KEY, JSON.stringify(blockedInputs))
    } catch (err) {
      console.error("Error saving blocked inputs:", err)
    }
  }, [blockedInputs])

  // Save stats to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(STATS_STORAGE_KEY, JSON.stringify(stats))
    } catch (err) {
      console.error("Error saving stats:", err)
    }
  }, [stats])

  // Test input function
  const handleTestInput = useCallback(async () => {
    if (!testInput.trim()) {
      setError("Please enter some text to test")
      return
    }

    setTesting(true)
    setError(null)
    setTestResult(null)

    try {
      const response = await evaluateInput({
        input_text: testInput,
        user_id: `test_${Date.now()}`,
        session_id: `session_${Date.now()}`,
      })

      setTestResult(response)
      setShowTestDialog(true)

      // If blocked or sanitized, add to blocked inputs list
      if (response.decision === "blocked" || response.decision === "sanitized") {
        const newBlockedInput: BlockedInput = {
          id: response.evaluation_id,
          timestamp: new Date().toLocaleString(),
          threatType: response.threat_detected ? formatThreatType(response.threat_detected) : "Unknown",
          severity: (response.severity?.toLowerCase() || "medium") as "critical" | "high" | "medium" | "low",
          confidence: Math.round(response.confidence * 100),
          action: response.decision as "blocked" | "sanitized" | "throttled",
          userId: `test_${Date.now()}`,
          preview: testInput.length > 50 ? testInput.substring(0, 50) + "..." : testInput,
          inputText: testInput,
          evaluationId: response.evaluation_id,
          userMessage: response.user_message || undefined,
        }

        setBlockedInputs((prev) => [newBlockedInput, ...prev].slice(0, 100)) // Keep last 100

        // Update stats
        setStats((prev) => ({
          ...prev,
          blockedToday: prev.blockedToday + 1,
          blockRate: prev.blockedToday + prev.allowedToday > 0 
            ? ((prev.blockedToday + 1) / (prev.blockedToday + prev.allowedToday + 1)) * 100 
            : 0,
          latencyAverage: prev.latencyAverage > 0 
            ? (prev.latencyAverage + response.latency_ms) / 2 
            : response.latency_ms,
        }))
      } else {
        // Update allowed count
        setStats((prev) => ({
          ...prev,
          allowedToday: prev.allowedToday + 1,
          blockRate: prev.blockedToday + prev.allowedToday > 0 
            ? (prev.blockedToday / (prev.blockedToday + prev.allowedToday + 1)) * 100 
            : 0,
          latencyAverage: prev.latencyAverage > 0 
            ? (prev.latencyAverage + response.latency_ms) / 2 
            : response.latency_ms,
        }))
      }
    } catch (err) {
      console.error("Error testing input:", err)
      setError(err instanceof Error ? err.message : "Failed to evaluate input")
    } finally {
      setTesting(false)
    }
  }, [testInput])

  // Filter blocked inputs based on search and selected tab
  const filteredInputs = blockedInputs.filter((input) => {
    const matchesSearch = 
      searchQuery === "" ||
      input.userId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      input.preview.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (input.inputText && input.inputText.toLowerCase().includes(searchQuery.toLowerCase()))
    
    return matchesSearch
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-500"
      case "high":
        return "bg-orange-500"
      case "medium":
        return "bg-yellow-500"
      case "low":
        return "bg-blue-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Input Guardrails</h1>
          <p className="text-muted-foreground">
            Evaluate user prompts before sending to LLM. Block malicious inputs in real-time.
          </p>
        </div>
        <Badge className="bg-green-500 text-white ml-auto">Active</Badge>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Test Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Test Input</CardTitle>
          <CardDescription>Test any input text against the guardrails</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Enter text to test..."
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleTestInput()
                }
              }}
              disabled={testing}
            />
            <Button onClick={handleTestInput} disabled={testing || !testInput.trim()}>
              {testing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Testing...
                </>
              ) : (
                "Test"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked Today</CardTitle>
            <ShieldCheck className="h-8 w-8 opacity-50 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-red-600">{stats.blockedToday}</div>
            <p className="text-xs text-muted-foreground mt-2">
              Block rate: <span className="text-red-500">{stats.blockRate.toFixed(1)}%</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Allowed Today</CardTitle>
            <CheckCircle2 className="h-8 w-8 opacity-50 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-600">{stats.allowedToday}</div>
            <p className="text-xs text-muted-foreground mt-2">
              False positives: <span className="text-yellow-500">{stats.falsePositives}</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Queue</CardTitle>
            <Clock className="h-8 w-8 opacity-50 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{stats.pendingQueue}</div>
            <p className="text-xs text-muted-foreground mt-2">
              Avg wait: <span className="text-green-500">{stats.latencyAverage.toFixed(0)}ms</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Latency Average</CardTitle>
            <Clock className="h-8 w-8 opacity-50 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-500">{stats.latencyAverage.toFixed(0)}ms</div>
            <p className="text-xs text-muted-foreground mt-2">
              P95: <span>{stats.latencyP95.toFixed(0)}ms</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All Threats</TabsTrigger>
          <TabsTrigger value="prompt-injection">Prompt Injection</TabsTrigger>
          <TabsTrigger value="jailbreak">Jailbreak</TabsTrigger>
          <TabsTrigger value="pii">PII</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {/* Content Area - 2 Columns */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Detection Rules Configuration Panel - Left Side (1 col) */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle>Detection Rules</CardTitle>
                <CardDescription>Configure input validation rules</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[600px] pr-4">
                  <Accordion type="single" collapsible className="w-full">
                    {/* Prompt Injection Detection */}
                    <AccordionItem value="prompt-injection">
                      <AccordionTrigger>Prompt Injection Detection</AccordionTrigger>
                      <AccordionContent className="space-y-4">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="prompt-injection-enabled">Enable</Label>
                          <Switch
                            id="prompt-injection-enabled"
                            checked={promptInjectionEnabled}
                            onCheckedChange={setPromptInjectionEnabled}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Block Threshold: {promptInjectionThreshold}%</Label>
                          <Slider
                            value={promptInjectionThreshold}
                            onValueChange={setPromptInjectionThreshold}
                            max={100}
                            step={5}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Action</Label>
                          <Select defaultValue="block">
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="block">Block</SelectItem>
                              <SelectItem value="allow">Allow</SelectItem>
                              <SelectItem value="log">Log Only</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </AccordionContent>
                    </AccordionItem>

                    {/* Jailbreak Detection */}
                    <AccordionItem value="jailbreak">
                      <AccordionTrigger>Jailbreak Detection</AccordionTrigger>
                      <AccordionContent className="space-y-4">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="jailbreak-enabled">Enable</Label>
                          <Switch
                            id="jailbreak-enabled"
                            checked={jailbreakEnabled}
                            onCheckedChange={setJailbreakEnabled}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Block Threshold: {jailbreakThreshold}%</Label>
                          <Slider value={jailbreakThreshold} onValueChange={setJailbreakThreshold} max={100} step={5} />
                        </div>
                        <div className="space-y-2">
                          <Label>Action</Label>
                          <Select defaultValue="block">
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="block">Block</SelectItem>
                              <SelectItem value="allow">Allow</SelectItem>
                              <SelectItem value="log">Log Only</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </AccordionContent>
                    </AccordionItem>

                    {/* PII Detection */}
                    <AccordionItem value="pii">
                      <AccordionTrigger>PII Detection</AccordionTrigger>
                      <AccordionContent className="space-y-4">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="pii-enabled">Enable</Label>
                          <Switch id="pii-enabled" checked={piiEnabled} onCheckedChange={setPiiEnabled} />
                        </div>
                        <div className="space-y-2">
                          <Label>Action</Label>
                          <Select defaultValue="sanitize">
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="block">Block</SelectItem>
                              <SelectItem value="sanitize">Sanitize</SelectItem>
                              <SelectItem value="log">Log Only</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>PII Types</Label>
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Switch id="ssn" defaultChecked />
                              <Label htmlFor="ssn">SSN</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Switch id="credit-card" defaultChecked />
                              <Label htmlFor="credit-card">Credit Card</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Switch id="email" defaultChecked />
                              <Label htmlFor="email">Email</Label>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Switch id="phone" defaultChecked />
                              <Label htmlFor="phone">Phone Number</Label>
                            </div>
                          </div>
                        </div>
                      </AccordionContent>
                    </AccordionItem>

                    {/* Rate Limiting */}
                    <AccordionItem value="rate-limiting">
                      <AccordionTrigger>Rate Limiting</AccordionTrigger>
                      <AccordionContent className="space-y-4">
                        <div className="flex items-center justify-between">
                          <Label htmlFor="rate-limit-enabled">Enable</Label>
                          <Switch id="rate-limit-enabled" checked={rateLimitEnabled} onCheckedChange={setRateLimitEnabled} />
                        </div>
                        <div className="space-y-2">
                          <Label>Requests per Minute</Label>
                          <Input type="number" defaultValue="60" />
                        </div>
                        <div className="space-y-2">
                          <Label>Action</Label>
                          <Select defaultValue="throttle">
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="block">Block</SelectItem>
                              <SelectItem value="throttle">Throttle</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
                </ScrollArea>
                <div className="flex space-x-2 mt-4 pt-4 border-t">
                  <Button className="flex-1" onClick={() => setError("Configuration updates coming soon")}>
                    Save Changes
                  </Button>
                  <Button variant="outline" className="flex-1 bg-transparent">
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Blocks Feed - Right Side (2 cols) */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Recent Blocks</CardTitle>
                <CardDescription>Real-time blocked inputs feed</CardDescription>
                <div className="flex items-center space-x-2 mt-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Search by user ID or prompt text..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select defaultValue="all">
                    <SelectTrigger className="w-[150px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Severities</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                {filteredInputs.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No blocked inputs yet. Test an input to see results here.
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Timestamp</TableHead>
                        <TableHead>Threat Type</TableHead>
                        <TableHead>Severity</TableHead>
                        <TableHead>Confidence</TableHead>
                        <TableHead>Action</TableHead>
                        <TableHead>User ID</TableHead>
                        <TableHead></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredInputs.map((input) => (
                        <TableRow key={input.id}>
                          <TableCell className="font-mono text-xs">{input.timestamp}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{input.threatType}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={`${getSeverityColor(input.severity)} text-white`}>{input.severity}</Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500" style={{ width: `${input.confidence}%` }} />
                              </div>
                              <span className="text-xs">{input.confidence}%</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={
                                input.action === "blocked"
                                  ? "text-red-500"
                                  : input.action === "sanitized"
                                    ? "text-orange-500"
                                    : "text-green-500"
                              }
                            >
                              {input.action}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-xs">{input.userId}</TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedInput(input)
                                setShowDetailsDialog(true)
                              }}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Test Result Dialog */}
      <Dialog open={showTestDialog} onOpenChange={setShowTestDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Test Result</DialogTitle>
            <DialogDescription>Evaluation result for your input</DialogDescription>
          </DialogHeader>
          {testResult && (
            <div className="space-y-4">
              <div>
                <Label>Decision</Label>
                <Badge
                  className={
                    testResult.decision === "blocked"
                      ? "bg-red-500 text-white"
                      : testResult.decision === "sanitized"
                        ? "bg-orange-500 text-white"
                        : "bg-green-500 text-white"
                  }
                >
                  {testResult.decision.toUpperCase()}
                </Badge>
              </div>
              <div>
                <Label>Confidence</Label>
                <div className="flex items-center space-x-2">
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{ width: `${testResult.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-sm">{(testResult.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
              {testResult.threat_detected && (
                <div>
                  <Label>Threat Detected</Label>
                  <Badge variant="outline">{formatThreatType(testResult.threat_detected)}</Badge>
                </div>
              )}
              {testResult.severity && (
                <div>
                  <Label>Severity</Label>
                  <Badge className={getSeverityColor(testResult.severity)}>
                    {testResult.severity}
                  </Badge>
                </div>
              )}
              {testResult.user_message && (
                <div>
                  <Label>User Message</Label>
                  <p className="text-sm text-muted-foreground">{testResult.user_message}</p>
                </div>
              )}
              <div>
                <Label>Latency</Label>
                <p className="text-sm">{testResult.latency_ms.toFixed(2)}ms</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Details Dialog */}
      <Dialog open={showDetailsDialog} onOpenChange={setShowDetailsDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Input Details</DialogTitle>
            <DialogDescription>Full details of the blocked input</DialogDescription>
          </DialogHeader>
          {selectedInput && (
            <div className="space-y-4">
              <div>
                <Label>Input Text</Label>
                <p className="text-sm bg-muted p-2 rounded">{selectedInput.inputText || selectedInput.preview}</p>
              </div>
              <div>
                <Label>Threat Type</Label>
                <Badge variant="outline">{selectedInput.threatType}</Badge>
              </div>
              <div>
                <Label>Severity</Label>
                <Badge className={getSeverityColor(selectedInput.severity)}>
                  {selectedInput.severity}
                </Badge>
              </div>
              <div>
                <Label>Confidence</Label>
                <p className="text-sm">{selectedInput.confidence}%</p>
              </div>
              <div>
                <Label>Action</Label>
                <Badge variant="outline">{selectedInput.action}</Badge>
              </div>
              {selectedInput.userMessage && (
                <div>
                  <Label>User Message</Label>
                  <p className="text-sm text-muted-foreground">{selectedInput.userMessage}</p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
