"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Brain, AlertTriangle, Database, TrendingUp } from "lucide-react"

const mockPatterns = [
  {
    id: "1",
    name: "GPT-4 Instruction Override Pattern",
    description: "Pattern detected in attempts to override system instructions",
    count: 45,
    confidence: 96,
    frequency: 3.2,
    firstSeen: "2024-01-10",
    lastSeen: "2 minutes ago",
    severity: "critical" as const,
  },
  {
    id: "2",
    name: "DAN Variant Evolution",
    description: "New variations of Do Anything Now jailbreak technique",
    count: 28,
    confidence: 89,
    frequency: 2.1,
    firstSeen: "2024-01-12",
    lastSeen: "15 minutes ago",
    severity: "high" as const,
  },
  {
    id: "3",
    name: "Data Extraction via Translation",
    description: "Attempts to extract training data through translation prompts",
    count: 12,
    confidence: 78,
    frequency: 0.8,
    firstSeen: "2024-01-14",
    lastSeen: "1 hour ago",
    severity: "medium" as const,
  },
]

export function ThreatIntelligenceContent() {
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
        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Threat Intelligence</h1>
          <p className="text-muted-foreground">Threat pattern detection and attack vector analysis</p>
        </div>
        <div className="ml-auto text-right">
          <div className="text-sm text-muted-foreground">Last Updated</div>
          <div className="font-semibold">2 minutes ago</div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
            <AlertTriangle className="h-8 w-8 opacity-50 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">23</div>
            <p className="text-xs text-muted-foreground mt-2">
              Critical: <span className="text-red-500">8</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500/10 to-transparent border-orange-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New Threats (24h)</CardTitle>
            <TrendingUp className="h-8 w-8 opacity-50 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">7</div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-orange-500">↑ 12%</span> from yesterday
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-transparent border-purple-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Patterns Detected</CardTitle>
            <Brain className="h-8 w-8 opacity-50 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">156</div>
            <p className="text-xs text-muted-foreground mt-2">
              Confidence: <span className="text-green-500">89%</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database Size</CardTitle>
            <Database className="h-8 w-8 opacity-50 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">3,247</div>
            <p className="text-xs text-muted-foreground mt-2">Known threat signatures</p>
          </CardContent>
        </Card>
      </div>

      {/* Threat Patterns */}
      <Card>
        <CardHeader>
          <CardTitle>Detected Threat Patterns</CardTitle>
          <CardDescription>Active threat patterns and attack vectors detected in the last 24 hours</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockPatterns.map((pattern) => (
              <Card key={pattern.id} className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <Badge className={`${getSeverityColor(pattern.severity)} text-white`}>{pattern.severity}</Badge>
                    <Badge variant="outline">{pattern.confidence}% confidence</Badge>
                  </div>
                  <h3 className="font-semibold mb-2">{pattern.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{pattern.description}</p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Occurrences</span>
                      <span className="font-semibold">{pattern.count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Frequency</span>
                      <span className="font-semibold">{pattern.frequency}/hr</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">First Seen</span>
                      <span className="font-semibold">{pattern.firstSeen}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Last Seen</span>
                      <span className="font-semibold">{pattern.lastSeen}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
