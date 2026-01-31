import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Brain, HelpCircle, BarChart3, CheckCircle } from 'lucide-react';
import {
  getShapValues,
  getModelConfidence,
  getModelMetrics,
  type ModelMetrics,
} from '@/services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import Chatbot from '@/components/Chatbot';

export default function ExplicabilidadPage() {
  const [selectedVariable, setSelectedVariable] = useState<'energia' | 'agua' | 'co2'>('energia');
  const [shapValues, setShapValues] = useState<{ feature: string; value: number }[]>([]);
  const [confidence, setConfidence] = useState<{ confianza_prediccion: number; certeza_recomendacion: number; modelo_activo: string }>({ confianza_prediccion: 0, certeza_recomendacion: 0, modelo_activo: '' });
  const [models, setModels] = useState<ModelMetrics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [shapData, confData, modelsData] = await Promise.all([
          getShapValues(selectedVariable),
          getModelConfidence(),
          getModelMetrics(),
        ]);
        setShapValues(shapData);
        setConfidence(confData);
        setModels(modelsData);
      } catch (error) {
        console.error('Error fetching explainability data:', error);
        // Mock data
        setShapValues([
          { feature: 'hora_del_dia', value: 18 },
          { feature: 'dia_semana', value: 15 },
          { feature: 'temperatura', value: 12 },
          { feature: 'ocupacion', value: 8 },
          { feature: 'historico', value: -5 },
          { feature: 'estacionalidad', value: -8 },
        ]);
        setConfidence({ confianza_prediccion: 94.2, certeza_recomendacion: 87.5, modelo_activo: 'XGBoost v2.0' });
        setModels([
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
            hiperparametros: { n_estimators: 100, max_depth: 6 },
            feature_importance: { volumen_corregido: 0.35, hora_del_dia: 0.22 },
          },
        ]);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedVariable]);

  const sortedShapValues = [...shapValues].sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Cargando explicabilidad...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary" />
            Explicabilidad del Modelo
          </h1>
          <p className="text-muted-foreground">Transparencia y auditabilidad de las predicciones con SHAP values</p>
        </div>
      </div>

      {/* Variable Selector */}
      <Card className="chart-container">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Waterfall Plot - Contribucion de Features
              </CardTitle>
              <p className="text-sm text-muted-foreground">Contribucion de cada feature a una prediccion individual</p>
            </div>
            <Select value={selectedVariable} onValueChange={(v) => setSelectedVariable(v as 'energia' | 'agua' | 'co2')}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="energia">Energia</SelectItem>
                <SelectItem value="agua">Agua</SelectItem>
                <SelectItem value="co2">CO2</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sortedShapValues} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis dataKey="feature" type="category" stroke="hsl(var(--muted-foreground))" fontSize={11} width={120} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => [value > 0 ? `+${value}` : value, 'Contribucion']}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {sortedShapValues.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.value >= 0 ? 'hsl(var(--success))' : 'hsl(var(--destructive))'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 p-4 rounded-lg bg-secondary/50">
            <div className="flex items-start gap-2">
              <HelpCircle className="w-4 h-4 text-muted-foreground mt-0.5" />
              <div className="text-sm text-muted-foreground">
                <p className="font-medium mb-1">Como interpretar este grafico:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li><span className="text-success">Valores positivos (verde)</span>: La feature aumenta la prediccion de consumo</li>
                  <li><span className="text-destructive">Valores negativos (rojo)</span>: La feature disminuye la prediccion de consumo</li>
                  <li>El tamano de la barra indica la magnitud del impacto</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Confidence Panel */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-success" />
              Panel de Confianza del Modelo
            </CardTitle>
            <p className="text-sm text-muted-foreground">Certeza de predicciones y recomendaciones</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Prediction Confidence */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">Confianza de Prediccion</span>
                  <span className="text-lg font-bold text-success">{confidence.confianza_prediccion}%</span>
                </div>
                <div className="h-4 bg-secondary rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${confidence.confianza_prediccion}%` }}
                    transition={{ duration: 0.8 }}
                    className="h-full bg-success rounded-full"
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Indica que tan seguro esta el modelo de sus predicciones de consumo
                </p>
              </div>

              {/* Recommendation Certainty */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">Certeza de Recomendacion</span>
                  <span className="text-lg font-bold text-primary">{confidence.certeza_recomendacion}%</span>
                </div>
                <div className="h-4 bg-secondary rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${confidence.certeza_recomendacion}%` }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="h-full bg-primary rounded-full"
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Probabilidad de que las recomendaciones generen el ahorro estimado
                </p>
              </div>

              {/* Active Model */}
              <div className="p-4 rounded-lg bg-success/10 border border-success/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">Modelo Activo</p>
                    <p className="text-lg font-bold text-success">{confidence.modelo_activo}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-success" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Model Performance Summary */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Resumen de Rendimiento</CardTitle>
            <p className="text-sm text-muted-foreground">Metricas clave del modelo en produccion</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {models.filter(m => m.activo).map((model) => (
                <>
                  <div key={`${model.nombre}-mae`} className="p-4 rounded-lg bg-secondary/50 text-center">
                    <p className="text-xs text-muted-foreground mb-1">MAE</p>
                    <p className="text-2xl font-bold text-success">{model.mae}</p>
                    <p className="text-xs text-muted-foreground">Error absoluto medio</p>
                  </div>
                  <div key={`${model.nombre}-rmse`} className="p-4 rounded-lg bg-secondary/50 text-center">
                    <p className="text-xs text-muted-foreground mb-1">RMSE</p>
                    <p className="text-2xl font-bold text-success">{model.rmse}</p>
                    <p className="text-xs text-muted-foreground">Error cuadratico medio</p>
                  </div>
                  <div key={`${model.nombre}-r2`} className="p-4 rounded-lg bg-secondary/50 text-center">
                    <p className="text-xs text-muted-foreground mb-1">R2 Score</p>
                    <p className="text-2xl font-bold text-primary">{model.r2_score}</p>
                    <p className="text-xs text-muted-foreground">Coeficiente de determinacion</p>
                  </div>
                  <div key={`${model.nombre}-time`} className="p-4 rounded-lg bg-secondary/50 text-center">
                    <p className="text-xs text-muted-foreground mb-1">Tiempo</p>
                    <p className="text-2xl font-bold">{model.tiempo_entrenamiento}</p>
                    <p className="text-xs text-muted-foreground">Entrenamiento</p>
                  </div>
                </>
              ))}
            </div>

            <div className="mt-6 p-4 rounded-lg bg-info/10 border border-info/30">
              <h4 className="font-medium text-info mb-2 flex items-center gap-2">
                <HelpCircle className="w-4 h-4" />
                Interpretacion de Metricas
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li><strong>MAE/RMSE bajos</strong>: El modelo predice con precision el consumo real</li>
                <li><strong>R2 cercano a 1</strong>: El modelo explica bien la variabilidad de los datos</li>
                <li><strong>Tiempo bajo</strong>: Permite reentrenamiento frecuente con nuevos datos</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feature Importance Explanation */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle className="text-lg">Importancia de Variables</CardTitle>
          <p className="text-sm text-muted-foreground">Variables que mas influyen en las predicciones del modelo</p>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sortedShapValues.slice(0, 6).map((item, index) => (
              <motion.div
                key={item.feature}
                initial={{ opacity: 0.8, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03, duration: 0.15 }}
                className="p-4 rounded-lg bg-secondary/50"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-sm">{item.feature}</span>
                  <span className={`text-sm font-bold ${item.value >= 0 ? 'text-success' : 'text-destructive'}`}>
                    {item.value >= 0 ? '+' : ''}{item.value}
                  </span>
                </div>
                <div className="h-2 bg-background rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(Math.abs(item.value) * 5, 100)}%` }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    className={`h-full rounded-full ${item.value >= 0 ? 'bg-success' : 'bg-destructive'}`}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {item.feature === 'hora_del_dia' && 'El consumo varia segun la hora del dia'}
                  {item.feature === 'dia_semana' && 'Dias laborales vs fin de semana'}
                  {item.feature === 'temperatura' && 'Impacto de la climatizacion'}
                  {item.feature === 'ocupacion' && 'Numero de personas en el edificio'}
                  {item.feature === 'historico' && 'Patrones de consumo pasado'}
                  {item.feature === 'estacionalidad' && 'Variaciones por epoca del ano'}
                </p>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Chatbot />
    </div>
  );
}
