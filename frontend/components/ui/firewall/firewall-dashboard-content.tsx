"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import Link from "next/link"
import {
  Shield,
  Activity,
  AlertTriangle,
  Clock,
  ShieldCheck,
  FileCheck,
  Brain,
  BarChart3,
  Play,
  Pause,
  ChevronRight,
} from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts"

// Mock data for demonstration
const threatTrendsData = [
  { time: "00:00", total: 45, blocked: 38, allowed: 7 },
  { time: "04:00", total: 32, blocked: 25, allowed: 7 },
  { time: "08:00", total: 78, blocked: 65, allowed: 13 },
  { time: "12:00", total: 95, blocked: 82, allowed: 13 },
  { time: "16:00", total: 67, blocked: 54, allowed: 13 },
  { time: "20:00", total: 52, blocked: 41, allowed: 11 },
]

const sparklineData = Array.from({ length: 60 }, (_, i) => ({
  value: Math.floor(Math.random() * 50) + 20,
}))

const mockThreats = [
  {
    id: "1",
    type: "Prompt Injection",
    severity: "critical" as const,
    description: "Attempted system prompt override detected",
    timestamp: "2 minutes ago",
    action: "blocked" as const,
    confidence: 98,
  },
  {
    id: "2",
    type: "Jailbreak Attempt",
    severity: "high" as const,
    description: "DAN variant detected in user input",
    timestamp: "5 minutes ago",
    action: "blocked" as const,
    confidence: 94,
  },
  {
    id: "3",
    type: "PII Exposure",
    severity: "medium" as const,
    description: "Credit card pattern detected in output",
    timestamp: "8 minutes ago",
    action: "sanitized" as const,
    confidence: 87,
  },
  {
    id: "4",
    type: "Toxicity",
    severity: "low" as const,
    description: "Mild offensive content detected",
    timestamp: "12 minutes ago",
    action: "allowed" as const,
    confidence: 72,
  },
]

const firewallModules = [
  {
    id: "input-guardrails",
    title: "Input Guardrails",
    icon: ShieldCheck,
    url: "/dashboard/firewall/input-guardrails",
    status: "active" as const,
    todayCount: 1247,
    blockedCount: 89,
    avgLatency: 24,
    iconColor: "text-blue-500",
  },
  {
    id: "output-evaluation",
    title: "Output Evaluation",
    icon: FileCheck,
    url: "/dashboard/firewall/output-evaluation",
    status: "active" as const,
    todayCount: 1189,
    blockedCount: 34,
    avgLatency: 18,
    iconColor: "text-green-500",
  },
  {
    id: "threat-intelligence",
    title: "Threat Intelligence",
    icon: Brain,
    url: "/dashboard/firewall/threat-intelligence",
    status: "active" as const,
    todayCount: 456,
    blockedCount: 123,
    avgLatency: 8,
    iconColor: "text-purple-500",
  },
  {
    id: "incident-response",
    title: "Incident Response",
    icon: AlertTriangle,
    url: "/dashboard/firewall/incident-response",
    status: "active" as const,
    todayCount: 12,
    blockedCount: 8,
    avgLatency: 5,
    iconColor: "text-red-500",
  },
  {
    id: "analytics",
    title: "Analytics",
    icon: BarChart3,
    url: "/dashboard/firewall/analytics",
    status: "active" as const,
    todayCount: 2436,
    blockedCount: 0,
    avgLatency: 2,
    iconColor: "text-yellow-500",
  },
]

export function FirewallDashboardContent() {
  const [paused, setPaused] = useState(false)
  const [securityScore, setSecurityScore] = useState(94)
  const [requestCount, setRequestCount] = useState(1247)
  const [blockedCount, setBlockedCount] = useState(89)
  const [avgLatency, setAvgLatency] = useState(24)

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-500"
    if (score >= 70) return "text-yellow-500"
    if (score >= 50) return "text-orange-500"
    return "text-red-500"
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "border-red-500 bg-red-500/10"
      case "high":
        return "border-orange-500 bg-orange-500/10"
      case "medium":
        return "border-yellow-500 bg-yellow-500/10"
      case "low":
        return "border-blue-500 bg-blue-500/10"
      default:
        return "border-gray-500 bg-gray-500/10"
    }
  }

  const getSeverityBadgeColor = (severity: string) => {
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

  const getActionColor = (action: string) => {
    switch (action) {
      case "blocked":
        return "text-red-500"
      case "sanitized":
        return "text-orange-500"
      case "allowed":
        return "text-green-500"
      default:
        return "text-gray-500"
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Firewall Dashboard</h1>
            <p className="text-muted-foreground">
              Real-time security monitoring and threat protection for your AI applications
            </p>
          </div>
        </div>
        <Badge className="bg-green-500 text-white flex items-center space-x-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
          </span>
          <span>Active</span>
        </Badge>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Security Score Widget */}
        <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Score</CardTitle>
            <Shield className="h-8 w-8 opacity-50 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className={`text-4xl font-bold ${getScoreColor(securityScore)}`}>{securityScore}%</div>
            <div className="flex items-center space-x-2 mt-2">
              <Progress value={securityScore} className="h-2" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-green-500">↑ 2.1%</span> from last hour
            </p>
          </CardContent>
        </Card>

        {/* Real-Time Request Counter */}
        <Card className="bg-gradient-to-br from-indigo-500/10 to-transparent border-indigo-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Requests (Last Hour)</CardTitle>
            <Activity className="h-8 w-8 opacity-50 text-indigo-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{requestCount.toLocaleString()}</div>
            <div className="h-8 mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sparklineData}>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(var(--primary))"
                    fill="hsl(var(--primary))"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-green-500">{Math.floor(requestCount / 60)} req/min</span>
            </p>
          </CardContent>
        </Card>

        {/* Blocked Requests Widget */}
        <Card className="bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked Today</CardTitle>
            <Shield className="h-8 w-8 opacity-50 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-red-600">{blockedCount}</div>
            <div className="space-y-1 mt-2">
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-red-500 mr-2"></span>
                  Prompt Injection
                </span>
                <span className="font-medium">45</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-orange-500 mr-2"></span>
                  Jailbreak
                </span>
                <span className="font-medium">28</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>
                  PII
                </span>
                <span className="font-medium">16</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Block rate: <span className="text-red-500">{((blockedCount / requestCount) * 100).toFixed(1)}%</span>
            </p>
          </CardContent>
        </Card>

        {/* Average Latency Widget */}
        <Card className="bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Latency</CardTitle>
            <Clock className="h-8 w-8 opacity-50 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-4xl font-bold ${avgLatency < 50 ? "text-green-500" : avgLatency < 100 ? "text-yellow-500" : "text-red-500"}`}
            >
              {avgLatency}ms
            </div>
            <div className="space-y-1 mt-2">
              <div className="flex items-center justify-between text-xs">
                <span>P95</span>
                <span className="font-medium">42ms</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span>P99</span>
                <span className="font-medium">68ms</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Target: <span className="text-green-500">&lt;50ms</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Real-Time Threat Feed and Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Real-Time Threat Feed - Takes 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Real-Time Threat Feed</CardTitle>
                <CardDescription>Live security events and blocked threats</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => setPaused(!paused)}>
                {paused ? <Play className="w-4 h-4 mr-2" /> : <Pause className="w-4 h-4 mr-2" />}
                {paused ? "Resume" : "Pause"}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-3">
                {mockThreats.map((threat) => (
                  <Card
                    key={threat.id}
                    className={`border-l-4 ${getSeverityColor(threat.severity)} hover:bg-accent/50 transition-colors cursor-pointer`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <Badge className={`${getSeverityBadgeColor(threat.severity)} text-white text-xs`}>
                              {threat.severity}
                            </Badge>
                            <span className="font-semibold text-sm">{threat.type}</span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">{threat.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                            <span>{threat.timestamp}</span>
                            <Badge variant="outline" className={getActionColor(threat.action)}>
                              {threat.action}
                            </Badge>
                            <span>Confidence: {threat.confidence}%</span>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-muted-foreground ml-2" />
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Threat Trends Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Threat Trends</CardTitle>
            <CardDescription>Last 24 hours</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={threatTrendsData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="time" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Line type="monotone" dataKey="total" stroke="hsl(var(--primary))" strokeWidth={2} name="Total" />
                <Line type="monotone" dataKey="blocked" stroke="#ef4444" strokeWidth={2} name="Blocked" />
                <Line type="monotone" dataKey="allowed" stroke="#22c55e" strokeWidth={2} name="Allowed" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Module Status Grid */}
      <Card>
        <CardHeader>
          <CardTitle>Firewall Modules</CardTitle>
          <CardDescription>Real-time status of all firewall components</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {firewallModules.map((module) => (
              <Link key={module.id} href={module.url}>
                <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div
                        className={`w-10 h-10 rounded-lg bg-gradient-to-br from-${module.iconColor.replace("text-", "")}/10 to-transparent flex items-center justify-center`}
                      >
                        <module.icon className={`w-6 h-6 ${module.iconColor}`} />
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                        </span>
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      </div>
                    </div>
                    <h3 className="font-semibold mb-3">{module.title}</h3>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <div className="text-muted-foreground">Today</div>
                        <div className="font-semibold">{module.todayCount.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Blocked</div>
                        <div className="font-semibold text-red-500">{module.blockedCount}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Latency</div>
                        <div className="font-semibold">{module.avgLatency}ms</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
