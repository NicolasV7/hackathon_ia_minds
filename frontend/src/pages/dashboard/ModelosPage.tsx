import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { CheckCircle, Boxes } from 'lucide-react';
import { getModelMetrics, getModelPredictions, type ModelMetrics } from '@/services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis,
} from 'recharts';
import Chatbot from '@/components/Chatbot';
import { LoadingScreen } from '@/components/ui/loading-screen';

export default function ModelosPage() {
  const [models, setModels] = useState<ModelMetrics[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('XGBoost');
  const [predictions, setPredictions] = useState<{ real: number[]; predicho: number[] }>({ real: [], predicho: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [modelsData, predsData] = await Promise.all([
          getModelMetrics(),
          getModelPredictions(selectedModel),
        ]);
        setModels(modelsData);
        setPredictions(predsData);
      } catch (error) {
        console.error('Error fetching models data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedModel]);

  const activeModel = models.find(m => m.activo) || models[0];
  const selectedModelData = models.find(m => m.nombre === selectedModel) || models[0];

  const r2Data = models.map(m => ({ name: m.nombre, r2: m.r2_score }));
  
  const scatterData = predictions.real.map((real, i) => ({
    real,
    predicho: predictions.predicho[i],
  }));

  if (loading) {
    return (
      <div className="p-6">
        <LoadingScreen 
          variant="models"
          title="Cargando Modelos"
          description="Obteniendo metricas y predicciones de ML..."
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <Boxes className="w-6 h-6 text-purple-400" />
          Modelos Predictivos
        </h1>
        <p className="text-muted-foreground">Comparacion de modelos XGBoost, Prophet y LSTM - Metricas, hiperparametros y explicabilidad</p>
      </div>

      {/* Model Comparison Cards */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle className="text-lg">Comparacion de Modelos (Voting)</CardTitle>
          <p className="text-sm text-muted-foreground">Ensamble de predicciones</p>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            {models.map((model) => (
              <motion.div
                key={model.nombre}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-lg border ${model.activo ? 'border-primary bg-primary/5' : 'border-border'}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-lg">{model.nombre}</h3>
                  {model.activo && (
                    <span className="badge-status badge-resolved flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Mejor
                    </span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  {model.nombre === 'XGBoost' ? 'Modelo de gradient boosting optimizado' :
                   model.nombre === 'Prophet' ? 'Modelo de series temporales de Meta' :
                   'Red neuronal recurrente'}
                </p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">MAE</p>
                    <p className="text-lg font-bold text-success">{model.mae}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">RMSE</p>
                    <p className="text-lg font-bold text-success">{model.rmse}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">R2 Score</p>
                    <p className="text-lg font-bold text-primary">{model.r2_score}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Tiempo</p>
                    <p className="text-lg font-bold">{model.tiempo_entrenamiento}</p>
                  </div>
                </div>
                {model.activo && (
                  <p className="text-xs text-success mt-3 flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Modelo activo en produccion
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* R2 Score Comparison */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Comparacion R2 Score</CardTitle>
            <p className="text-sm text-muted-foreground">Valores cercanos a 1.0 indican mejor ajuste</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={r2Data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis domain={[0.8, 1]} stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="r2" fill="hsl(var(--success))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Real vs Predicted */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Valores Reales vs Predicciones</CardTitle>
            <p className="text-sm text-muted-foreground">Modelo: {selectedModel}</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis type="number" dataKey="real" name="Real" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis type="number" dataKey="predicho" name="Predicho" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Scatter name="Predicciones" data={scatterData} fill="hsl(var(--primary))" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

        {/* Technical Details */}
      <Card className="chart-container" key={`technical-details-${selectedModel}`}>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              Detalles Tecnicos
              <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-1 rounded">
                {selectedModel}
              </span>
            </CardTitle>
            <p className="text-sm text-muted-foreground">Configuracion y caracteristicas del modelo seleccionado</p>
          </div>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-40">
              <SelectValue>{selectedModel}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="XGBoost">XGBoost</SelectItem>
              <SelectItem value="Prophet">Prophet</SelectItem>
              <SelectItem value="LSTM">LSTM</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Column - General Info & Hyperparameters */}
            <div className="space-y-6" key={`general-info-${selectedModel}`}>
              <div>
                <h4 className="font-medium mb-4 flex items-center gap-2">
                  Informacion General
                </h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="p-3 rounded-lg bg-secondary/50" key={`version-${selectedModel}`}>
                    <p className="text-muted-foreground mb-1">Version</p>
                    <p className="font-mono">{selectedModelData?.version || '-'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50" key={`framework-${selectedModel}`}>
                    <p className="text-muted-foreground mb-1">Framework</p>
                    <p className="font-mono">{selectedModelData?.framework || '-'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50" key={`fecha-${selectedModel}`}>
                    <p className="text-muted-foreground mb-1">Fecha entrenamiento</p>
                    <p className="font-mono">{selectedModelData?.fecha_entrenamiento || '-'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-secondary/50" key={`datos-${selectedModel}`}>
                    <p className="text-muted-foreground mb-1">Datos de entrenamiento</p>
                    <p className="font-mono">{selectedModelData?.datos_entrenamiento?.toLocaleString() || '-'} registros</p>
                  </div>
                </div>
              </div>

              <div key={`hiperparametros-${selectedModel}`}>
                <h4 className="font-medium mb-4 flex items-center gap-2">
                  Hiperparametros
                </h4>
                <div className="space-y-2">
                  {selectedModelData?.hiperparametros && Object.entries(selectedModelData.hiperparametros).map(([key, value]) => (
                    <div key={`${selectedModel}-${key}`} className="flex justify-between py-2 border-b border-border/50 text-sm">
                      <span className="font-mono text-muted-foreground">{key}</span>
                      <span className="font-mono font-medium">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column - Feature Importance */}
            <div key={`features-${selectedModel}`}>
              <h4 className="font-medium mb-4 flex items-center gap-2">
                Features Importantes
              </h4>
              <div className="space-y-3">
                {selectedModelData?.feature_importance && Object.entries(selectedModelData.feature_importance)
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .map(([feature, importance], index) => (
                    <div key={`${selectedModel}-${feature}`} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-mono">{feature}</span>
                        <span className="font-medium">{((importance as number) * 100).toFixed(0)}%</span>
                      </div>
                      <div className="h-2 bg-secondary rounded-full overflow-hidden">
                        <motion.div
                          key={`bar-${selectedModel}-${feature}`}
                          initial={{ width: 0 }}
                          animate={{ width: `${(importance as number) * 100}%` }}
                          transition={{ duration: 0.5, delay: index * 0.1 }}
                          className="h-full bg-primary rounded-full"
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Chatbot />
    </div>
  );
}
