"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { useQueryClient } from "@tanstack/react-query"

export type AlertType = "anomaly" | "prediction" | "recommendation" | "system"
export type AlertSeverity = "low" | "medium" | "high" | "critical"

export interface AlertMetadata {
  sede?: string
  sector?: string
  potential_savings_kwh?: number
  [key: string]: unknown
}

export interface Alert {
  id: string
  type: AlertType
  severity: AlertSeverity
  title: string
  message: string
  timestamp: string
  sede: string
  metadata?: AlertMetadata
}

interface UseWebSocketOptions {
  sede?: string
  onAlert?: (alert: Alert) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocket({
  sede,
  onAlert,
  onConnect,
  onDisconnect,
  onError,
  reconnectInterval = 5000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const [lastAlert, setLastAlert] = useState<Alert | null>(null)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const queryClient = useQueryClient()

  const connect = useCallback(() => {
    if (typeof window === "undefined") return

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws"
    const url = sede ? `${wsUrl}/${sede}` : wsUrl

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        console.log("WebSocket connected")
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
        onConnect?.()
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === "alert") {
            const alert: Alert = {
              id: data.id || crypto.randomUUID(),
              type: data.alert_type,
              severity: data.severity,
              title: data.title,
              message: data.message,
              timestamp: data.timestamp,
              sede: data.sede,
              metadata: data.metadata,
            }

            setLastAlert(alert)
            setAlerts((prev) => [alert, ...prev].slice(0, 100))
            onAlert?.(alert)

            // Invalidate relevant queries based on alert type
            if (alert.type === "anomaly") {
              queryClient.invalidateQueries({ queryKey: ["anomalies"] })
              queryClient.invalidateQueries({ queryKey: ["anomaly-summary"] })
            } else if (alert.type === "prediction") {
              queryClient.invalidateQueries({ queryKey: ["predictions"] })
            } else if (alert.type === "recommendation") {
              queryClient.invalidateQueries({ queryKey: ["recommendations"] })
            }
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error)
        }
      }

      ws.onclose = () => {
        console.log("WebSocket disconnected")
        setIsConnected(false)
        onDisconnect?.()

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current}`)
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        onError?.(error)
      }
    } catch (error) {
      console.error("Error creating WebSocket connection:", error)
    }
  }, [sede, onAlert, onConnect, onDisconnect, onError, reconnectInterval, maxReconnectAttempts, queryClient])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const sendMessage = useCallback((message: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn("WebSocket is not connected")
    }
  }, [])

  const clearAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  const removeAlert = useCallback((alertId: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== alertId))
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastAlert,
    alerts,
    connect,
    disconnect,
    sendMessage,
    clearAlerts,
    removeAlert,
  }
}

// Hook for real-time anomaly alerts
export function useAnomalyAlerts(sede?: string) {
  const [anomalyAlerts, setAnomalyAlerts] = useState<Alert[]>([])

  const handleAlert = useCallback((alert: Alert) => {
    if (alert.type === "anomaly") {
      setAnomalyAlerts((prev) => [alert, ...prev].slice(0, 50))
    }
  }, [])

  const { isConnected, alerts, clearAlerts, removeAlert } = useWebSocket({
    sede,
    onAlert: handleAlert,
  })

  return {
    isConnected,
    anomalyAlerts,
    allAlerts: alerts,
    clearAlerts,
    removeAlert,
  }
}

// Hook for real-time prediction updates
export function usePredictionUpdates(sede?: string) {
  const [lastPrediction, setLastPrediction] = useState<Alert | null>(null)

  const handleAlert = useCallback((alert: Alert) => {
    if (alert.type === "prediction") {
      setLastPrediction(alert)
    }
  }, [])

  const { isConnected } = useWebSocket({
    sede,
    onAlert: handleAlert,
  })

  return {
    isConnected,
    lastPrediction,
  }
}
