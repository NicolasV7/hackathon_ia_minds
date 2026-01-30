"use client"

import { useState } from "react"
import { Sidebar } from "./sidebar"
import { Header } from "./header"
import type { Sede } from "@/lib/types"

interface DashboardLayoutProps {
  children: React.ReactNode
  title: string
}

export function DashboardLayout({ children, title }: DashboardLayoutProps) {
  const [sede, setSede] = useState<Sede>("Tunja")

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header sede={sede} onSedeChange={setSede} title={title} />
        <main className="flex-1 overflow-auto p-6">
          {typeof children === "function"
            ? (children as (sede: Sede) => React.ReactNode)(sede)
            : children}
        </main>
      </div>
    </div>
  )
}

// Export a hook-friendly version
export function useSede() {
  const [sede, setSede] = useState<Sede>("Tunja")
  return { sede, setSede }
}
