import { Button } from "@/components/ui/button"
import {
  Shield,
  Target,
  Zap,
  FileText,
  ArrowRight,
  CheckCircle2,
  Lock,
  BarChart3,
  Sparkles,
  AlertTriangle,
  TrendingUp,
  Users,
  Code2,
  Brain,
  Layers,
} from "lucide-react"
import Link from "next/link"
import { BentoCard, BentoGrid } from "@/components/bento-grid"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col particles">
      <nav className="glass-strong border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Shield className="size-6 text-primary glow-primary" />
              <div className="absolute inset-0 animate-ping">
                <Shield className="size-6 text-primary opacity-20" />
              </div>
            </div>
            <span className="text-xl font-bold gradient-text">Evalence</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost" className="hover:bg-primary/10">
                Sign In
              </Button>
            </Link>
            <Link href="/login">
              <Button className="glow-primary group">
                Get Started
                <Sparkles className="ml-2 size-4 group-hover:rotate-12 transition-transform" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      <section className="gradient-hero grid-background relative py-24 md:py-32">
        <div className="container mx-auto px-4 relative z-10">
          <div className="mx-auto max-w-4xl text-center space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full glass px-4 py-2 text-sm float">
              <Sparkles className="size-4 text-primary" />
              <span className="text-muted-foreground">Enterprise-Grade LLM Security Testing</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-tight">
              <span className="gradient-text">Adversarial Testing</span>
              <br />
              <span className="text-foreground">for Modern AI Systems</span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Simulate real-world attacks, identify vulnerabilities, and fortify your LLMs against prompt injection,
              jailbreaks, and data extraction attempts.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/login">
                <Button size="lg" className="glow-primary card-3d group text-lg px-8">
                  Launch Attack Lab
                  <ArrowRight className="ml-2 size-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="glass text-lg px-8 bg-transparent">
                View Documentation
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-background relative overflow-hidden">
        <div className="absolute inset-0 grid-background opacity-30" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full glass px-4 py-2 text-sm">
                <AlertTriangle className="size-4 text-destructive" />
                <span className="text-muted-foreground">The Challenge</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold leading-tight">
                <span className="text-foreground">AI Systems Are Under</span>
                <br />
                <span className="gradient-text">Constant Attack</span>
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                As Large Language Models become integral to business operations, they face sophisticated threats from
                malicious actors. Prompt injections can manipulate AI behavior, jailbreaks bypass safety measures, and
                data extraction attacks expose sensitive information.
              </p>
              <div className="space-y-4">
              <div className="flex items-start gap-3 glass-strong rounded-lg p-4 card-3d">
                <div className="rounded-full bg-destructive/20 p-2 mt-1">
                  <Target className="size-5 text-destructive" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Prompt Injection Attacks</h3>
                  <p className="text-sm text-muted-foreground">
                    Attackers manipulate model outputs by injecting malicious instructions into user inputs
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 glass-strong rounded-lg p-4 card-3d">
                <div className="rounded-full bg-destructive/20 p-2 mt-1">
                  <Shield className="size-5 text-destructive" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Safety Bypass Attempts</h3>
                  <p className="text-sm text-muted-foreground">
                    Sophisticated jailbreak techniques circumvent built-in safety guardrails and ethical constraints
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 glass-strong rounded-lg p-4 card-3d">
                <div className="rounded-full bg-destructive/20 p-2 mt-1">
                  <FileText className="size-5 text-destructive" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Data Leakage Risks</h3>
                  <p className="text-sm text-muted-foreground">
                    Models can inadvertently expose training data, system prompts, and confidential information
                  </p>
                </div>
              </div>
              </div>
            </div>

            <div className="relative">
              <div className="glass-strong rounded-2xl p-8 space-y-6 card-3d neon-border">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground">Threat Landscape 2025</span>
                  <TrendingUp className="size-4 text-destructive" />
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-foreground">Prompt Injection Attempts</span>
                      <span className="text-sm font-bold text-destructive">+340%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full w-[85%] bg-gradient-to-r from-destructive to-destructive/50 rounded-full" />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-foreground">Jailbreak Techniques</span>
                      <span className="text-sm font-bold text-destructive">+275%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full w-[70%] bg-gradient-to-r from-orange-500 to-orange-500/50 rounded-full" />
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-foreground">Data Extraction Attacks</span>
                      <span className="text-sm font-bold text-destructive">+190%</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div className="h-full w-[55%] bg-gradient-to-r from-amber-500 to-amber-500/50 rounded-full" />
                    </div>
                  </div>
                </div>
                <div className="pt-4 border-t border-border/50">
                  <p className="text-xs text-muted-foreground">
                    Source: Global AI Security Report 2025 • Based on 10M+ attack simulations
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 gradient-hero relative">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-16">
            <div className="inline-flex items-center gap-2 rounded-full glass px-4 py-2 text-sm">
              <Sparkles className="size-4 text-primary" />
              <span className="text-muted-foreground">Our Solution</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold">
              <span className="gradient-text">Proactive Defense</span>
              <br />
              <span className="text-foreground">Through Adversarial Testing</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Evalence empowers security teams to think like attackers. Our platform simulates real-world adversarial
              scenarios, helping you discover vulnerabilities before malicious actors do.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="glass-strong rounded-2xl p-8 card-3d neon-border space-y-4">
              <div className="rounded-full bg-primary/20 p-3 w-fit">
                <Brain className="size-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-foreground">Intelligent Attack Simulation</h3>
              <p className="text-muted-foreground leading-relaxed">
                Our AI-powered engine generates sophisticated attack vectors based on the latest threat intelligence,
                continuously adapting to emerging vulnerabilities.
              </p>
            </div>

            <div className="glass-strong rounded-2xl p-8 card-3d neon-border space-y-4">
              <div className="rounded-full bg-secondary/20 p-3 w-fit">
                <Layers className="size-6 text-secondary" />
              </div>
              <h3 className="text-xl font-bold text-foreground">Multi-Layer Defense Testing</h3>
              <p className="text-muted-foreground leading-relaxed">
                Test every layer of your AI stack—from input validation to output filtering—ensuring comprehensive
                protection across your entire system architecture.
              </p>
            </div>

            <div className="glass-strong rounded-2xl p-8 card-3d neon-border space-y-4">
              <div className="rounded-full bg-cyan-500/20 p-3 w-fit">
                <Code2 className="size-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold text-foreground">Actionable Remediation</h3>
              <p className="text-muted-foreground leading-relaxed">
                Get detailed vulnerability reports with specific code-level recommendations and best practices to
                strengthen your defenses immediately.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-background relative">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold">
              <span className="gradient-text">Comprehensive Security</span> Testing Suite
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Advanced attack simulations designed for enterprise AI security teams
            </p>
          </div>

          <BentoGrid>
            <BentoCard
              icon={Target}
              title="Prompt Injection Defense"
              description="Test resilience against sophisticated prompt manipulation and injection attacks with 24+ real-world scenarios."
              gradient="from-indigo-500/20 to-purple-500/20"
              glowColor="primary"
            />
            <BentoCard
              icon={Shield}
              title="Jailbreak Detection"
              description="Identify and prevent attempts to bypass safety guardrails with advanced pattern recognition."
              gradient="from-pink-500/20 to-rose-500/20"
              glowColor="secondary"
            />
            <BentoCard
              icon={FileText}
              title="Data Extraction Prevention"
              description="Simulate attacks targeting sensitive training data and system prompts to strengthen defenses."
              gradient="from-cyan-500/20 to-blue-500/20"
              glowColor="cyan"
            />
            <BentoCard
              icon={Zap}
              title="Adversarial Robustness"
              description="Run sophisticated adversarial attacks to test model stability and response consistency."
              gradient="from-purple-500/20 to-indigo-500/20"
              glowColor="purple"
            />
            <BentoCard
              icon={CheckCircle2}
              title="Continuous Monitoring"
              description="Real-time threat detection with automated alerts and comprehensive security dashboards."
              gradient="from-green-500/20 to-emerald-500/20"
              glowColor="primary"
            />
            <BentoCard
              icon={Lock}
              title="Enterprise Encryption"
              description="Military-grade encryption for all test data with complete audit trails and compliance reporting."
              gradient="from-orange-500/20 to-amber-500/20"
              glowColor="secondary"
            />
            <BentoCard
              icon={BarChart3}
              title="Performance Analytics"
              description="Deep insights into model behavior with detailed metrics, trends, and optimization recommendations."
              gradient="from-violet-500/20 to-purple-500/20"
              glowColor="purple"
            />
          </BentoGrid>
        </div>
      </section>

      <section className="py-24 gradient-hero relative">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-4xl font-bold">
              <span className="text-foreground">Trusted by</span>{" "}
              <span className="gradient-text">Enterprise Teams</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Trusted by leading organizations securing their AI systems
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="glass-strong rounded-2xl p-8 card-3d neon-border">
              <div className="text-5xl font-bold gradient-text mb-2">99.9%</div>
              <div className="text-lg text-foreground font-medium">Attack Detection Rate</div>
              <div className="text-sm text-muted-foreground mt-2">
                Industry-leading accuracy across all threat categories
              </div>
            </div>
            <div className="glass-strong rounded-2xl p-8 card-3d neon-border">
              <div className="text-5xl font-bold gradient-text mb-2">10M+</div>
              <div className="text-lg text-foreground font-medium">Tests Executed</div>
              <div className="text-sm text-muted-foreground mt-2">Protecting Fortune 500 AI deployments daily</div>
            </div>
            <div className="glass-strong rounded-2xl p-8 card-3d neon-border">
              <div className="text-5xl font-bold gradient-text mb-2">&lt;50ms</div>
              <div className="text-lg text-foreground font-medium">Average Response Time</div>
              <div className="text-sm text-muted-foreground mt-2">Real-time protection without performance impact</div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-background relative overflow-hidden">
        <div className="absolute inset-0 grid-background opacity-20" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="glass-strong rounded-3xl p-12 md:p-16 card-3d neon-border text-center space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full glass px-4 py-2 text-sm">
              <Users className="size-4 text-primary" />
              <span className="text-muted-foreground">Join 500+ Security Teams</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold leading-tight">
              <span className="text-foreground">Ready to Secure Your</span>
              <br />
              <span className="gradient-text">AI Infrastructure?</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Start testing your LLMs against real-world adversarial attacks today. No credit card required for your
              first 100 tests.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/login">
                <Button size="lg" className="glow-primary card-3d group text-lg px-8">
                  Start Free Trial
                  <ArrowRight className="ml-2 size-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="glass text-lg px-8 bg-transparent">
                Schedule Demo
              </Button>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-8 pt-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="size-5 text-primary" />
                <span className="text-sm text-muted-foreground">No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="size-5 text-primary" />
                <span className="text-sm text-muted-foreground">Setup in 5 minutes</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="size-5 text-primary" />
                <span className="text-sm text-muted-foreground">Cancel anytime</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="glass-strong border-t">
        <div className="container mx-auto px-4 py-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Shield className="size-5 text-primary" />
              <span className="font-semibold">Evalence</span>
            </div>
            <span className="text-sm text-muted-foreground">© 2025 Evalence. Enterprise AI Security Platform.</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
