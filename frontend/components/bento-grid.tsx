import type { ReactNode } from "react"
import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface BentoGridProps {
  children: ReactNode
  className?: string
}

export function BentoGrid({ children, className }: BentoGridProps) {
  return <div className={cn("grid auto-rows-[192px] grid-cols-1 gap-4 md:grid-cols-3", className)}>{children}</div>
}

interface BentoCardProps {
  icon: LucideIcon
  title: string
  description: string
  className?: string
  gradient?: string
  glowColor?: "primary" | "secondary" | "cyan" | "purple"
}

export function BentoCard({
  icon: Icon,
  title,
  description,
  className,
  gradient,
  glowColor = "primary",
}: BentoCardProps) {
  const glowClasses = {
    primary: "glow-primary",
    secondary: "glow-secondary",
    cyan: "glow-cyan",
    purple: "glow-purple",
  }

  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-xl border glass card-3d holographic transition-all duration-300",
        className,
      )}
    >
      {gradient && (
        <div
          className={cn(
            "absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-300",
            gradient,
          )}
        />
      )}

      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div className={cn("absolute inset-0 rounded-xl", glowClasses[glowColor])} />
      </div>

      <div className="relative flex flex-col gap-3 p-6 card-3d-content">
        <div
          className={cn(
            "flex size-12 items-center justify-center rounded-lg bg-primary/10 backdrop-blur-sm",
            "group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300",
            glowClasses[glowColor],
          )}
        >
          <Icon className="size-6 text-primary group-hover:text-foreground transition-colors" />
        </div>

        <div>
          <h3 className="font-semibold text-lg mb-1 group-hover:gradient-text transition-all">{title}</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
        </div>
      </div>

      <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-primary/20 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    </div>
  )
}
