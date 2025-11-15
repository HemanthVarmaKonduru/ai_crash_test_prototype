"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Target, Shield, FileText, Zap, Clock, DollarSign, Coins, Activity, CheckCircle2, Download, BarChart3 } from "lucide-react"
import {
  Bar,
  BarChart,
  Area,
  AreaChart,
  Pie,
  PieChart,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import apiConfig from "@/lib/api-config"

// Module type mapping
const MODULE_TYPE_MAP: Record<string, string> = {
  prompt_injection: "Prompt Injection",
  jailbreak: "Jailbreak Detection",
  data_extraction: "Data Extraction",
  adversarial_attacks: "Adversarial Attacks",
}

// Module icons
const MODULE_ICONS: Record<string, any> = {
  "Prompt Injection": Target,
  "Jailbreak Detection": Shield,
  "Data Extraction": FileText,
  "Adversarial Attacks": Zap,
}

// Module colors
const MODULE_COLORS: Record<string, string> = {
  "Prompt Injection": "#6366f1",
  "Jailbreak Detection": "#ec4899",
  "Data Extraction": "#06b6d4",
  "Adversarial Attacks": "#a855f7",
}

// Default mock data (fallback)
const moduleStats = [
  {
    module: "Prompt Injection",
    icon: Target,
    totalTests: 342,
    prompts: 1247,
    successful: 318,
    failures: 24,
    avgResponseTime: 1.2,
    avgEvalTime: 0.8,
    avgTestTime: 2.1,
    totalCost: 45.32,
    totalTokens: 125430,
    avgTokensPerRun: 367,
    color: "#6366f1",
    gradient: "from-indigo-500/10 to-purple-500/10",
  },
  {
    module: "Jailbreak Detection",
    icon: Shield,
    totalTests: 289,
    prompts: 1089,
    successful: 267,
    failures: 22,
    avgResponseTime: 1.5,
    avgEvalTime: 1.1,
    avgTestTime: 2.8,
    totalCost: 52.18,
    totalTokens: 143890,
    avgTokensPerRun: 498,
    color: "#ec4899",
    gradient: "from-pink-500/10 to-rose-500/10",
  },
  {
    module: "Data Extraction",
    icon: FileText,
    totalTests: 256,
    prompts: 892,
    successful: 241,
    failures: 15,
    avgResponseTime: 1.0,
    avgEvalTime: 0.6,
    avgTestTime: 1.7,
    totalCost: 38.76,
    totalTokens: 98234,
    avgTokensPerRun: 384,
    color: "#06b6d4",
    gradient: "from-cyan-500/10 to-blue-500/10",
  },
  {
    module: "Adversarial Attacks",
    icon: Zap,
    totalTests: 360,
    prompts: 1456,
    successful: 332,
    failures: 28,
    avgResponseTime: 1.8,
    avgEvalTime: 1.3,
    avgTestTime: 3.2,
    totalCost: 67.94,
    totalTokens: 187650,
    avgTokensPerRun: 521,
    color: "#a855f7",
    gradient: "from-purple-500/10 to-indigo-500/10",
  },
]

// Calculate totals
const totals = {
  tests: moduleStats.reduce((sum, m) => sum + m.totalTests, 0),
  prompts: moduleStats.reduce((sum, m) => sum + m.prompts, 0),
  successful: moduleStats.reduce((sum, m) => sum + m.successful, 0),
  failures: moduleStats.reduce((sum, m) => sum + m.failures, 0),
  cost: moduleStats.reduce((sum, m) => sum + m.totalCost, 0),
  tokens: moduleStats.reduce((sum, m) => sum + m.totalTokens, 0),
}

// Time series data for trends
const timeSeriesData = [
  { date: "Jan", promptInjection: 45, jailbreak: 38, dataExtraction: 32, adversarial: 52 },
  { date: "Feb", promptInjection: 52, jailbreak: 42, dataExtraction: 38, adversarial: 58 },
  { date: "Mar", promptInjection: 61, jailbreak: 48, dataExtraction: 41, adversarial: 65 },
  { date: "Apr", promptInjection: 58, jailbreak: 51, dataExtraction: 45, adversarial: 62 },
  { date: "May", promptInjection: 67, jailbreak: 55, dataExtraction: 48, adversarial: 71 },
  { date: "Jun", promptInjection: 72, jailbreak: 59, dataExtraction: 52, adversarial: 74 },
]

// Success rate comparison data
const successRateData = moduleStats.map((m) => ({
  module: m.module.split(" ")[0],
  successRate: ((m.successful / m.totalTests) * 100).toFixed(1),
  failureRate: ((m.failures / m.totalTests) * 100).toFixed(1),
}))

// Cost breakdown pie chart data
const costBreakdownData = moduleStats.map((m) => ({
  name: m.module.split(" ")[0],
  value: m.totalCost,
  color: m.color,
}))

// Token consumption data
const tokenConsumptionData = moduleStats.map((m) => ({
  module: m.module.split(" ")[0],
  tokens: m.totalTokens / 1000, // Convert to K
  avgPerRun: m.avgTokensPerRun,
}))

// Response time comparison
const responseTimeData = moduleStats.map((m) => ({
  module: m.module.split(" ")[0],
  response: m.avgResponseTime,
  evaluation: m.avgEvalTime,
  total: m.avgTestTime,
}))

export default function EvalsPage() {
  const [analyticsData, setAnalyticsData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const response = await fetch(apiConfig.endpoints.analytics.summary)
        if (response.ok) {
          const data = await response.json()
          setAnalyticsData(data)
        }
      } catch (error) {
        console.error("Failed to fetch analytics:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchAnalytics()
  }, [])

  // Transform API data to match UI structure
  const transformAnalyticsData = () => {
    if (!analyticsData || !analyticsData.by_module) {
      return { moduleStats: moduleStats, totals: totals }
    }

    const transformedModules = Object.entries(analyticsData.by_module).map(([moduleType, stats]: [string, any]) => {
      const moduleName = MODULE_TYPE_MAP[moduleType] || moduleType
      const Icon = MODULE_ICONS[moduleName] || Activity
      const color = MODULE_COLORS[moduleName] || "#6366f1"

      return {
        module: moduleName,
        icon: Icon,
        totalTests: stats.total_tests || 0,
        prompts: stats.total_prompts || 0,
        successful: stats.successful || 0,
        failures: stats.failures || 0,
        avgResponseTime: stats.avg_response_time || 0,
        avgEvalTime: 0, // Not directly available, could calculate from test runs
        avgTestTime: stats.average_time || 0,
        totalCost: stats.total_cost || 0,
        totalTokens: stats.total_tokens || 0,
        avgTokensPerRun: stats.average_tokens || 0,
        color: color,
        gradient: `from-${color.replace('#', '')}-500/10 to-${color.replace('#', '')}-500/10`,
      }
    })

    // Calculate totals
    const calculatedTotals = {
      tests: transformedModules.reduce((sum, m) => sum + m.totalTests, 0),
      prompts: transformedModules.reduce((sum, m) => sum + m.prompts, 0),
      successful: transformedModules.reduce((sum, m) => sum + m.successful, 0),
      failures: transformedModules.reduce((sum, m) => sum + m.failures, 0),
      cost: transformedModules.reduce((sum, m) => sum + m.totalCost, 0),
      tokens: transformedModules.reduce((sum, m) => sum + m.totalTokens, 0),
    }

    return {
      moduleStats: transformedModules.length > 0 ? transformedModules : moduleStats,
      totals: calculatedTotals.tests > 0 ? calculatedTotals : totals,
    }
  }

  const { moduleStats: displayModuleStats, totals: displayTotals } = transformAnalyticsData()

  // Recalculate derived data
  const successRateData = displayModuleStats.map((m: any) => ({
    module: m.module.split(" ")[0],
    successRate: m.prompts > 0 ? ((m.successful / m.prompts) * 100).toFixed(1) : "0",
    failureRate: m.prompts > 0 ? ((m.failures / m.prompts) * 100).toFixed(1) : "0",
  }))

  const costBreakdownData = displayModuleStats.map((m: any) => ({
    name: m.module.split(" ")[0],
    value: m.totalCost,
    color: m.color,
  }))

  const tokenConsumptionData = displayModuleStats.map((m: any) => ({
    module: m.module.split(" ")[0],
    tokens: m.totalTokens / 1000, // Convert to K
    avgPerRun: m.avgTokensPerRun,
  }))

  const responseTimeData = displayModuleStats.map((m: any) => ({
    module: m.module.split(" ")[0],
    response: m.avgResponseTime,
    evaluation: m.avgEvalTime,
    total: m.avgTestTime,
  }))

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-muted-foreground">Loading analytics...</div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="size-6 text-primary" />
            <h1 className="text-3xl font-bold tracking-tight">Evals & Analytics</h1>
          </div>
          <p className="text-muted-foreground">Comprehensive metrics and analytics across all testing modules</p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 size-4" />
          Export Report
        </Button>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tests Run</CardTitle>
            <Activity className="size-5 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{displayTotals.tests.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">Across all modules</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Prompts</CardTitle>
            <FileText className="size-5 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{displayTotals.prompts.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">Sent to models</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle2 className="size-5 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {displayTotals.prompts > 0 ? ((displayTotals.successful / displayTotals.prompts) * 100).toFixed(1) : "0"}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {displayTotals.successful} successful / {displayTotals.failures} failures
            </p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <DollarSign className="size-5 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">${displayTotals.cost.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground mt-1">LLM API costs</p>
          </CardContent>
        </Card>
      </div>

      {/* Module Performance Cards */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Module Performance</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {displayModuleStats.map((module: any) => (
            <Card key={module.module} className={`border-primary/20 bg-gradient-to-br ${module.gradient}`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-10 items-center justify-center rounded-lg bg-background/50 backdrop-blur-sm">
                      <module.icon className="size-5" style={{ color: module.color }} />
                    </div>
                    <CardTitle className="text-lg">{module.module}</CardTitle>
                  </div>
                  <Badge
                    variant="secondary"
                    style={{
                      backgroundColor: `${module.color}20`,
                      color: module.color,
                      borderColor: module.color,
                    }}
                  >
                    {module.prompts > 0 ? ((module.successful / module.prompts) * 100).toFixed(1) : "0"}% success
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Tests Run</p>
                    <p className="text-2xl font-bold">{module.totalTests}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Prompts</p>
                    <p className="text-2xl font-bold">{module.prompts.toLocaleString()}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Avg Response Time</p>
                    <p className="text-lg font-semibold">{module.avgResponseTime}s</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Avg Test Time</p>
                    <p className="text-lg font-semibold">{module.avgTestTime}s</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Total Cost</p>
                    <p className="text-lg font-semibold">${module.totalCost}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Tokens Used</p>
                    <p className="text-lg font-semibold">{(module.totalTokens / 1000).toFixed(1)}K</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Test Trends Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Test Trends Over Time</CardTitle>
            <CardDescription>Monthly test execution across modules</CardDescription>
          </CardHeader>
          <CardContent className="pb-4">
            <ChartContainer
              config={{
                promptInjection: { label: "Prompt Injection", color: "#6366f1" },
                jailbreak: { label: "Jailbreak", color: "#ec4899" },
                dataExtraction: { label: "Data Extraction", color: "#06b6d4" },
                adversarial: { label: "Adversarial", color: "#a855f7" },
              }}
              className="h-[280px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="promptInjection"
                    stackId="1"
                    stroke="#6366f1"
                    fill="#6366f1"
                    fillOpacity={0.6}
                    name="Prompt Injection"
                  />
                  <Area
                    type="monotone"
                    dataKey="jailbreak"
                    stackId="1"
                    stroke="#ec4899"
                    fill="#ec4899"
                    fillOpacity={0.6}
                    name="Jailbreak"
                  />
                  <Area
                    type="monotone"
                    dataKey="dataExtraction"
                    stackId="1"
                    stroke="#06b6d4"
                    fill="#06b6d4"
                    fillOpacity={0.6}
                    name="Data Extraction"
                  />
                  <Area
                    type="monotone"
                    dataKey="adversarial"
                    stackId="1"
                    stroke="#a855f7"
                    fill="#a855f7"
                    fillOpacity={0.6}
                    name="Adversarial"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Cost Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Cost Distribution</CardTitle>
            <CardDescription>Total API costs by module</CardDescription>
          </CardHeader>
          <CardContent className="pb-4">
            <ChartContainer
              config={{
                value: { label: "Cost", color: "hsl(var(--primary))" },
              }}
              className="h-[280px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={costBreakdownData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {costBreakdownData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Response Time Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Response Time Analysis</CardTitle>
            <CardDescription>Average times by module (seconds)</CardDescription>
          </CardHeader>
          <CardContent className="pb-4">
            <ChartContainer
              config={{
                response: { label: "Response Time", color: "#6366f1" },
                evaluation: { label: "Evaluation Time", color: "#ec4899" },
                total: { label: "Total Time", color: "#06b6d4" },
              }}
              className="h-[280px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={responseTimeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="module" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Bar dataKey="response" fill="#6366f1" name="Response Time" />
                  <Bar dataKey="evaluation" fill="#ec4899" name="Evaluation Time" />
                  <Bar dataKey="total" fill="#06b6d4" name="Total Time" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Token Consumption */}
        <Card>
          <CardHeader>
            <CardTitle>Token Consumption</CardTitle>
            <CardDescription>Total tokens used (in thousands)</CardDescription>
          </CardHeader>
          <CardContent className="pb-4">
            <ChartContainer
              config={{
                tokens: { label: "Total Tokens", color: "#a855f7" },
              }}
              className="h-[280px] w-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={tokenConsumptionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="module" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Bar dataKey="tokens" fill="#a855f7" name="Total Tokens (K)" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Additional Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Clock className="size-4 text-primary" />
              Average Response Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {displayModuleStats.length > 0 ? (displayModuleStats.reduce((sum: number, m: any) => sum + m.avgResponseTime, 0) / displayModuleStats.length).toFixed(2) : "0"}s
            </div>
            <p className="text-xs text-muted-foreground mt-1">Across all modules</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Coins className="size-4 text-primary" />
              Average Tokens Per Run
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {displayModuleStats.length > 0 ? Math.round(displayModuleStats.reduce((sum: number, m: any) => sum + m.avgTokensPerRun, 0) / displayModuleStats.length) : 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Per test execution</p>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <DollarSign className="size-4 text-primary" />
              Cost Per Test
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${displayTotals.tests > 0 ? (displayTotals.cost / displayTotals.tests).toFixed(3) : "0.000"}</div>
            <p className="text-xs text-muted-foreground mt-1">Average across all tests</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

