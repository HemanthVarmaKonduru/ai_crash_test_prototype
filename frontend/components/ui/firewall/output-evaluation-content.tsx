"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileCheck, CheckCircle2, FileEdit, Clock } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

const safetyScoreData = [
  { range: "0-20", count: 5, midpoint: 10 },
  { range: "20-40", count: 12, midpoint: 30 },
  { range: "40-60", count: 28, midpoint: 50 },
  { range: "60-80", count: 145, midpoint: 70 },
  { range: "80-100", count: 998, midpoint: 90 },
]

export function OutputEvaluationContent() {
  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center">
          <FileCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Output Evaluation</h1>
          <p className="text-muted-foreground">
            Evaluate LLM responses after generation. Detect unsafe or low-quality content.
          </p>
        </div>
        <Badge className="bg-green-500 text-white ml-auto">Active</Badge>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked Today</CardTitle>
            <FileCheck className="h-8 w-8 opacity-50 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-red-600">34</div>
            <p className="text-xs text-muted-foreground mt-2">
              Block rate: <span className="text-red-500">2.9%</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-500/10 to-transparent border-orange-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sanitized Today</CardTitle>
            <FileEdit className="h-8 w-8 opacity-50 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-orange-600">67</div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-orange-500">12 methods used</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Allowed Today</CardTitle>
            <CheckCircle2 className="h-8 w-8 opacity-50 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-600">1,088</div>
            <p className="text-xs text-muted-foreground mt-2">
              Avg safety score: <span className="text-green-500">92%</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Latency Average</CardTitle>
            <Clock className="h-8 w-8 opacity-50 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-500">18ms</div>
            <p className="text-xs text-muted-foreground mt-2">
              P95: <span>32ms</span>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Safety Score Distribution Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Safety Score Distribution</CardTitle>
          <CardDescription>Distribution of output safety scores over the last 24 hours</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={safetyScoreData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
            <div>
              <div className="text-sm text-muted-foreground">Average Score</div>
              <div className="text-2xl font-bold text-green-500">87.3%</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Median Score</div>
              <div className="text-2xl font-bold">89%</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Below Threshold</div>
              <div className="text-2xl font-bold text-red-500">101</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
