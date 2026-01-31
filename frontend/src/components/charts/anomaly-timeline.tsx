'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Anomaly {
  id: string | number;
  timestamp: string;
  sede: string;
  sector: string;
  anomaly_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  deviation_pct: number;
  potential_savings_kwh?: number;
}

interface AnomalyTimelineProps {
  anomalies: Anomaly[];
  title?: string;
  maxItems?: number;
  showSector?: boolean;
  onAnomalyClick?: (anomaly: Anomaly) => void;
}

const severityConfig = {
  low: {
    color: 'bg-blue-500',
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    label: 'Baja',
  },
  medium: {
    color: 'bg-yellow-500',
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    label: 'Media',
  },
  high: {
    color: 'bg-orange-500',
    badge: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    label: 'Alta',
  },
  critical: {
    color: 'bg-red-500',
    badge: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    label: 'Crítica',
  },
};

const anomalyTypeLabels: Record<string, string> = {
  off_hours_usage: 'Consumo nocturno',
  weekend_anomaly: 'Fin de semana',
  consumption_spike: 'Pico de consumo',
  low_occupancy_high_consumption: 'Bajo uso, alto consumo',
  holiday_consumption: 'Día festivo',
  academic_vacation_high: 'Vacaciones',
  statistical_outlier: 'Outlier estadístico',
  consumption_drop: 'Caída de consumo',
};

const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) {
    return 'Hace menos de 1 hora';
  } else if (diffHours < 24) {
    return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
  } else if (diffDays < 7) {
    return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;
  } else {
    return date.toLocaleDateString('es-CO', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
};

export function AnomalyTimeline({
  anomalies,
  title = 'Timeline de Anomalías',
  maxItems = 10,
  showSector = true,
  onAnomalyClick,
}: AnomalyTimelineProps) {
  const sortedAnomalies = useMemo(() => {
    return [...anomalies]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, maxItems);
  }, [anomalies, maxItems]);

  if (sortedAnomalies.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            No hay anomalías detectadas en el periodo seleccionado
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center justify-between">
          {title}
          <Badge variant="secondary" className="ml-2">
            {anomalies.length} total
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />

          {/* Anomaly items */}
          <div className="space-y-4">
            {sortedAnomalies.map((anomaly, index) => {
              const config = severityConfig[anomaly.severity];
              const typeLabel = anomalyTypeLabels[anomaly.anomaly_type] || anomaly.anomaly_type;

              return (
                <div
                  key={anomaly.id || index}
                  className={`
                    relative pl-10 cursor-pointer
                    hover:bg-gray-50 dark:hover:bg-gray-800/50
                    rounded-lg p-2 transition-colors
                  `}
                  onClick={() => onAnomalyClick?.(anomaly)}
                >
                  {/* Timeline dot */}
                  <div
                    className={`
                      absolute left-2 w-5 h-5 rounded-full border-2 border-white dark:border-gray-900
                      ${config.color}
                    `}
                  />

                  {/* Content */}
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge className={config.badge}>{config.label}</Badge>
                      <Badge variant="outline" className="text-xs">
                        {typeLabel}
                      </Badge>
                      {showSector && anomaly.sector !== 'total' && (
                        <Badge variant="secondary" className="text-xs">
                          {anomaly.sector}
                        </Badge>
                      )}
                    </div>

                    <p className="text-sm font-medium">
                      {anomaly.description.length > 100
                        ? `${anomaly.description.substring(0, 100)}...`
                        : anomaly.description}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{formatTimestamp(anomaly.timestamp)}</span>
                      <span>Desviación: {Math.abs(anomaly.deviation_pct).toFixed(0)}%</span>
                      {anomaly.potential_savings_kwh && anomaly.potential_savings_kwh > 0 && (
                        <span className="text-green-600 dark:text-green-400">
                          Ahorro potencial: {anomaly.potential_savings_kwh.toFixed(1)} kWh
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {anomalies.length > maxItems && (
          <p className="text-center text-sm text-muted-foreground mt-4">
            Mostrando {maxItems} de {anomalies.length} anomalías
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// Summary component for dashboard
export function AnomalySummary({
  anomalies,
  title = 'Resumen de Anomalías',
}: {
  anomalies: Anomaly[];
  title?: string;
}) {
  const summary = useMemo(() => {
    const bySeverity: Record<string, number> = { low: 0, medium: 0, high: 0, critical: 0 };
    const byType: Record<string, number> = {};
    let totalSavings = 0;

    anomalies.forEach((a) => {
      bySeverity[a.severity] = (bySeverity[a.severity] || 0) + 1;
      byType[a.anomaly_type] = (byType[a.anomaly_type] || 0) + 1;
      totalSavings += a.potential_savings_kwh || 0;
    });

    return { bySeverity, byType, totalSavings };
  }, [anomalies]);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(summary.bySeverity).map(([severity, count]) => {
            const config = severityConfig[severity as keyof typeof severityConfig];
            return (
              <div key={severity} className="text-center">
                <div
                  className={`
                    w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center
                    ${config.color} text-white font-bold text-lg
                  `}
                >
                  {count}
                </div>
                <p className="text-sm text-muted-foreground">{config.label}</p>
              </div>
            );
          })}
        </div>

        {summary.totalSavings > 0 && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg text-center">
            <p className="text-sm text-muted-foreground">Ahorro potencial total</p>
            <p className="text-xl font-bold text-green-600 dark:text-green-400">
              {summary.totalSavings.toFixed(1)} kWh
            </p>
            <p className="text-sm text-muted-foreground">
              ~${(summary.totalSavings * 600).toLocaleString('es-CO')} COP/mes
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default AnomalyTimeline;
