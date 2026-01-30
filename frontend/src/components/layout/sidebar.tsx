"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Settings,
  Zap,
} from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Predicciones", href: "/predictions", icon: TrendingUp },
  { name: "Anomalias", href: "/anomalies", icon: AlertTriangle },
  { name: "Recomendaciones", href: "/recommendations", icon: Lightbulb },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col bg-white border-r">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 px-6 border-b">
        <Zap className="h-8 w-8 text-primary" />
        <div>
          <h1 className="font-bold text-lg text-gray-900">UPTC EcoEnergy</h1>
          <p className="text-xs text-gray-500">Sistema de Eficiencia</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-white"
                  : "text-gray-700 hover:bg-gray-100"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <div className="text-xs text-gray-500">
          <p>UPTC - HackDay 2025</p>
          <p>v1.0.0</p>
        </div>
      </div>
    </div>
  )
}
