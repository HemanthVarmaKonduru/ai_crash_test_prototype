import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Target,
  Shield,
  FileText,
  Zap,
  ArrowRight,
  Activity,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
} from "lucide-react"
import Link from "next/link"

const modules = [
  {
    title: "Prompt Injection",
    description: "Test your LLM's resilience against prompt injection attacks with real-world scenarios.",
    icon: Target,
    status: "ready",
    tests: 24,
    href: "/dashboard/prompt-injection",
    gradient: "from-indigo-500/10 to-purple-500/10",
    iconColor: "text-indigo-500",
  },
  {
    title: "Jailbreak Detection",
    description: "Identify and prevent jailbreak attempts that bypass safety guardrails.",
    icon: Shield,
    status: "ready",
    tests: 18,
    href: "/dashboard/jailbreak",
    gradient: "from-pink-500/10 to-rose-500/10",
    iconColor: "text-pink-500",
  },
  {
    title: "Data Extraction",
    description: "Simulate attacks that attempt to extract sensitive training data or system prompts.",
    icon: FileText,
    status: "ready",
    tests: 15,
    href: "/dashboard/data-extraction",
    gradient: "from-cyan-500/10 to-blue-500/10",
    iconColor: "text-cyan-500",
  },
  {
    title: "Adversarial Attacks",
    description: "Run sophisticated adversarial attacks to test model robustness.",
    icon: Zap,
    status: "ready",
    tests: 21,
    href: "/dashboard/adversarial",
    gradient: "from-purple-500/10 to-indigo-500/10",
    iconColor: "text-purple-500",
  },
]

const stats = [
  {
    label: "Total Tests Run",
    value: "1,247",
    change: "+12%",
    icon: Activity,
    trend: "up",
    gradient: "from-indigo-500/20 to-purple-500/20",
  },
  {
    label: "Vulnerabilities Found",
    value: "23",
    change: "-8%",
    icon: AlertTriangle,
    trend: "down",
    gradient: "from-orange-500/20 to-red-500/20",
  },
  {
    label: "Success Rate",
    value: "94.2%",
    change: "+2.1%",
    icon: CheckCircle2,
    trend: "up",
    gradient: "from-green-500/20 to-emerald-500/20",
  },
]

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          <span className="gradient-text">Attack Lab Dashboard</span>
        </h1>
        <p className="text-muted-foreground mt-2">
          Select an attack module to begin testing your LLM's security posture.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.label} className="glass card-3d holographic relative overflow-hidden">
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-50`} />

            <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
              <div className="flex size-10 items-center justify-center rounded-lg bg-background/50 backdrop-blur-sm">
                <stat.icon className="size-5 text-muted-foreground" />
              </div>
            </CardHeader>
            <CardContent className="relative">
              <div className="text-3xl font-bold gradient-text">{stat.value}</div>
              <div className="flex items-center gap-1 mt-1">
                {stat.trend === "up" ? (
                  <TrendingUp className="size-4 text-green-500" />
                ) : (
                  <TrendingDown className="size-4 text-red-500" />
                )}
                <p className={`text-xs font-medium ${stat.trend === "up" ? "text-green-500" : "text-red-500"}`}>
                  {stat.change} from last month
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Attack Modules</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {modules.map((module) => (
            <Card
              key={module.title}
              className="group glass card-3d holographic relative overflow-hidden border-2 hover:border-primary/50 transition-all duration-300"
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${module.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
              />

              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-primary/20 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              <CardHeader className="relative">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`flex size-12 items-center justify-center rounded-lg bg-background/50 backdrop-blur-sm glow-primary group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}
                    >
                      <module.icon className={`size-6 ${module.iconColor}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg group-hover:gradient-text transition-all">{module.title}</CardTitle>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-xs glass">
                          {module.tests} tests
                        </Badge>
                        <Badge variant="outline" className="text-xs glass">
                          {module.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
                <CardDescription className="mt-3 leading-relaxed">{module.description}</CardDescription>
              </CardHeader>
              <CardContent className="relative">
                <Button asChild className="w-full glow-primary group-hover:scale-105 transition-transform duration-300">
                  <Link href={module.href}>
                    Launch Module
                    <ArrowRight className="ml-2 size-4 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

          <Card className="glass-strong neon-border relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5" />
            <CardHeader className="relative">
              <CardTitle className="gradient-text">Getting Started</CardTitle>
              <CardDescription>
                New to Evalence? Here's how to get the most out of your attack simulations.
              </CardDescription>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="flex items-start gap-4 group">
                <div className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary text-primary-foreground text-sm font-bold shrink-0 group-hover:scale-110 transition-transform">
                  1
                </div>
                <div className="space-y-1">
                  <p className="font-medium">Configure your LLM endpoint</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Connect your model API in Settings to begin testing.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 group">
                <div className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary text-primary-foreground text-sm font-bold shrink-0 group-hover:scale-110 transition-transform">
                  2
                </div>
                <div className="space-y-1">
                  <p className="font-medium">Select an attack module</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Choose from our curated library of adversarial tests.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4 group">
                <div className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary text-primary-foreground text-sm font-bold shrink-0 group-hover:scale-110 transition-transform">
                  3
                </div>
                <div className="space-y-1">
                  <p className="font-medium">Review results and reports</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Analyze vulnerabilities and export detailed security reports.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
    </div>
  )
}
