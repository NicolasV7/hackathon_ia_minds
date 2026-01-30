"use client"

import { Select } from "@/components/ui/select"
import type { Sede } from "@/lib/types"

interface HeaderProps {
  sede: Sede
  onSedeChange: (sede: Sede) => void
  title: string
}

const sedeOptions = [
  { value: "Tunja", label: "Sede Tunja" },
  { value: "Duitama", label: "Sede Duitama" },
  { value: "Sogamoso", label: "Sede Sogamoso" },
  { value: "Chiquinquira", label: "Sede Chiquinquira" },
]

export function Header({ sede, onSedeChange, title }: HeaderProps) {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium text-gray-700">Sede:</label>
        <Select
          value={sede}
          onChange={(e) => onSedeChange(e.target.value as Sede)}
          options={sedeOptions}
          className="w-48"
        />
      </div>
    </header>
  )
}
