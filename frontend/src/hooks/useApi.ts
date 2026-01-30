"use client"

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { Sede } from '@/lib/types'
import {
  analyticsService,
  predictionsService,
  anomaliesService,
  recommendationsService,
} from '@/lib/api/services'

// ============== Analytics Hooks ==============

export function useDashboardKPIs(sede: Sede, days: number = 30) {
  return useQuery({
    queryKey: ['dashboard', sede, days],
    queryFn: () => analyticsService.getDashboardKPIs(sede, days),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useConsumptionTrends(
  sede: Sede,
  startDate: string,
  endDate: string,
  granularity: 'hourly' | 'daily' | 'weekly' = 'hourly'
) {
  return useQuery({
    queryKey: ['consumption-trends', sede, startDate, endDate, granularity],
    queryFn: () => analyticsService.getConsumptionTrends(sede, startDate, endDate, granularity),
    enabled: !!startDate && !!endDate,
  })
}

export function useSectorBreakdown(sede: Sede, startDate: string, endDate: string) {
  return useQuery({
    queryKey: ['sector-breakdown', sede, startDate, endDate],
    queryFn: () => analyticsService.getSectorBreakdown(sede, startDate, endDate),
    enabled: !!startDate && !!endDate,
  })
}

export function useHourlyPatterns(sede: Sede, days: number = 30) {
  return useQuery({
    queryKey: ['hourly-patterns', sede, days],
    queryFn: () => analyticsService.getHourlyPatterns(sede, days),
  })
}

export function useEfficiencyScore(sede: Sede, days: number = 30) {
  return useQuery({
    queryKey: ['efficiency-score', sede, days],
    queryFn: () => analyticsService.getEfficiencyScore(sede, days),
  })
}

// ============== Predictions Hooks ==============

export function usePredictions(sede: Sede, skip = 0, limit = 100) {
  return useQuery({
    queryKey: ['predictions', sede, skip, limit],
    queryFn: () => predictionsService.getPredictionsBySede(sede, skip, limit),
  })
}

export function useLatestPredictions(sede: Sede, limit = 24) {
  return useQuery({
    queryKey: ['predictions-latest', sede, limit],
    queryFn: () => predictionsService.getLatestPredictions(sede, limit),
  })
}

export function useCreatePrediction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: predictionsService.createPrediction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] })
    },
  })
}

export function useCreateBatchPredictions() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({
      sede,
      startTimestamp,
      horizonHours,
      temperaturaExteriorC,
      ocupacionPct,
    }: {
      sede: Sede
      startTimestamp: string
      horizonHours?: number
      temperaturaExteriorC?: number
      ocupacionPct?: number
    }) => predictionsService.createBatchPredictions(
      sede,
      startTimestamp,
      horizonHours,
      temperaturaExteriorC,
      ocupacionPct
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictions'] })
    },
  })
}

// ============== Anomalies Hooks ==============

export function useAnomalies(sede: Sede, severity?: string, skip = 0, limit = 100) {
  return useQuery({
    queryKey: ['anomalies', sede, severity, skip, limit],
    queryFn: () => anomaliesService.getAnomaliesBySede(sede, severity, skip, limit),
  })
}

export function useAnomalySummary(sede: Sede) {
  return useQuery({
    queryKey: ['anomaly-summary', sede],
    queryFn: () => anomaliesService.getAnomalySummary(sede),
  })
}

export function useUnresolvedAnomalies(sede?: Sede) {
  return useQuery({
    queryKey: ['anomalies-unresolved', sede],
    queryFn: () => anomaliesService.getUnresolvedAnomalies(sede),
  })
}

export function useDetectAnomalies() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({
      sede,
      days,
      severityThreshold,
    }: {
      sede: Sede
      days?: number
      severityThreshold?: string
    }) => anomaliesService.detectAnomalies(sede, days, severityThreshold),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['anomalies'] })
    },
  })
}

export function useUpdateAnomalyStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ anomalyId, status }: { anomalyId: number; status: string }) =>
      anomaliesService.updateAnomalyStatus(anomalyId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['anomalies'] })
    },
  })
}

// ============== Recommendations Hooks ==============

export function useRecommendations(sede: Sede, priority?: string, status?: string) {
  return useQuery({
    queryKey: ['recommendations', sede, priority, status],
    queryFn: () => recommendationsService.getRecommendationsBySede(sede, priority, status),
  })
}

export function usePendingRecommendations(sede?: Sede) {
  return useQuery({
    queryKey: ['recommendations-pending', sede],
    queryFn: () => recommendationsService.getPendingRecommendations(sede),
  })
}

export function useGenerateRecommendations() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ sede, days }: { sede: Sede; days?: number }) =>
      recommendationsService.generateRecommendations(sede, days),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
    },
  })
}

export function useUpdateRecommendationStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({
      recommendationId,
      status,
      implementationNotes,
    }: {
      recommendationId: number
      status: string
      implementationNotes?: string
    }) => recommendationsService.updateRecommendationStatus(
      recommendationId,
      status,
      implementationNotes
    ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations'] })
    },
  })
}
