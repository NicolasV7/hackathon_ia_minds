"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface EfficiencyGaugeProps {
  score: number
  components: {
    anomaly_score: number
    consistency_score: number
    off_hours_score: number
  }
}

export function EfficiencyGauge({ score, components }: EfficiencyGaugeProps) {
  const getScoreColor = (value: number) => {
    if (value >= 80) return "text-green-600"
    if (value >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBg = (value: number) => {
    if (value >= 80) return "bg-green-500"
    if (value >= 60) return "bg-yellow-500"
    return "bg-red-500"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Score de Eficiencia</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center">
          {/* Main Score Circle */}
          <div className="relative w-32 h-32 mb-4">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                className="text-gray-200"
              />
              <circle
                cx="64"
                cy="64"
                r="56"
                stroke="currentColor"
                strokeWidth="12"
                fill="none"
                strokeDasharray={`${(score / 100) * 352} 352`}
                className={getScoreColor(score)}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-3xl font-bold ${getScoreColor(score)}`}>
                {score}
              </span>
            </div>
          </div>

          {/* Component Scores */}
          <div className="w-full space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Anomalias</span>
                <span className={getScoreColor(components.anomaly_score)}>
                  {components.anomaly_score}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBg(components.anomaly_score)} rounded-full transition-all`}
                  style={{ width: `${components.anomaly_score}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Consistencia</span>
                <span className={getScoreColor(components.consistency_score)}>
                  {components.consistency_score}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBg(components.consistency_score)} rounded-full transition-all`}
                  style={{ width: `${components.consistency_score}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Fuera de horario</span>
                <span className={getScoreColor(components.off_hours_score)}>
                  {components.off_hours_score}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${getScoreBg(components.off_hours_score)} rounded-full transition-all`}
                  style={{ width: `${components.off_hours_score}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
