"use client"

import { useState } from "react"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { useLatestPredictions, useCreateBatchPredictions } from "@/hooks/useApi"
import { formatNumber, formatDateTime } from "@/lib/utils"
import type { Sede } from "@/lib/types"
import { TrendingUp, RefreshCw, Calendar } from "lucide-react"

export default function PredictionsPage() {
  const [sede, setSede] = useState<Sede>("Tunja")
  const [horizonHours, setHorizonHours] = useState(24)

  const { data: predictions, isLoading, refetch } = useLatestPredictions(sede, 48)
  const createBatchMutation = useCreateBatchPredictions()

  const handleGeneratePredictions = async () => {
    const startTimestamp = new Date().toISOString()
    await createBatchMutation.mutateAsync({
      sede,
      startTimestamp,
      horizonHours,
    })
    refetch()
  }

  const chartData = predictions?.map((p) => ({
    timestamp: new Date(p.prediction_timestamp).toLocaleTimeString("es-CO", {
      hour: "2-digit",
      minute: "2-digit",
    }),
    predicted: p.predicted_kwh,
    confidence: p.confidence_score * 100,
  })) || []

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header sede={sede} onSedeChange={setSede} title="Predicciones" />
        
        <main className="flex-1 overflow-auto p-6">
          {/* Actions */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold">Pronostico de Consumo</h2>
              <p className="text-sm text-gray-500">
                Predicciones de consumo energetico usando ML
              </p>
            </div>
            <div className="flex items-center gap-4">
              <select
                value={horizonHours}
                onChange={(e) => setHorizonHours(Number(e.target.value))}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value={24}>24 horas</option>
                <option value={48}>48 horas</option>
                <option value={72}>72 horas</option>
                <option value={168}>7 dias</option>
              </select>
              <Button
                onClick={handleGeneratePredictions}
                disabled={createBatchMutation.isPending}
              >
                {createBatchMutation.isPending ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Generando...
                  </>
                ) : (
                  <>
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Generar Predicciones
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Chart */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Pronostico de Consumo - Sede {sede}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <Skeleton className="h-[400px]" />
              ) : chartData.length > 0 ? (
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                      <XAxis
                        dataKey="timestamp"
                        tick={{ fontSize: 11 }}
                        tickLine={false}
                        axisLine={false}
                      />
                      <YAxis
                        tick={{ fontSize: 12 }}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `${value} kWh`}
                      />
                      <Tooltip
                        formatter={(value: number, name: string) => [
                          name === "predicted"
                            ? `${value.toFixed(2)} kWh`
                            : `${value.toFixed(1)}%`,
                          name === "predicted" ? "Consumo Predicho" : "Confianza",
                        ]}
                        contentStyle={{
                          backgroundColor: "white",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                        }}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="predicted"
                        name="Consumo Predicho"
                        stroke="#16a34a"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-[400px] flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p>No hay predicciones disponibles</p>
                    <p className="text-sm">Haz clic en "Generar Predicciones" para crear un pronostico</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Predictions Table */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Detalle de Predicciones</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-2">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-12" />
                  ))}
                </div>
              ) : predictions && predictions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-medium">Fecha/Hora</th>
                        <th className="text-right py-3 px-4 font-medium">Consumo Predicho</th>
                        <th className="text-right py-3 px-4 font-medium">Confianza</th>
                        <th className="text-right py-3 px-4 font-medium">Temperatura</th>
                        <th className="text-right py-3 px-4 font-medium">Ocupacion</th>
                      </tr>
                    </thead>
                    <tbody>
                      {predictions.slice(0, 24).map((prediction) => (
                        <tr key={prediction.id} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4">
                            {formatDateTime(prediction.prediction_timestamp)}
                          </td>
                          <td className="py-3 px-4 text-right font-mono">
                            {formatNumber(prediction.predicted_kwh)} kWh
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Badge variant={prediction.confidence_score > 0.8 ? "success" : "warning"}>
                              {(prediction.confidence_score * 100).toFixed(0)}%
                            </Badge>
                          </td>
                          <td className="py-3 px-4 text-right">
                            {prediction.temperatura_exterior_c?.toFixed(1) || "-"}C
                          </td>
                          <td className="py-3 px-4 text-right">
                            {prediction.ocupacion_pct?.toFixed(0) || "-"}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">
                  No hay predicciones para mostrar
                </p>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}
