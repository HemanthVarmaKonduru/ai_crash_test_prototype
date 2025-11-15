"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertTriangle, Clock, CheckCircle2, User } from "lucide-react"

const mockIncidents = [
  {
    id: "INC-001",
    type: "Coordinated Attack",
    severity: "critical" as const,
    status: "in-progress" as const,
    detectedAt: "2024-01-15 14:32:15",
    responseTime: "3",
    assignedTo: "John Doe",
  },
  {
    id: "INC-002",
    type: "Data Exfiltration Attempt",
    severity: "high" as const,
    status: "new" as const,
    detectedAt: "2024-01-15 14:15:42",
    responseTime: "N/A",
    assignedTo: "Unassigned",
  },
  {
    id: "INC-003",
    type: "Jailbreak Pattern",
    severity: "medium" as const,
    status: "resolved" as const,
    detectedAt: "2024-01-15 13:48:22",
    responseTime: "12",
    assignedTo: "Jane Smith",
  },
]

export function IncidentResponseContent() {
  const [selectedIncident, setSelectedIncident] = useState(mockIncidents[0])

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case "new":
        return "bg-blue-500"
      case "assigned":
        return "bg-purple-500"
      case "in-progress":
        return "bg-yellow-500"
      case "resolved":
        return "bg-green-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center">
          <AlertTriangle className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Incident Response</h1>
          <p className="text-muted-foreground">Manage and respond to security incidents</p>
        </div>
        <Badge className="bg-red-500 text-white ml-auto">2 Active</Badge>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Incidents</CardTitle>
            <AlertTriangle className="h-8 w-8 opacity-50 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">2</div>
            <p className="text-xs text-muted-foreground mt-2">
              Critical: <span className="text-red-500">1</span>
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolved Today</CardTitle>
            <CheckCircle2 className="h-8 w-8 opacity-50 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-600">12</div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-green-500">↑ 8%</span> from yesterday
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Clock className="h-8 w-8 opacity-50 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">8m</div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-green-500">↓ 2m</span> from last week
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-transparent border-purple-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
            <Clock className="h-8 w-8 opacity-50 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">45m</div>
            <p className="text-xs text-muted-foreground mt-2">
              <span className="text-green-500">↓ 12m</span> from last week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="active" className="space-y-4">
        <TabsList>
          <TabsTrigger value="active">
            Active
            <Badge className="ml-2 bg-red-500 text-white">2</Badge>
          </TabsTrigger>
          <TabsTrigger value="resolved">Resolved</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Incident List - Left Side */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Active Incidents</CardTitle>
                <CardDescription>Security incidents requiring immediate attention</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Incident ID</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Severity</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Detected At</TableHead>
                      <TableHead>Response Time</TableHead>
                      <TableHead>Assigned To</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockIncidents
                      .filter((inc) => inc.status !== "resolved")
                      .map((incident) => (
                        <TableRow
                          key={incident.id}
                          className="cursor-pointer hover:bg-accent"
                          onClick={() => setSelectedIncident(incident)}
                        >
                          <TableCell className="font-mono">{incident.id}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{incident.type}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={`${getSeverityColor(incident.severity)} text-white`}>
                              {incident.severity}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={`${getStatusColor(incident.status)} text-white`}>{incident.status}</Badge>
                          </TableCell>
                          <TableCell className="font-mono text-xs">{incident.detectedAt}</TableCell>
                          <TableCell>{incident.responseTime === "N/A" ? "N/A" : `${incident.responseTime}m`}</TableCell>
                          <TableCell>
                            {incident.assignedTo === "Unassigned" ? (
                              <Badge variant="outline">{incident.assignedTo}</Badge>
                            ) : (
                              <div className="flex items-center space-x-2">
                                <User className="w-4 h-4" />
                                <span>{incident.assignedTo}</span>
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            {/* Incident Details - Right Side */}
            <Card>
              <CardHeader>
                <CardTitle>Incident Details</CardTitle>
                <CardDescription>{selectedIncident.id}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="font-semibold mb-3">Overview</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">ID</span>
                      <span className="font-mono">{selectedIncident.id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Type</span>
                      <Badge variant="outline">{selectedIncident.type}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Severity</span>
                      <Badge className={`${getSeverityColor(selectedIncident.severity)} text-white`}>
                        {selectedIncident.severity}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Status</span>
                      <Badge className={`${getStatusColor(selectedIncident.status)} text-white`}>
                        {selectedIncident.status}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Response Actions</h3>
                  <div className="space-y-2">
                    <Button className="w-full" variant="default">
                      Assign to Me
                    </Button>
                    <Button className="w-full bg-transparent" variant="outline">
                      Update Status
                    </Button>
                    <Button className="w-full bg-transparent" variant="outline">
                      Resolve Incident
                    </Button>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Timeline</h3>
                  <div className="space-y-4">
                    <div className="flex space-x-3">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                        <div className="w-0.5 h-full bg-border"></div>
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="font-semibold text-sm">Incident Detected</div>
                        <div className="text-xs text-muted-foreground">{selectedIncident.detectedAt}</div>
                      </div>
                    </div>
                    <div className="flex space-x-3">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                        <div className="w-0.5 h-full bg-border"></div>
                      </div>
                      <div className="flex-1 pb-4">
                        <div className="font-semibold text-sm">Investigation Started</div>
                        <div className="text-xs text-muted-foreground">by {selectedIncident.assignedTo}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
