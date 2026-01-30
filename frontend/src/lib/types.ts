// API Response Types

export type Sede = 'Tunja' | 'Duitama' | 'Sogamoso' | 'Chiquinquira'

export interface Prediction {
  id: number
  sede: Sede
  prediction_timestamp: string
  predicted_kwh: number
  confidence_score: number
  temperatura_exterior_c?: number
  ocupacion_pct?: number
  es_festivo: boolean
  es_semana_parciales: boolean
  es_semana_finales: boolean
  created_at: string
}

export interface PredictionRequest {
  timestamp: string
  sede: Sede
  temperatura_exterior_c?: number
  ocupacion_pct?: number
  es_festivo?: boolean
  es_semana_parciales?: boolean
  es_semana_finales?: boolean
}

export interface Anomaly {
  id: number
  timestamp: string
  sede: Sede
  sector: string
  anomaly_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  actual_value: number
  expected_value: number
  deviation_pct: number
  description: string
  recommendation: string
  potential_savings_kwh: number
  status: 'unresolved' | 'investigating' | 'resolved'
  detected_at: string
  created_at: string
}

export interface AnomalySummary {
  sede: Sede
  total_anomalies: number
  by_severity: Record<string, number>
  by_type: Record<string, number>
  total_potential_savings_kwh: number
}

export interface Recommendation {
  id: number
  sede: Sede
  sector: string
  anomaly_id?: number
  title: string
  description: string
  category: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  expected_savings_kwh: number
  expected_savings_cop: number
  expected_co2_reduction_kg: number
  implementation_difficulty?: string
  actions?: string[]
  status: 'pending' | 'in_progress' | 'implemented' | 'rejected'
  implemented_at?: string
  created_at: string
}

export interface DashboardKPI {
  sede: Sede
  period_days: number
  consumption: {
    total_kwh: number
    avg_kwh: number
    max_kwh: number
    min_kwh: number
    record_count: number
  }
  anomalies: {
    total: number
    by_severity: Record<string, number>
    by_type: Record<string, number>
    potential_savings_kwh: number
  }
  recommendations: {
    total_pending: number
    potential_savings_kwh: number
    potential_savings_cop: number
  }
  predictions: {
    avg_predicted_kwh: number
    forecast_count: number
  }
}

export interface ConsumptionTrend {
  sede: Sede
  granularity: 'hourly' | 'daily' | 'weekly'
  start_date: string
  end_date: string
  data_points: Array<{
    timestamp: string
    consumption_kwh: number
    hora?: number
  }>
  statistics: {
    mean: number
    max: number
    min: number
    count: number
  }
}

export interface SectorBreakdown {
  sede: Sede
  start_date: string
  end_date: string
  sectors: Record<string, {
    consumption_kwh: number
    percentage: number
  }>
  total_kwh: number
}

export interface HourlyPattern {
  sede: Sede
  period_days: number
  hourly_averages: Array<{
    hora: number
    avg_consumption: number
  }>
}

export interface EfficiencyScore {
  sede: Sede
  period_days: number
  overall_score: number
  components: {
    anomaly_score: number
    consistency_score: number
    off_hours_score: number
  }
  metrics: {
    total_anomalies: number
    anomaly_rate: number
    off_hours_anomalies: number
  }
}
