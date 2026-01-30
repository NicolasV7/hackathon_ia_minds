"use client"

import { useState } from "react"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Select } from "@/components/ui/select"
import {
  useRecommendations,
  useGenerateRecommendations,
  useUpdateRecommendationStatus,
} from "@/hooks/useApi"
import { formatNumber, formatCurrency, getPriorityColor, getStatusColor } from "@/lib/utils"
import type { Sede } from "@/lib/types"
import {
  Lightbulb,
  RefreshCw,
  CheckCircle,
  XCircle,
  DollarSign,
  Leaf,
  Zap,
} from "lucide-react"

export default function RecommendationsPage() {
  const [sede, setSede] = useState<Sede>("Tunja")
  const [statusFilter, setStatusFilter] = useState<string>("")
  const [priorityFilter, setPriorityFilter] = useState<string>("")

  const { data: recommendations, isLoading, refetch } = useRecommendations(
    sede,
    priorityFilter || undefined,
    statusFilter || undefined
  )
  const generateMutation = useGenerateRecommendations()
  const updateStatusMutation = useUpdateRecommendationStatus()

  const handleGenerate = async () => {
    await generateMutation.mutateAsync({ sede, days: 7 })
    refetch()
  }

  const handleUpdateStatus = async (recommendationId: number, status: string) => {
    await updateStatusMutation.mutateAsync({ recommendationId, status })
    refetch()
  }

  const statusOptions = [
    { value: "", label: "Todos los estados" },
    { value: "pending", label: "Pendiente" },
    { value: "in_progress", label: "En progreso" },
    { value: "implemented", label: "Implementado" },
    { value: "rejected", label: "Rechazado" },
  ]

  const priorityOptions = [
    { value: "", label: "Todas las prioridades" },
    { value: "low", label: "Baja" },
    { value: "medium", label: "Media" },
    { value: "high", label: "Alta" },
    { value: "urgent", label: "Urgente" },
  ]

  // Calculate totals
  const totals = recommendations?.reduce(
    (acc, rec) => ({
      savings_kwh: acc.savings_kwh + (rec.expected_savings_kwh || 0),
      savings_cop: acc.savings_cop + (rec.expected_savings_cop || 0),
      co2_kg: acc.co2_kg + (rec.expected_co2_reduction_kg || 0),
    }),
    { savings_kwh: 0, savings_cop: 0, co2_kg: 0 }
  ) || { savings_kwh: 0, savings_cop: 0, co2_kg: 0 }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header sede={sede} onSedeChange={setSede} title="Recomendaciones" />
        
        <main className="flex-1 overflow-auto p-6">
          {/* Summary Cards */}
          <div className="grid gap-4 md:grid-cols-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Recomendaciones</p>
                    <p className="text-2xl font-bold">{recommendations?.length || 0}</p>
                  </div>
                  <Lightbulb className="h-8 w-8 text-yellow-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Ahorro Potencial</p>
                    <p className="text-2xl font-bold text-green-600">
                      {formatCurrency(totals.savings_cop)}
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Reduccion CO2</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {formatNumber(totals.co2_kg, 0)} kg
                    </p>
                  </div>
                  <Leaf className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center justify-center">
                <Button
                  onClick={handleGenerate}
                  disabled={generateMutation.isPending}
                  className="w-full"
                >
                  {generateMutation.isPending ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Generando...
                    </>
                  ) : (
                    <>
                      <Lightbulb className="mr-2 h-4 w-4" />
                      Generar Recomendaciones
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <label className="text-sm font-medium">Estado:</label>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={statusOptions}
              className="w-40"
            />
            <label className="text-sm font-medium ml-4">Prioridad:</label>
            <Select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              options={priorityOptions}
              className="w-40"
            />
          </div>

          {/* Recommendations List */}
          <div className="space-y-4">
            {isLoading ? (
              [...Array(3)].map((_, i) => <Skeleton key={i} className="h-48" />)
            ) : recommendations && recommendations.length > 0 ? (
              recommendations.map((rec) => (
                <Card key={rec.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getPriorityColor(rec.priority)}>
                            {rec.priority}
                          </Badge>
                          <Badge variant="outline">{rec.category}</Badge>
                          <Badge className={getStatusColor(rec.status)}>
                            {rec.status}
                          </Badge>
                        </div>
                        <h3 className="text-lg font-semibold">{rec.title}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Sector: {rec.sector} | Dificultad: {rec.implementation_difficulty || 'Media'}
                        </p>
                      </div>
                    </div>

                    <p className="text-gray-700 mb-4">{rec.description}</p>

                    {/* Savings Summary */}
                    <div className="grid grid-cols-3 gap-4 p-4 bg-green-50 rounded-lg mb-4">
                      <div className="text-center">
                        <Zap className="h-5 w-5 mx-auto text-green-600 mb-1" />
                        <p className="text-lg font-bold text-green-700">
                          {formatNumber(rec.expected_savings_kwh, 0)} kWh
                        </p>
                        <p className="text-xs text-green-600">Ahorro energia</p>
                      </div>
                      <div className="text-center">
                        <DollarSign className="h-5 w-5 mx-auto text-green-600 mb-1" />
                        <p className="text-lg font-bold text-green-700">
                          {formatCurrency(rec.expected_savings_cop)}
                        </p>
                        <p className="text-xs text-green-600">Ahorro economico</p>
                      </div>
                      <div className="text-center">
                        <Leaf className="h-5 w-5 mx-auto text-green-600 mb-1" />
                        <p className="text-lg font-bold text-green-700">
                          {formatNumber(rec.expected_co2_reduction_kg, 1)} kg
                        </p>
                        <p className="text-xs text-green-600">Reduccion CO2</p>
                      </div>
                    </div>

                    {/* Actions List */}
                    {rec.actions && rec.actions.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium mb-2">Acciones sugeridas:</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {rec.actions.map((action, idx) => (
                            <li key={idx}>{action}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action Buttons */}
                    {rec.status === 'pending' && (
                      <div className="flex gap-2 pt-4 border-t">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleUpdateStatus(rec.id, 'in_progress')}
                        >
                          Iniciar
                        </Button>
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleUpdateStatus(rec.id, 'implemented')}
                        >
                          <CheckCircle className="mr-1 h-4 w-4" />
                          Implementar
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleUpdateStatus(rec.id, 'rejected')}
                        >
                          <XCircle className="mr-1 h-4 w-4" />
                          Rechazar
                        </Button>
                      </div>
                    )}
                    {rec.status === 'in_progress' && (
                      <div className="flex gap-2 pt-4 border-t">
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleUpdateStatus(rec.id, 'implemented')}
                        >
                          <CheckCircle className="mr-1 h-4 w-4" />
                          Marcar como Implementado
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="py-12 text-center text-gray-500">
                  <Lightbulb className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No hay recomendaciones disponibles</p>
                  <p className="text-sm">Haz clic en "Generar Recomendaciones" para crear nuevas</p>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
