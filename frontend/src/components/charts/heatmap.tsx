'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface HeatmapData {
  hour: number;
  day: number;
  value: number;
}

interface ConsumptionHeatmapProps {
  data: HeatmapData[];
  title?: string;
  colorScale?: 'efficiency' | 'intensity';
  showLabels?: boolean;
}

const DAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

// Color scales
const getEfficiencyColor = (value: number, min: number, max: number): string => {
  const normalized = (value - min) / (max - min || 1);
  
  // Green (efficient) to Red (inefficient)
  if (normalized < 0.25) return 'bg-green-100 dark:bg-green-900/30';
  if (normalized < 0.5) return 'bg-yellow-100 dark:bg-yellow-900/30';
  if (normalized < 0.75) return 'bg-orange-100 dark:bg-orange-900/30';
  return 'bg-red-100 dark:bg-red-900/30';
};

const getIntensityColor = (value: number, min: number, max: number): string => {
  const normalized = (value - min) / (max - min || 1);
  
  // Light to dark blue
  if (normalized < 0.2) return 'bg-blue-50 dark:bg-blue-950';
  if (normalized < 0.4) return 'bg-blue-100 dark:bg-blue-900';
  if (normalized < 0.6) return 'bg-blue-200 dark:bg-blue-800';
  if (normalized < 0.8) return 'bg-blue-300 dark:bg-blue-700';
  return 'bg-blue-400 dark:bg-blue-600';
};

export function ConsumptionHeatmap({
  data,
  title = 'Consumo por Hora y Día',
  colorScale = 'intensity',
  showLabels = true,
}: ConsumptionHeatmapProps) {
  const { gridData, minValue, maxValue } = useMemo(() => {
    // Create 7x24 grid
    const grid: (number | null)[][] = Array(7)
      .fill(null)
      .map(() => Array(24).fill(null));
    
    let min = Infinity;
    let max = -Infinity;
    
    data.forEach(({ hour, day, value }) => {
      if (day >= 0 && day < 7 && hour >= 0 && hour < 24) {
        grid[day][hour] = value;
        min = Math.min(min, value);
        max = Math.max(max, value);
      }
    });
    
    return { gridData: grid, minValue: min, maxValue: max };
  }, [data]);

  const getColor = colorScale === 'efficiency' ? getEfficiencyColor : getIntensityColor;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="min-w-[600px]">
            {/* Hour labels */}
            <div className="flex mb-1">
              <div className="w-12"></div>
              {HOURS.map((hour) => (
                <div
                  key={hour}
                  className="flex-1 text-center text-xs text-muted-foreground"
                >
                  {hour % 3 === 0 ? `${hour}` : ''}
                </div>
              ))}
            </div>

            {/* Grid */}
            {DAYS.map((day, dayIndex) => (
              <div key={day} className="flex items-center">
                <div className="w-12 text-xs text-muted-foreground pr-2 text-right">
                  {day}
                </div>
                <div className="flex-1 flex gap-[1px]">
                  {HOURS.map((hour) => {
                    const value = gridData[dayIndex][hour];
                    const hasValue = value !== null;
                    
                    return (
                      <div
                        key={`${dayIndex}-${hour}`}
                        className={`
                          flex-1 aspect-square rounded-sm cursor-pointer
                          transition-all duration-200 hover:scale-110 hover:z-10
                          ${hasValue ? getColor(value!, minValue, maxValue) : 'bg-gray-100 dark:bg-gray-800'}
                        `}
                        title={hasValue ? `${day} ${hour}:00 - ${value!.toFixed(2)} kWh` : `${day} ${hour}:00 - Sin datos`}
                      >
                        {showLabels && hasValue && value! > maxValue * 0.8 && (
                          <span className="text-[6px] text-white font-bold flex items-center justify-center h-full">
                            !
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* Legend */}
            <div className="flex items-center justify-center mt-4 gap-4">
              <span className="text-xs text-muted-foreground">Bajo</span>
              <div className="flex gap-1">
                {colorScale === 'intensity' ? (
                  <>
                    <div className="w-4 h-4 rounded bg-blue-50 dark:bg-blue-950"></div>
                    <div className="w-4 h-4 rounded bg-blue-100 dark:bg-blue-900"></div>
                    <div className="w-4 h-4 rounded bg-blue-200 dark:bg-blue-800"></div>
                    <div className="w-4 h-4 rounded bg-blue-300 dark:bg-blue-700"></div>
                    <div className="w-4 h-4 rounded bg-blue-400 dark:bg-blue-600"></div>
                  </>
                ) : (
                  <>
                    <div className="w-4 h-4 rounded bg-green-100 dark:bg-green-900/30"></div>
                    <div className="w-4 h-4 rounded bg-yellow-100 dark:bg-yellow-900/30"></div>
                    <div className="w-4 h-4 rounded bg-orange-100 dark:bg-orange-900/30"></div>
                    <div className="w-4 h-4 rounded bg-red-100 dark:bg-red-900/30"></div>
                  </>
                )}
              </div>
              <span className="text-xs text-muted-foreground">Alto</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Helper to transform API data to heatmap format
export function transformToHeatmapData(
  consumptionData: Array<{
    timestamp: string;
    energia_total_kwh: number;
  }>
): HeatmapData[] {
  const aggregated: { [key: string]: { sum: number; count: number } } = {};

  consumptionData.forEach((record) => {
    const date = new Date(record.timestamp);
    const hour = date.getHours();
    const day = date.getDay() === 0 ? 6 : date.getDay() - 1; // Convert to Mon=0
    
    const key = `${day}-${hour}`;
    
    if (!aggregated[key]) {
      aggregated[key] = { sum: 0, count: 0 };
    }
    aggregated[key].sum += record.energia_total_kwh;
    aggregated[key].count += 1;
  });

  return Object.entries(aggregated).map(([key, { sum, count }]) => {
    const [day, hour] = key.split('-').map(Number);
    return {
      day,
      hour,
      value: sum / count, // Average
    };
  });
}

export default ConsumptionHeatmap;
