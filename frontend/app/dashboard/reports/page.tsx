"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart3,
  Download,
  Calendar,
  TrendingUp,
  TrendingDown,
  Shield,
  Target,
  FileText,
  Zap,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts"

const testHistory = [
  { date: "2025-01-10", module: "Prompt Injection", passed: 18, failed: 6, total: 24 },
  { date: "2025-01-11", module: "Jailbreak", passed: 15, failed: 3, total: 18 },
  { date: "2025-01-12", module: "Data Extraction", passed: 13, failed: 2, total: 15 },
  { date: "2025-01-13", module: "Adversarial", passed: 19, failed: 2, total: 21 },
  { date: "2025-01-14", module: "Prompt Injection", passed: 20, failed: 4, total: 24 },
  { date: "2025-01-15", module: "Jailbreak", passed: 16, failed: 2, total: 18 },
]

const weeklyData = [
  { week: "Week 1", tests: 120, passed: 98, failed: 22 },
  { week: "Week 2", tests: 145, passed: 125, failed: 20 },
  { week: "Week 3", tests: 168, passed: 152, failed: 16 },
  { week: "Week 4", tests: 189, passed: 175, failed: 14 },
]

const moduleDistribution = [
  { name: "Prompt Injection", value: 35, color: "hsl(var(--chart-1))" },
  { name: "Jailbreak", value: 25, color: "hsl(var(--chart-2))" },
  { name: "Data Extraction", value: 20, color: "hsl(var(--chart-3))" },
  { name: "Adversarial", value: 20, color: "hsl(var(--chart-4))" },
]

const vulnerabilities = [
  {
    id: 1,
    severity: "high",
    module: "Prompt Injection",
    description: "System prompt can be partially extracted using delimiter escape",
    date: "2025-01-14",
    status: "open",
  },
  {
    id: 2,
    severity: "medium",
    module: "Jailbreak",
    description: "Role-play scenarios occasionally bypass content filters",
    date: "2025-01-13",
    status: "investigating",
  },
  {
    id: 3,
    severity: "critical",
    module: "Data Extraction",
    description: "Training data memorization detected in edge cases",
    date: "2025-01-12",
    status: "resolved",
  },
]

export default function ReportsPage() {
  const [timeRange, setTimeRange] = useState("30d")

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Reports</h1>
          <p className="text-muted-foreground mt-2">
            Comprehensive analysis of your LLM security testing results and trends.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[140px]">
              <Calendar className="mr-2 size-4" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button>
            <Download className="mr-2 size-4" />
            Export Report
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
            <BarChart3 className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
            <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
              <TrendingUp className="size-3" />
              +12% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle2 className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
              <TrendingUp className="size-3" />
              +2.1% improvement
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vulnerabilities</CardTitle>
            <AlertTriangle className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">23</div>
            <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
              <TrendingDown className="size-3" />
              -8% reduction
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Zap className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.2s</div>
            <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
              <TrendingDown className="size-3" />
              -0.3s faster
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="vulnerabilities">Vulnerabilities</TabsTrigger>
          <TabsTrigger value="history">Test History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Weekly Test Performance</CardTitle>
                <CardDescription>Test results over the last 4 weeks</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis dataKey="week" className="text-xs" />
                    <YAxis className="text-xs" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--popover))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "var(--radius)",
                      }}
                    />
                    <Bar dataKey="passed" fill="hsl(var(--chart-1))" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="failed" fill="hsl(var(--chart-5))" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Test Distribution by Module</CardTitle>
                <CardDescription>Breakdown of tests across attack modules</CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={moduleDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {moduleDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Success Rate Trend</CardTitle>
              <CardDescription>Track your security posture improvement over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="week" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--popover))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "var(--radius)",
                    }}
                  />
                  <Line type="monotone" dataKey="passed" stroke="hsl(var(--chart-1))" strokeWidth={2} />
                  <Line type="monotone" dataKey="failed" stroke="hsl(var(--chart-5))" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vulnerabilities" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detected Vulnerabilities</CardTitle>
              <CardDescription>Security issues identified during testing</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {vulnerabilities.map((vuln) => (
                  <div key={vuln.id} className="flex items-start gap-4 p-4 border rounded-lg">
                    <div
                      className={`size-10 rounded-full flex items-center justify-center shrink-0 ${
                        vuln.severity === "critical"
                          ? "bg-destructive/10"
                          : vuln.severity === "high"
                            ? "bg-orange-500/10"
                            : "bg-yellow-500/10"
                      }`}
                    >
                      <AlertTriangle
                        className={`size-5 ${
                          vuln.severity === "critical"
                            ? "text-destructive"
                            : vuln.severity === "high"
                              ? "text-orange-500"
                              : "text-yellow-500"
                        }`}
                      />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant={vuln.severity === "critical" ? "destructive" : "default"} className="text-xs">
                          {vuln.severity}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {vuln.module}
                        </Badge>
                        <span className="text-xs text-muted-foreground ml-auto">{vuln.date}</span>
                      </div>
                      <p className="text-sm font-medium">{vuln.description}</p>
                      <Badge
                        variant={
                          vuln.status === "resolved"
                            ? "outline"
                            : vuln.status === "investigating"
                              ? "secondary"
                              : "default"
                        }
                        className="text-xs"
                      >
                        {vuln.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Test Runs</CardTitle>
              <CardDescription>Detailed history of all security tests</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {testHistory.map((test, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="size-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        {test.module === "Prompt Injection" && <Target className="size-5 text-primary" />}
                        {test.module === "Jailbreak" && <Shield className="size-5 text-primary" />}
                        {test.module === "Data Extraction" && <FileText className="size-5 text-primary" />}
                        {test.module === "Adversarial" && <Zap className="size-5 text-primary" />}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{test.module}</p>
                        <p className="text-xs text-muted-foreground">{test.date}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-medium">
                          {test.passed}/{test.total} passed
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {Math.round((test.passed / test.total) * 100)}% success
                        </p>
                      </div>
                      <Button variant="ghost" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
