"use client"

import { useState } from "react"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { KPICard } from "@/components/dashboard/kpi-card"
import { EfficiencyGauge } from "@/components/dashboard/efficiency-gauge"
import { ConsumptionChart } from "@/components/dashboard/consumption-chart"
import { SectorBreakdownChart } from "@/components/dashboard/sector-breakdown-chart"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import {
  useDashboardKPIs,
  useHourlyPatterns,
  useEfficiencyScore,
  useUnresolvedAnomalies,
  usePendingRecommendations,
} from "@/hooks/useApi"
import { formatNumber, formatCurrency, getSeverityColor, getPriorityColor } from "@/lib/utils"
import type { Sede } from "@/lib/types"
import {
  Zap,
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  DollarSign,
  Leaf,
} from "lucide-react"

export default function DashboardPage() {
  const [sede, setSede] = useState<Sede>("Tunja")
  const days = 30

  const { data: kpis, isLoading: kpisLoading } = useDashboardKPIs(sede, days)
  const { data: hourlyPatterns, isLoading: patternsLoading } = useHourlyPatterns(sede, days)
  const { data: efficiency, isLoading: efficiencyLoading } = useEfficiencyScore(sede, days)
  const { data: unresolvedAnomalies } = useUnresolvedAnomalies(sede)
  const { data: pendingRecommendations } = usePendingRecommendations(sede)

  // Mock sector data for now (would come from API)
  const sectorData = {
    comedor: { consumption_kwh: 15000, percentage: 12 },
    salones: { consumption_kwh: 35000, percentage: 28 },
    laboratorios: { consumption_kwh: 38000, percentage: 30 },
    auditorios: { consumption_kwh: 10000, percentage: 8 },
    oficinas: { consumption_kwh: 27000, percentage: 22 },
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header sede={sede} onSedeChange={setSede} title="Dashboard" />
        
        <main className="flex-1 overflow-auto p-6">
          {/* KPI Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
            {kpisLoading ? (
              <>
                {[...Array(4)].map((_, i) => (
                  <Skeleton key={i} className="h-32" />
                ))}
              </>
            ) : kpis ? (
              <>
                <KPICard
                  title="Consumo Total"
                  value={`${formatNumber(kpis.consumption.total_kwh, 0)} kWh`}
                  subtitle={`Promedio: ${formatNumber(kpis.consumption.avg_kwh)} kWh/h`}
                  icon={Zap}
                />
                <KPICard
                  title="Anomalias Detectadas"
                  value={kpis.anomalies.total}
                  subtitle={`${kpis.anomalies.by_severity?.high || 0} alta severidad`}
                  icon={AlertTriangle}
                />
                <KPICard
                  title="Ahorro Potencial"
                  value={formatCurrency(kpis.recommendations.potential_savings_cop)}
                  subtitle={`${formatNumber(kpis.recommendations.potential_savings_kwh, 0)} kWh`}
                  icon={DollarSign}
                />
                <KPICard
                  title="Recomendaciones Pendientes"
                  value={kpis.recommendations.total_pending}
                  subtitle="Acciones por implementar"
                  icon={Lightbulb}
                />
              </>
            ) : (
              <div className="col-span-4 text-center text-gray-500 py-8">
                No se pudieron cargar los KPIs. Verifica que el backend este corriendo.
              </div>
            )}
          </div>

          {/* Charts Row */}
          <div className="grid gap-6 lg:grid-cols-3 mb-6">
            {/* Efficiency Gauge */}
            <div className="lg:col-span-1">
              {efficiencyLoading ? (
                <Skeleton className="h-[400px]" />
              ) : efficiency ? (
                <EfficiencyGauge
                  score={efficiency.overall_score}
                  components={efficiency.components}
                />
              ) : (
                <Card className="h-[400px] flex items-center justify-center">
                  <p className="text-gray-500">Sin datos de eficiencia</p>
                </Card>
              )}
            </div>

            {/* Consumption Chart */}
            <div className="lg:col-span-2">
              {patternsLoading ? (
                <Skeleton className="h-[400px]" />
              ) : hourlyPatterns ? (
                <ConsumptionChart data={hourlyPatterns.hourly_averages} />
              ) : (
                <Card className="h-[400px] flex items-center justify-center">
                  <p className="text-gray-500">Sin datos de consumo</p>
                </Card>
              )}
            </div>
          </div>

          {/* Bottom Row */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Sector Breakdown */}
            <SectorBreakdownChart sectors={sectorData} />

            {/* Recent Anomalies & Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Actividad Reciente</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Anomalies */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      Anomalias Sin Resolver ({unresolvedAnomalies?.length || 0})
                    </h4>
                    <div className="space-y-2">
                      {unresolvedAnomalies?.slice(0, 3).map((anomaly) => (
                        <div
                          key={anomaly.id}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded"
                        >
                          <div className="flex-1">
                            <p className="text-sm font-medium truncate">
                              {anomaly.description}
                            </p>
                            <p className="text-xs text-gray-500">
                              {anomaly.sector} - {anomaly.anomaly_type}
                            </p>
                          </div>
                          <Badge
                            className={getSeverityColor(anomaly.severity)}
                            variant="outline"
                          >
                            {anomaly.severity}
                          </Badge>
                        </div>
                      )) || (
                        <p className="text-sm text-gray-500">No hay anomalias pendientes</p>
                      )}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">
                      Recomendaciones Pendientes ({pendingRecommendations?.length || 0})
                    </h4>
                    <div className="space-y-2">
                      {pendingRecommendations?.slice(0, 3).map((rec) => (
                        <div
                          key={rec.id}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded"
                        >
                          <div className="flex-1">
                            <p className="text-sm font-medium truncate">
                              {rec.title}
                            </p>
                            <p className="text-xs text-gray-500">
                              Ahorro: {formatCurrency(rec.expected_savings_cop)}
                            </p>
                          </div>
                          <Badge
                            className={getPriorityColor(rec.priority)}
                            variant="outline"
                          >
                            {rec.priority}
                          </Badge>
                        </div>
                      )) || (
                        <p className="text-sm text-gray-500">No hay recomendaciones pendientes</p>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
