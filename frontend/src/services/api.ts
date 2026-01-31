// API Configuration for FastAPI Backend
// Use environment variable or default to production backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://77.42.26.173:8000';
const DEBUG = import.meta.env.VITE_DEBUG === 'true';

// Generic fetch wrapper with error handling
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {},
  fallbackData?: () => T
): Promise<T> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`[API] Request: ${url}`);
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`[API] Response from ${endpoint}:`, data);
    return data;
  } catch (error) {
    console.error(`[API] Error for ${endpoint}:`, error);
    if (fallbackData) {
      console.log(`[API] Using fallback data for ${endpoint}`);
      return fallbackData();
    }
    throw error;
  }
}

// Types
export interface Prediction {
  id: string;
  sede: string;
  sector: string;
  fecha: string;
  energia_real: number;
  energia_predicha: number;
  agua_real: number;
  agua_predicha: number;
  co2_real: number;
  co2_predicha: number;
}

export interface Anomaly {
  id: string;
  sede: string;
  sector: string;
  fecha: string;
  tipo: string;
  severidad: 'critica' | 'alta' | 'media' | 'baja';
  estado: 'pendiente' | 'revisada' | 'resuelta';
  descripcion: string;
  valor_detectado: number;
  valor_esperado: number;
}

export interface Recommendation {
  id: string;
  sede: string;
  sector: string;
  tipo: string;
  descripcion: string;
  ahorro_estimado: number;
  prioridad: 'alta' | 'media' | 'baja';
  estado: 'pendiente' | 'implementada' | 'rechazada';
}

export interface DashboardKPIs {
  sedes_monitoreadas: number;
  promedio_energia: number;
  promedio_agua: number;
  huella_carbono: number;
  score_sostenibilidad: number;
  alertas_activas: number;
  total_emisiones: number;
  indice_eficiencia: number;
}

export interface ModelMetrics {
  nombre: string;
  mae: number;
  rmse: number;
  r2_score: number;
  tiempo_entrenamiento: string;
  activo: boolean;
  version: string;
  framework: string;
  fecha_entrenamiento: string;
  datos_entrenamiento: number;
  hiperparametros: Record<string, any>;
  feature_importance: Record<string, number>;
}

export interface ConsumptionTrend {
  fecha: string;
  energia_real: number;
  energia_predicha: number;
  agua_real: number;
  agua_predicha: number;
  co2_real: number;
  co2_predicha: number;
}

export interface SectorBreakdown {
  sector: string;
  energia: number;
  agua: number;
  co2: number;
  porcentaje: number;
}

export interface HourlyPattern {
  hora: string;
  energia: number;
  agua: number;
  co2: number;
}

export interface SedeInfo {
  id: string;
  nombre: string;
  estudiantes: number;
  lat: number;
  lng: number;
  consumo_energia: number;
  consumo_agua: number;
  emisiones_co2: number;
}

// API Functions

// Health Check
export async function healthCheck(): Promise<{ status: string }> {
  return apiRequest('/health', {}, () => ({ status: 'offline' }));
}

// Predictions
export async function createPrediction(data: Partial<Prediction>): Promise<Prediction> {
  return apiRequest('/api/v1/predictions/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createBatchPredictions(data: Partial<Prediction>[]): Promise<Prediction[]> {
  return apiRequest('/api/v1/predictions/batch', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getPredictionsBySede(sede: string): Promise<Prediction[]> {
  return apiRequest(`/api/v1/predictions/sede/${sede}`, {}, () => []);
}

export async function getLatestPredictions(sede: string): Promise<Prediction[]> {
  return apiRequest(`/api/v1/predictions/sede/${sede}/latest`, {}, () => []);
}

export async function getPredictionsByDateRange(startDate: string, endDate: string): Promise<Prediction[]> {
  return apiRequest(`/api/v1/predictions/range?start=${startDate}&end=${endDate}`, {}, () => []);
}

// Anomalies
export async function detectAnomalies(data: { sede?: string; sector?: string }): Promise<Anomaly[]> {
  return apiRequest('/api/v1/anomalies/detect', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getAnomaliesBySede(sede: string): Promise<Anomaly[]> {
  return apiRequest(`/api/v1/anomalies/sede/${sede}`, {}, () => []);
}

export async function getAnomalySummary(sede: string): Promise<{ total: number; por_estado: Record<string, number>; por_severidad: Record<string, number> }> {
  return apiRequest(`/api/v1/anomalies/sede/${sede}/summary`, {}, () => ({
    total: 0,
    por_estado: {},
    por_severidad: {}
  }));
}

export async function getUnresolvedAnomalies(): Promise<Anomaly[]> {
  return apiRequest('/api/v1/anomalies/unresolved', {}, () => getMockAnomalies());
}

export async function getAnomaliesByDateRange(startDate: string, endDate: string): Promise<Anomaly[]> {
  return apiRequest(`/api/v1/anomalies/range?start=${startDate}&end=${endDate}`, {}, () => []);
}

export async function updateAnomalyStatus(anomalyId: string, estado: string): Promise<Anomaly> {
  return apiRequest(`/api/v1/anomalies/${anomalyId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ estado }),
  });
}

// Recommendations
export async function generateRecommendations(data: { sede?: string; sector?: string }): Promise<Recommendation[]> {
  return apiRequest('/api/v1/recommendations/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getRecommendationsBySede(sede: string): Promise<Recommendation[]> {
  return apiRequest(`/api/v1/recommendations/sede/${sede}`, {}, () => []);
}

export async function getPendingRecommendations(): Promise<Recommendation[]> {
  return apiRequest('/api/v1/recommendations/pending', {}, () => []);
}

export async function updateRecommendationStatus(recommendationId: string, estado: string): Promise<Recommendation> {
  return apiRequest(`/api/v1/recommendations/${recommendationId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ estado }),
  });
}

// Analytics
export async function getDashboardKPIs(sede?: string): Promise<DashboardKPIs> {
  const endpoint = sede ? `/api/v1/analytics/dashboard/${sede}` : '/api/v1/analytics/dashboard/all';
  return apiRequest(endpoint, {}, () => getMockDashboardKPIs());
}

export async function getConsumptionTrends(sede: string): Promise<ConsumptionTrend[]> {
  return apiRequest(`/api/v1/analytics/consumption/trends/${sede}`, {}, () => getMockConsumptionTrends());
}

export async function getSectorBreakdown(sede: string): Promise<SectorBreakdown[]> {
  return apiRequest(`/api/v1/analytics/consumption/sectors/${sede}`, {}, () => []);
}

export async function getHourlyPatterns(sede: string): Promise<HourlyPattern[]> {
  return apiRequest(`/api/v1/analytics/patterns/hourly/${sede}`, {}, () => []);
}

export async function getEfficiencyScore(sede: string): Promise<{ score: number; detalles: Record<string, number> }> {
  return apiRequest(`/api/v1/analytics/efficiency/score/${sede}`, {}, () => ({ score: 0, detalles: {} }));
}

// GET /api/v1/models/metrics - Get all model metrics
export async function getModelMetrics(): Promise<ModelMetrics[]> {
  return apiRequest('/api/v1/models/metrics', {}, () => getMockModelMetrics());
}

// GET /api/v1/models/{model_name}/predictions - Get model predictions comparison
export async function getModelPredictions(modelName: string): Promise<{ real: number[]; predicho: number[] }> {
  return apiRequest(`/api/v1/models/${modelName}/predictions`, {}, () => getMockModelPredictions());
}

// GET /api/v1/analytics/correlations/{sede} - Get correlation matrix
export async function getCorrelationMatrix(sede: string): Promise<{ variables: string[]; matrix: number[][] }> {
  return apiRequest(`/api/v1/analytics/correlations/${sede}`, {}, () => getMockCorrelations());
}

// GET /api/v1/analytics/academic-periods - Get consumption by academic period
export async function getAcademicPeriodConsumption(): Promise<{ periodo: string; energia: number; agua: number; co2: number }[]> {
  return apiRequest('/api/v1/analytics/academic-periods', {}, () => getMockAcademicPeriods());
}

// GET /api/v1/optimization/opportunities - Get optimization opportunities
export async function getOptimizationOpportunities(): Promise<{ area: string; potencial_ahorro: number; descripcion: string }[]> {
  return apiRequest('/api/v1/optimization/opportunities', {}, () => getMockOpportunities());
}

// GET /api/v1/optimization/savings-projection - Get savings projection (waterfall)
export async function getSavingsProjection(): Promise<{ categoria: string; valor: number; tipo: 'ahorro' | 'total' }[]> {
  return apiRequest('/api/v1/optimization/savings-projection', {}, () => getMockSavingsProjection());
}

// GET /api/v1/optimization/sustainability - Get sustainability contribution
export async function getSustainabilityContribution(): Promise<{ arboles_salvados: number; agua_ahorrada: number; co2_reducido: number }> {
  return apiRequest('/api/v1/optimization/sustainability', {}, () => getMockSustainability());
}

// GET /api/v1/optimization/pareto - Get pareto analysis
export async function getParetoAnalysis(): Promise<{ causa: string; porcentaje: number; acumulado: number }[]> {
  return apiRequest('/api/v1/optimization/pareto', {}, () => getMockPareto());
}

// GET /api/v1/alerts/evolution - Get alert evolution over time
export async function getAlertEvolution(): Promise<{ mes: string; anomalias: number; desbalances: number; criticas: number }[]> {
  return apiRequest('/api/v1/alerts/evolution', {}, () => getMockAlertEvolution());
}

// GET /api/v1/explainability/shap/{variable} - Get SHAP values
export async function getShapValues(variable: 'energia' | 'agua' | 'co2'): Promise<{ feature: string; value: number }[]> {
  return apiRequest(`/api/v1/explainability/shap/${variable}`, {}, () => getMockShapValues());
}

// GET /api/v1/explainability/confidence - Get model confidence
export async function getModelConfidence(): Promise<{ confianza_prediccion: number; certeza_recomendacion: number; modelo_activo: string }> {
  return apiRequest('/api/v1/explainability/confidence', {}, () => getMockConfidence());
}

// POST /api/v1/chat - Chat with AI assistant
export async function sendChatMessage(message: string): Promise<{ response: string }> {
  return apiRequest('/api/v1/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }, () => ({ response: 'Lo siento, no puedo procesar tu solicitud en este momento. Por favor, intenta de nuevo.' }));
}

// GET /api/v1/sedes - Get all sedes info
export async function getSedesInfo(): Promise<SedeInfo[]> {
  return apiRequest('/api/v1/sedes', {}, () => getMockSedes());
}

// Mock data functions for fallback
function getMockModelMetrics(): ModelMetrics[] {
  return [
    {
      nombre: 'XGBoost',
      mae: 0.042,
      rmse: 0.068,
      r2_score: 0.94,
      tiempo_entrenamiento: '3.2 min',
      activo: true,
      version: '2.0.3',
      framework: 'Scikit-Learn 1.3.2',
      fecha_entrenamiento: '2025-01-15',
      datos_entrenamiento: 15240,
      hiperparametros: {
        n_estimators: 100,
        max_depth: 6,
        learning_rate: 0.1,
        subsample: 0.8,
        colsample_bytree: 0.8,
        min_child_weight: 1,
      },
      feature_importance: {
        volumen_corregido: 0.35,
        hora_del_dia: 0.22,
        dia_semana: 0.18,
        temperatura: 0.13,
        ocupacion_estimada: 0.08,
        mes: 0.04,
      },
    },
    {
      nombre: 'Prophet',
      mae: 0.058,
      rmse: 0.089,
      r2_score: 0.88,
      tiempo_entrenamiento: '5.1 min',
      activo: false,
      version: '1.1.4',
      framework: 'Meta Prophet',
      fecha_entrenamiento: '2025-01-15',
      datos_entrenamiento: 15240,
      hiperparametros: {},
      feature_importance: {},
    },
    {
      nombre: 'LSTM',
      mae: 0.051,
      rmse: 0.078,
      r2_score: 0.91,
      tiempo_entrenamiento: '12.5 min',
      activo: false,
      version: '2.1.0',
      framework: 'TensorFlow 2.15',
      fecha_entrenamiento: '2025-01-15',
      datos_entrenamiento: 15240,
      hiperparametros: {},
      feature_importance: {},
    },
  ];
}

function getMockModelPredictions(): { real: number[]; predicho: number[] } {
  return {
    real: [4.5, 5.2, 6.1, 7.3, 8.2, 9.5, 10.1, 11.2, 12.5, 11.8, 10.5, 9.2, 8.1, 7.5, 6.8],
    predicho: [4.3, 5.0, 6.3, 7.1, 8.5, 9.3, 10.4, 11.0, 12.8, 11.5, 10.2, 9.5, 8.3, 7.2, 7.0],
  };
}

function getMockCorrelations(): { variables: string[]; matrix: number[][] } {
  return {
    variables: ['Energia', 'Agua', 'CO2', 'Temperatura'],
    matrix: [
      [1.0, 0.82, 0.95, -0.45],
      [0.82, 1.0, 0.78, -0.32],
      [0.95, 0.78, 1.0, -0.41],
      [-0.45, -0.32, -0.41, 1.0],
    ],
  };
}

function getMockAcademicPeriods(): { periodo: string; energia: number; agua: number; co2: number }[] {
  return [
    { periodo: 'Semestre 1 2024', energia: 55000, agua: 12000, co2: 85 },
    { periodo: 'Vacaciones Jun', energia: 28000, agua: 6000, co2: 42 },
    { periodo: 'Semestre 2 2024', energia: 52000, agua: 11500, co2: 80 },
    { periodo: 'Vacaciones Dic', energia: 25000, agua: 5500, co2: 38 },
    { periodo: 'Semestre 1 2025', energia: 48000, agua: 10800, co2: 74 },
  ];
}

function getMockOpportunities(): { area: string; potencial_ahorro: number; descripcion: string }[] {
  return [
    { area: 'Climatizacion inteligente', potencial_ahorro: 15200, descripcion: 'Optimizar sistemas HVAC con sensores de ocupacion' },
    { area: 'Sensores de presencia', potencial_ahorro: 8500, descripcion: 'Iluminacion automatica en aulas y pasillos' },
    { area: 'Equipos eficientes', potencial_ahorro: 12300, descripcion: 'Reemplazo de equipos de laboratorio obsoletos' },
    { area: 'Paneles solares', potencial_ahorro: 22000, descripcion: 'Instalacion de energia solar en techos' },
  ];
}

function getMockSavingsProjection(): { categoria: string; valor: number; tipo: 'ahorro' | 'total' }[] {
  return [
    { categoria: 'Consumo actual', valor: 100000, tipo: 'total' },
    { categoria: 'Reduccion energia', valor: -15000, tipo: 'ahorro' },
    { categoria: 'Reduccion agua', valor: -8000, tipo: 'ahorro' },
    { categoria: 'Reduccion CO2', valor: -12000, tipo: 'ahorro' },
    { categoria: 'Eficiencia operativa', valor: -5000, tipo: 'ahorro' },
    { categoria: 'Consumo proyectado', valor: 60000, tipo: 'total' },
  ];
}

function getMockSustainability(): { arboles_salvados: number; agua_ahorrada: number; co2_reducido: number } {
  return {
    arboles_salvados: 847,
    agua_ahorrada: 12500,
    co2_reducido: 125.3,
  };
}

function getMockPareto(): { causa: string; porcentaje: number; acumulado: number }[] {
  return [
    { causa: 'Climatizacion 24/7', porcentaje: 35, acumulado: 35 },
    { causa: 'Iluminacion sin uso', porcentaje: 25, acumulado: 60 },
    { causa: 'Equipos standby', porcentaje: 18, acumulado: 78 },
    { causa: 'Fugas de agua', porcentaje: 12, acumulado: 90 },
    { causa: 'Otros', porcentaje: 10, acumulado: 100 },
  ];
}

function getMockAlertEvolution(): { mes: string; anomalias: number; desbalances: number; criticas: number }[] {
  return [
    { mes: 'Ene', anomalias: 8, desbalances: 4, criticas: 2 },
    { mes: 'Feb', anomalias: 10, desbalances: 5, criticas: 3 },
    { mes: 'Mar', anomalias: 12, desbalances: 6, criticas: 2 },
    { mes: 'Abr', anomalias: 15, desbalances: 8, criticas: 4 },
    { mes: 'May', anomalias: 11, desbalances: 5, criticas: 2 },
    { mes: 'Jun', anomalias: 9, desbalances: 4, criticas: 1 },
    { mes: 'Jul', anomalias: 13, desbalances: 6, criticas: 3 },
  ];
}

function getMockShapValues(): { feature: string; value: number }[] {
  return [
    { feature: 'hora_del_dia', value: 18 },
    { feature: 'dia_semana', value: 15 },
    { feature: 'temperatura', value: 12 },
    { feature: 'ocupacion', value: 8 },
    { feature: 'historico', value: -5 },
    { feature: 'estacionalidad', value: -8 },
  ];
}

function getMockConfidence(): { confianza_prediccion: number; certeza_recomendacion: number; modelo_activo: string } {
  return {
    confianza_prediccion: 94.2,
    certeza_recomendacion: 87.5,
    modelo_activo: 'XGBoost v2.0',
  };
}

function getMockSedes(): SedeInfo[] {
  return [
    { id: 'tunja', nombre: 'Tunja (Principal)', estudiantes: 18000, lat: 5.5353, lng: -73.3678, consumo_energia: 45000, consumo_agua: 9500, emisiones_co2: 68 },
    { id: 'duitama', nombre: 'Duitama', estudiantes: 5500, lat: 5.8267, lng: -73.0333, consumo_energia: 18200, consumo_agua: 3800, emisiones_co2: 27 },
    { id: 'sogamoso', nombre: 'Sogamoso', estudiantes: 6000, lat: 5.7147, lng: -72.9314, consumo_energia: 15500, consumo_agua: 3200, emisiones_co2: 23 },
    { id: 'chiquinquira', nombre: 'Chiquinquira', estudiantes: 2000, lat: 5.6167, lng: -73.8167, consumo_energia: 6800, consumo_agua: 1400, emisiones_co2: 10 },
  ];
}

function getMockDashboardKPIs(): DashboardKPIs {
  return {
    sedes_monitoreadas: 4,
    promedio_energia: 21400,
    promedio_agua: 4200,
    huella_carbono: 3.98,
    score_sostenibilidad: 78,
    alertas_activas: 5,
    total_emisiones: 125.3,
    indice_eficiencia: 9.2,
  };
}

function getMockConsumptionTrends(): ConsumptionTrend[] {
  return [
    { fecha: 'Ene', energia_real: 28000, energia_predicha: 27500, agua_real: 5800, agua_predicha: 5600, co2_real: 42, co2_predicha: 41 },
    { fecha: 'Feb', energia_real: 30000, energia_predicha: 29800, agua_real: 6200, agua_predicha: 6000, co2_real: 45, co2_predicha: 44 },
    { fecha: 'Mar', energia_real: 32000, energia_predicha: 31500, agua_real: 6500, agua_predicha: 6300, co2_real: 48, co2_predicha: 47 },
    { fecha: 'Abr', energia_real: 35000, energia_predicha: 34000, agua_real: 7000, agua_predicha: 6800, co2_real: 52, co2_predicha: 51 },
    { fecha: 'May', energia_real: 38000, energia_predicha: 37500, agua_real: 7500, agua_predicha: 7300, co2_real: 57, co2_predicha: 56 },
    { fecha: 'Jun', energia_real: 42000, energia_predicha: 41000, agua_real: 8200, agua_predicha: 8000, co2_real: 63, co2_predicha: 62 },
    { fecha: 'Jul', energia_real: 45000, energia_predicha: 44500, agua_real: 8800, agua_predicha: 8600, co2_real: 68, co2_predicha: 67 },
    { fecha: 'Ago', energia_real: 48000, energia_predicha: 47000, agua_real: 9200, agua_predicha: 9000, co2_real: 72, co2_predicha: 71 },
    { fecha: 'Sep', energia_real: 50000, energia_predicha: 49500, agua_real: 9500, agua_predicha: 9300, co2_real: 75, co2_predicha: 74 },
  ];
}

function getMockAnomalies(): Anomaly[] {
  return [
    { id: '1', sede: 'Tunja', sector: 'Comedores', fecha: '2025-01-30 08:30', tipo: 'anomalia', severidad: 'critica', estado: 'pendiente', descripcion: 'Consumo anomalo detectado: +45% respecto al baseline', valor_detectado: 4500, valor_esperado: 3100 },
    { id: '2', sede: 'Duitama', sector: 'Laboratorios', fecha: '2025-01-30 07:15', tipo: 'desbalance', severidad: 'alta', estado: 'revisada', descripcion: 'Desbalance en consumo entre horario laboral y nocturno', valor_detectado: 1200, valor_esperado: 800 },
    { id: '3', sede: 'Sogamoso', sector: 'Oficinas', fecha: '2025-01-29 14:20', tipo: 'anomalia', severidad: 'media', estado: 'pendiente', descripcion: 'Consumo elevado detectado en fin de semana', valor_detectado: 890, valor_esperado: 200 },
  ];
}
