"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts"

interface SectorBreakdownChartProps {
  sectors: Record<string, { consumption_kwh: number; percentage: number }>
}

const COLORS = ["#16a34a", "#2563eb", "#dc2626", "#eab308", "#8b5cf6"]
const SECTOR_LABELS: Record<string, string> = {
  comedor: "Comedor",
  salones: "Salones",
  laboratorios: "Laboratorios",
  auditorios: "Auditorios",
  oficinas: "Oficinas",
}

export function SectorBreakdownChart({ sectors }: SectorBreakdownChartProps) {
  const data = Object.entries(sectors).map(([key, value]) => ({
    name: SECTOR_LABELS[key] || key,
    value: value.consumption_kwh,
    percentage: value.percentage,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Consumo por Sector</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, name: string, props: any) => [
                  `${value.toFixed(2)} kWh (${props.payload.percentage.toFixed(1)}%)`,
                  name,
                ]}
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                }}
              />
              <Legend
                layout="vertical"
                align="right"
                verticalAlign="middle"
                formatter={(value, entry: any) =>
                  `${value} (${entry.payload.percentage.toFixed(1)}%)`
                }
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
