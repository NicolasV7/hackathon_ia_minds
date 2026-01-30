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
  useAnomalies,
  useAnomalySummary,
  useDetectAnomalies,
  useUpdateAnomalyStatus,
} from "@/hooks/useApi"
import { formatNumber, formatDateTime, getSeverityColor, getStatusColor } from "@/lib/utils"
import type { Sede } from "@/lib/types"
import { AlertTriangle, Search, RefreshCw, CheckCircle, XCircle } from "lucide-react"

export default function AnomaliesPage() {
  const [sede, setSede] = useState<Sede>("Tunja")
  const [severityFilter, setSeverityFilter] = useState<string>("")

  const { data: anomalies, isLoading, refetch } = useAnomalies(
    sede,
    severityFilter || undefined
  )
  const { data: summary } = useAnomalySummary(sede)
  const detectMutation = useDetectAnomalies()
  const updateStatusMutation = useUpdateAnomalyStatus()

  const handleDetectAnomalies = async () => {
    await detectMutation.mutateAsync({ sede, days: 7 })
    refetch()
  }

  const handleUpdateStatus = async (anomalyId: number, status: string) => {
    await updateStatusMutation.mutateAsync({ anomalyId, status })
    refetch()
  }

  const severityOptions = [
    { value: "", label: "Todas las severidades" },
    { value: "low", label: "Baja" },
    { value: "medium", label: "Media" },
    { value: "high", label: "Alta" },
    { value: "critical", label: "Critica" },
  ]

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header sede={sede} onSedeChange={setSede} title="Anomalias" />
        
        <main className="flex-1 overflow-auto p-6">
          {/* Summary Cards */}
          <div className="grid gap-4 md:grid-cols-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Anomalias</p>
                    <p className="text-2xl font-bold">{summary?.total_anomalies || 0}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Alta Severidad</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {(summary?.by_severity?.high || 0) + (summary?.by_severity?.critical || 0)}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Ahorro Potencial</p>
                    <p className="text-2xl font-bold text-green-600">
                      {formatNumber(summary?.total_potential_savings_kwh || 0, 0)} kWh
                    </p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 flex items-center justify-center">
                <Button
                  onClick={handleDetectAnomalies}
                  disabled={detectMutation.isPending}
                  className="w-full"
                >
                  {detectMutation.isPending ? (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                      Analizando...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Detectar Anomalias
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <label className="text-sm font-medium">Filtrar por severidad:</label>
            <Select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              options={severityOptions}
              className="w-48"
            />
          </div>

          {/* Anomalies List */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Anomalias Detectadas</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-24" />
                  ))}
                </div>
              ) : anomalies && anomalies.length > 0 ? (
                <div className="space-y-4">
                  {anomalies.map((anomaly) => (
                    <div
                      key={anomaly.id}
                      className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={getSeverityColor(anomaly.severity)}>
                              {anomaly.severity}
                            </Badge>
                            <Badge variant="outline">{anomaly.anomaly_type}</Badge>
                            <Badge className={getStatusColor(anomaly.status)}>
                              {anomaly.status}
                            </Badge>
                          </div>
                          <h4 className="font-medium">{anomaly.description}</h4>
                          <p className="text-sm text-gray-500 mt-1">
                            Sector: {anomaly.sector} | {formatDateTime(anomaly.timestamp)}
                          </p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                        <div>
                          <span className="text-gray-500">Valor actual:</span>
                          <span className="ml-2 font-mono">{formatNumber(anomaly.actual_value)} kWh</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Esperado:</span>
                          <span className="ml-2 font-mono">{formatNumber(anomaly.expected_value)} kWh</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Desviacion:</span>
                          <span className={`ml-2 font-mono ${anomaly.deviation_pct > 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {anomaly.deviation_pct > 0 ? '+' : ''}{formatNumber(anomaly.deviation_pct)}%
                          </span>
                        </div>
                      </div>

                      <div className="mt-3 p-2 bg-blue-50 rounded text-sm">
                        <strong>Recomendacion:</strong> {anomaly.recommendation}
                      </div>

                      {anomaly.status === 'unresolved' && (
                        <div className="flex gap-2 mt-3">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUpdateStatus(anomaly.id, 'investigating')}
                          >
                            Investigar
                          </Button>
                          <Button
                            size="sm"
                            variant="default"
                            onClick={() => handleUpdateStatus(anomaly.id, 'resolved')}
                          >
                            <CheckCircle className="mr-1 h-4 w-4" />
                            Resolver
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No se encontraron anomalias</p>
                  <p className="text-sm">Haz clic en "Detectar Anomalias" para analizar el consumo</p>
                </div>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}
