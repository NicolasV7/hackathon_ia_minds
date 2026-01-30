import apiClient from './client'
import type {
  Sede,
  Prediction,
  PredictionRequest,
  Anomaly,
  AnomalySummary,
  Recommendation,
  DashboardKPI,
  ConsumptionTrend,
  SectorBreakdown,
  HourlyPattern,
  EfficiencyScore,
} from '../types'

// ============== Analytics Service ==============

export const analyticsService = {
  getDashboardKPIs: async (sede: Sede, days: number = 30): Promise<DashboardKPI> => {
    const { data } = await apiClient.get(`/analytics/dashboard/${sede}`, {
      params: { days },
    })
    return data
  },

  getConsumptionTrends: async (
    sede: Sede,
    startDate: string,
    endDate: string,
    granularity: 'hourly' | 'daily' | 'weekly' = 'hourly'
  ): Promise<ConsumptionTrend> => {
    const { data } = await apiClient.get(`/analytics/consumption/trends/${sede}`, {
      params: { start_date: startDate, end_date: endDate, granularity },
    })
    return data
  },

  getSectorBreakdown: async (
    sede: Sede,
    startDate: string,
    endDate: string
  ): Promise<SectorBreakdown> => {
    const { data } = await apiClient.get(`/analytics/consumption/sectors/${sede}`, {
      params: { start_date: startDate, end_date: endDate },
    })
    return data
  },

  getHourlyPatterns: async (sede: Sede, days: number = 30): Promise<HourlyPattern> => {
    const { data } = await apiClient.get(`/analytics/patterns/hourly/${sede}`, {
      params: { days },
    })
    return data
  },

  getEfficiencyScore: async (sede: Sede, days: number = 30): Promise<EfficiencyScore> => {
    const { data } = await apiClient.get(`/analytics/efficiency/score/${sede}`, {
      params: { days },
    })
    return data
  },
}

// ============== Predictions Service ==============

export const predictionsService = {
  createPrediction: async (request: PredictionRequest): Promise<Prediction> => {
    const { data } = await apiClient.post('/predictions/', request)
    return data
  },

  createBatchPredictions: async (
    sede: Sede,
    startTimestamp: string,
    horizonHours: number = 24,
    temperaturaExteriorC: number = 20,
    ocupacionPct: number = 70
  ): Promise<Prediction[]> => {
    const { data } = await apiClient.post('/predictions/batch', {
      sede,
      start_timestamp: startTimestamp,
      horizon_hours: horizonHours,
      temperatura_exterior_c: temperaturaExteriorC,
      ocupacion_pct: ocupacionPct,
    })
    return data
  },

  getPredictionsBySede: async (
    sede: Sede,
    skip: number = 0,
    limit: number = 100
  ): Promise<Prediction[]> => {
    const { data } = await apiClient.get(`/predictions/sede/${sede}`, {
      params: { skip, limit },
    })
    return data
  },

  getLatestPredictions: async (sede: Sede, limit: number = 24): Promise<Prediction[]> => {
    const { data } = await apiClient.get(`/predictions/sede/${sede}/latest`, {
      params: { limit },
    })
    return data
  },
}

// ============== Anomalies Service ==============

export const anomaliesService = {
  detectAnomalies: async (
    sede: Sede,
    days: number = 7,
    severityThreshold?: string
  ): Promise<Anomaly[]> => {
    const { data } = await apiClient.post('/anomalies/detect', {
      sede,
      days,
      severity_threshold: severityThreshold,
    })
    return data
  },

  getAnomaliesBySede: async (
    sede: Sede,
    severity?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<Anomaly[]> => {
    const { data } = await apiClient.get(`/anomalies/sede/${sede}`, {
      params: { severity, skip, limit },
    })
    return data
  },

  getAnomalySummary: async (sede: Sede): Promise<AnomalySummary> => {
    const { data } = await apiClient.get(`/anomalies/sede/${sede}/summary`)
    return data
  },

  getUnresolvedAnomalies: async (sede?: Sede): Promise<Anomaly[]> => {
    const { data } = await apiClient.get('/anomalies/unresolved', {
      params: sede ? { sede } : {},
    })
    return data
  },

  updateAnomalyStatus: async (
    anomalyId: number,
    status: string
  ): Promise<Anomaly> => {
    const { data } = await apiClient.patch(`/anomalies/${anomalyId}/status`, {
      status,
    })
    return data
  },
}

// ============== Recommendations Service ==============

export const recommendationsService = {
  generateRecommendations: async (
    sede: Sede,
    days: number = 7
  ): Promise<Recommendation[]> => {
    const { data } = await apiClient.post('/recommendations/generate', {
      sede,
      days,
    })
    return data
  },

  getRecommendationsBySede: async (
    sede: Sede,
    priority?: string,
    status?: string,
    skip: number = 0,
    limit: number = 100
  ): Promise<Recommendation[]> => {
    const { data } = await apiClient.get(`/recommendations/sede/${sede}`, {
      params: { priority, status, skip, limit },
    })
    return data
  },

  getPendingRecommendations: async (sede?: Sede): Promise<Recommendation[]> => {
    const { data } = await apiClient.get('/recommendations/pending', {
      params: sede ? { sede } : {},
    })
    return data
  },

  updateRecommendationStatus: async (
    recommendationId: number,
    status: string,
    implementationNotes?: string
  ): Promise<Recommendation> => {
    const { data } = await apiClient.patch(`/recommendations/${recommendationId}/status`, {
      status,
      implementation_notes: implementationNotes,
    })
    return data
  },
}
