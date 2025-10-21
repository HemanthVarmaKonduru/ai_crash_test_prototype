"use client"

import type React from "react"

import { Shield, Target, Zap, FileText, Settings, Home, BarChart3 } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

const attackModules = [
  {
    title: "Prompt Injection",
    icon: Target,
    url: "/dashboard/prompt-injection",
    description: "Test prompt injection vulnerabilities",
  },
  {
    title: "Jailbreak Detection",
    icon: Shield,
    url: "/dashboard/jailbreak",
    description: "Detect jailbreak attempts",
  },
  {
    title: "Data Extraction",
    icon: FileText,
    url: "/dashboard/data-extraction",
    description: "Test data leakage scenarios",
  },
  {
    title: "Adversarial Attacks",
    icon: Zap,
    url: "/dashboard/adversarial",
    description: "Run adversarial attack simulations",
  },
]

const navigationItems = [
  {
    title: "Overview",
    icon: Home,
    url: "/dashboard",
  },
  {
    title: "Reports",
    icon: BarChart3,
    url: "/dashboard/reports",
  },
  {
    title: "Settings",
    icon: Settings,
    url: "/dashboard/settings",
  },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  return (
    <SidebarProvider>
      <Sidebar variant="inset">
        <SidebarHeader className="border-b border-sidebar-border">
          <div className="flex items-center gap-2 px-2 py-1">
            <div className="flex size-8 items-center justify-center rounded-lg bg-sidebar-primary">
              <Shield className="size-4 text-sidebar-primary-foreground" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold">LLMShield</span>
              <span className="text-xs text-sidebar-foreground/70">Attack Lab</span>
            </div>
          </div>
        </SidebarHeader>

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {navigationItems.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild isActive={pathname === item.url}>
                      <Link href={item.url}>
                        <item.icon />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          <SidebarGroup>
            <SidebarGroupLabel>Attack Modules</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {attackModules.map((module) => (
                  <SidebarMenuItem key={module.title}>
                    <SidebarMenuButton asChild isActive={pathname === module.url} tooltip={module.description}>
                      <Link href={module.url}>
                        <module.icon />
                        <span>{module.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter className="border-t border-sidebar-border">
          <SidebarMenu>
            <SidebarMenuItem>
              <div className="flex items-center gap-2 px-2 py-1.5 text-xs text-sidebar-foreground/70">
                <div className="size-2 rounded-full bg-green-500" />
                <span>All systems operational</span>
              </div>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
              </BreadcrumbItem>
              {pathname !== "/dashboard" && (
                <>
                  <BreadcrumbSeparator />
                  <BreadcrumbItem>
                    <BreadcrumbPage>
                      {attackModules.find((m) => m.url === pathname)?.title ||
                        navigationItems.find((n) => n.url === pathname)?.title ||
                        "Page"}
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </>
              )}
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <main className="flex flex-1 flex-col gap-4 p-4 md:p-6">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  )
}
