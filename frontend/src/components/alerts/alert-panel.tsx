"use client"

import { useState } from "react"
import { AlertTriangle, Bell, CheckCircle, Info, X, XCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import type { Alert, AlertSeverity, AlertType, AlertMetadata } from "@/hooks/useWebSocket"

interface AlertPanelProps {
  alerts: Alert[]
  onDismiss?: (alertId: string) => void
  onClearAll?: () => void
  maxHeight?: string
  className?: string
}

const severityConfig: Record<
  AlertSeverity,
  { icon: typeof AlertTriangle; color: string; label: string }
> = {
  critical: {
    icon: XCircle,
    color: "text-red-600 bg-red-50 border-red-200",
    label: "Crítico",
  },
  high: {
    icon: AlertTriangle,
    color: "text-orange-600 bg-orange-50 border-orange-200",
    label: "Alto",
  },
  medium: {
    icon: AlertTriangle,
    color: "text-yellow-600 bg-yellow-50 border-yellow-200",
    label: "Medio",
  },
  low: {
    icon: Info,
    color: "text-blue-600 bg-blue-50 border-blue-200",
    label: "Bajo",
  },
}

const typeConfig: Record<AlertType, { label: string; color: string }> = {
  anomaly: { label: "Anomalía", color: "bg-red-100 text-red-800" },
  prediction: { label: "Predicción", color: "bg-blue-100 text-blue-800" },
  recommendation: { label: "Recomendación", color: "bg-green-100 text-green-800" },
  system: { label: "Sistema", color: "bg-gray-100 text-gray-800" },
}

function AlertItem({
  alert,
  onDismiss,
}: {
  alert: Alert
  onDismiss?: (alertId: string) => void
}) {
  const severity = severityConfig[alert.severity]
  const type = typeConfig[alert.type]
  const Icon = severity.icon

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return "Ahora"
    if (diffMins < 60) return `Hace ${diffMins} min`
    if (diffHours < 24) return `Hace ${diffHours} h`
    if (diffDays < 7) return `Hace ${diffDays} d`
    return date.toLocaleDateString("es-CO", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div
      className={cn(
        "relative p-4 border rounded-lg transition-all hover:shadow-md",
        severity.color
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="secondary" className={cn("text-xs", type.color)}>
              {type.label}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {severity.label}
            </Badge>
            <span className="text-xs text-muted-foreground ml-auto">
              {formatTime(alert.timestamp)}
            </span>
          </div>
          <h4 className="font-semibold text-sm mb-1">{alert.title}</h4>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {alert.message}
          </p>
          {alert.metadata && (
            <div className="mt-2 flex flex-wrap gap-2">
              {alert.metadata.sede && (
                <Badge variant="outline" className="text-xs">
                  {alert.metadata.sede}
                </Badge>
              )}
              {alert.metadata.sector && (
                <Badge variant="outline" className="text-xs">
                  {alert.metadata.sector}
                </Badge>
              )}
              {alert.metadata.potential_savings_kwh && (
                <Badge variant="outline" className="text-xs text-green-600">
                  Ahorro: {alert.metadata.potential_savings_kwh} kWh
                </Badge>
              )}
            </div>
          )}
        </div>
        {onDismiss && (
          <Button
            variant="ghost"
            size="icon"
            className="flex-shrink-0 h-6 w-6"
            onClick={() => onDismiss(alert.id)}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}

export function AlertPanel({
  alerts,
  onDismiss,
  onClearAll,
  maxHeight = "400px",
  className,
}: AlertPanelProps) {
  const [filter, setFilter] = useState<AlertType | "all">("all")
  const [severityFilter, setSeverityFilter] = useState<AlertSeverity | "all">(
    "all"
  )

  const filteredAlerts = alerts.filter((alert) => {
    if (filter !== "all" && alert.type !== filter) return false
    if (severityFilter !== "all" && alert.severity !== severityFilter) return false
    return true
  })

  const unreadCount = alerts.length
  const criticalCount = alerts.filter((a) => a.severity === "critical").length
  const highCount = alerts.filter((a) => a.severity === "high").length

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <CardTitle className="text-lg">Alertas en Tiempo Real</CardTitle>
            {unreadCount > 0 && (
              <Badge variant="secondary">{unreadCount}</Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            {criticalCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                {criticalCount} Críticas
              </Badge>
            )}
            {highCount > 0 && (
              <Badge variant="default" className="text-xs bg-orange-500">
                {highCount} Altas
              </Badge>
            )}
            {onClearAll && alerts.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearAll}
                className="h-8"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Limpiar
              </Button>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 mt-3">
          <div className="flex gap-1">
            {[
              { value: "all", label: "Todas" },
              { value: "anomaly", label: "Anomalías" },
              { value: "prediction", label: "Predicciones" },
              { value: "recommendation", label: "Recomendaciones" },
            ].map(({ value, label }) => (
              <Button
                key={value}
                variant={filter === value ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter(value as AlertType | "all")}
                className="h-7 text-xs"
              >
                {label}
              </Button>
            ))}
          </div>
          <div className="flex gap-1">
            {[
              { value: "all", label: "Todas" },
              { value: "critical", label: "Críticas" },
              { value: "high", label: "Altas" },
            ].map(({ value, label }) => (
              <Button
                key={value}
                variant={severityFilter === value ? "default" : "outline"}
                size="sm"
                onClick={() =>
                  setSeverityFilter(value as AlertSeverity | "all")
                }
                className="h-7 text-xs"
              >
                {label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <ScrollArea className={cn("pr-4", maxHeight &amp;&amp; `h-[${maxHeight}]`)}>
          <div className="space-y-3">
            {filteredAlerts.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Info className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No hay alertas para mostrar</p>
                <p className="text-sm">
                  Las alertas aparecerán aquí en tiempo real
                </p>
              </div>
            ) : (
              filteredAlerts.map((alert) => (
                <AlertItem
                  key={alert.id}
                  alert={alert}
                  onDismiss={onDismiss}
                />
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}

// Compact alert badge for header/navigation
export function AlertBadge({
  count,
  criticalCount,
}: {
  count: number
  criticalCount?: number
}) {
  if (count === 0) return null

  return (
    <div className="relative inline-flex">
      <Bell className="h-5 w-5" />
      <span
        className={cn(
          "absolute -top-1 -right-1 h-4 w-4 rounded-full text-[10px] font-medium flex items-center justify-center",
          criticalCount && criticalCount > 0
            ? "bg-red-500 text-white"
            : "bg-primary text-primary-foreground"
        )}
      >
        {count > 9 ? "9+" : count}
      </span>
    </div>
  )
}

// Alert summary card for dashboard
export function AlertSummaryCard({
  alerts,
  className,
}: {
  alerts: Alert[]
  className?: string
}) {
  const bySeverity = {
    critical: alerts.filter((a) => a.severity === "critical").length,
    high: alerts.filter((a) => a.severity === "high").length,
    medium: alerts.filter((a) => a.severity === "medium").length,
    low: alerts.filter((a) => a.severity === "low").length,
  }

  const byType = {
    anomaly: alerts.filter((a) => a.type === "anomaly").length,
    prediction: alerts.filter((a) => a.type === "prediction").length,
    recommendation: alerts.filter((a) => a.type === "recommendation").length,
    system: alerts.filter((a) => a.type === "system").length,
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">
          Resumen de Alertas
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-xs text-muted-foreground mb-2">Por Severidad</p>
            <div className="grid grid-cols-4 gap-2">
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">
                  {bySeverity.critical}
                </p>
                <p className="text-xs text-muted-foreground">Críticas</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">
                  {bySeverity.high}
                </p>
                <p className="text-xs text-muted-foreground">Altas</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-yellow-600">
                  {bySeverity.medium}
                </p>
                <p className="text-xs text-muted-foreground">Medias</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {bySeverity.low}
                </p>
                <p className="text-xs text-muted-foreground">Bajas</p>
              </div>
            </div>
          </div>

          <div>
            <p className="text-xs text-muted-foreground mb-2">Por Tipo</p>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="text-xs">
                {byType.anomaly} Anomalías
              </Badge>
              <Badge variant="outline" className="text-xs">
                {byType.prediction} Predicciones
              </Badge>
              <Badge variant="outline" className="text-xs">
                {byType.recommendation} Recomendaciones
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
