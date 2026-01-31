import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingDown, TreeDeciduous, Droplets, Cloud, Lightbulb, Target, Scale } from 'lucide-react';
import { LoadingScreen } from '@/components/ui/loading-screen';
import { SedeSelector } from '@/components/ui/sede-selector';
import {
  getSavingsProjection,
  getSustainabilityContribution,
  getParetoAnalysis,
  getOptimizationOpportunities,
  getPendingRecommendations,
  getSedesInfo,
  generateAIRecommendations,
  getDashboardKPIs,
  type Recommendation,
  type SedeInfo,
} from '@/services/api';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart, Line, Cell,
} from 'recharts';
import Chatbot from '@/components/Chatbot';

export default function BalancesPage() {
  const [savings, setSavings] = useState<{ categoria: string; valor: number; tipo: 'ahorro' | 'total' }[]>([]);
  const [sustainability, setSustainability] = useState<{ arboles_salvados: number; agua_ahorrada: number; co2_reducido: number }>({ arboles_salvados: 0, agua_ahorrada: 0, co2_reducido: 0 });
  const [pareto, setPareto] = useState<{ causa: string; porcentaje: number; acumulado: number }[]>([]);
  const [opportunities, setOpportunities] = useState<{ area: string; potencial_ahorro: number; descripcion: string }[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [sedes, setSedes] = useState<SedeInfo[]>([]);
  const [selectedSede, setSelectedSede] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const sedeParam = selectedSede === 'all' ? undefined : selectedSede;
        const [savingsData, sustData, paretoData, oppData, recData, sedesData] = await Promise.all([
          getSavingsProjection(sedeParam),
          getSustainabilityContribution(sedeParam),
          getParetoAnalysis(sedeParam),
          getOptimizationOpportunities(sedeParam),
          getPendingRecommendations(sedeParam),
          getSedesInfo(),
        ]);
        setSavings(savingsData);
        setSustainability(sustData);
        setPareto(paretoData);
        setOpportunities(oppData);
        setRecommendations(recData);
        setSedes(sedesData);
      } catch (error) {
        console.error('Error fetching balances data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedSede]);

  // Waterfall chart data with running total
  const waterfallData = savings.map((item, index) => {
    const prevTotal = index === 0 ? 0 : savings.slice(0, index).reduce((sum, s) => sum + s.valor, 0);
    return {
      ...item,
      start: item.tipo === 'total' && index === 0 ? 0 : prevTotal,
      end: item.tipo === 'total' && index === 0 ? item.valor : prevTotal + item.valor,
    };
  });

  const getPriorityColor = (prioridad: string) => {
    switch (prioridad) {
      case 'alta': return 'badge-critical';
      case 'media': return 'badge-pending';
      default: return 'badge-resolved';
    }
  };

  // Generate AI recommendations based on current data
  const handleGenerateAIRecommendations = async () => {
    try {
      setAiLoading(true);
      const sedeData = sedes.find(s => s.id === selectedSede) || sedes[0];
      if (!sedeData) return;

      const aiResponse = await generateAIRecommendations(
        selectedSede === 'all' ? 'Todas' : sedeData.nombre,
        sedeData.consumo_energia,
        sedeData.consumo_agua,
        sedeData.emisiones_co2,
        5 // Default anomalies count
      );
      
      setRecommendations(aiResponse.recomendaciones);
    } catch (error) {
      console.error('Error generating AI recommendations:', error);
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <LoadingScreen 
          variant="balances"
          title="Cargando Balances"
          description="Calculando proyecciones de ahorro y sostenibilidad..."
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <Scale className="w-6 h-6 text-emerald-400" />
            Balances Energeticos
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Proyecciones de ahorro y contribucion a sostenibilidad</p>
        </div>
        <SedeSelector
          sedes={sedes}
          selectedSede={selectedSede}
          onSedeChange={setSelectedSede}
          showAllOption={true}
        />
      </div>

      {/* Opportunities and Areas */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Opportunities */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-primary" />
              Oportunidades Identificadas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {opportunities.map((opp, index) => (
                <motion.div
                  key={opp.area}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium mb-1">{opp.area}</h4>
                      <p className="text-sm text-muted-foreground">{opp.descripcion}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-success">{opp.potencial_ahorro.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">kWh/ano</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Areas de Mejora */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Areas de Mejora</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { area: 'Eficiencia HVAC', progreso: 65, meta: 80 },
                { area: 'Iluminacion LED', progreso: 78, meta: 90 },
                { area: 'Equipos Clase A', progreso: 45, meta: 70 },
                { area: 'Energia Solar', progreso: 20, meta: 50 },
              ].map((item) => (
                <div key={item.area} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{item.area}</span>
                    <span className="text-muted-foreground">{item.progreso}% / {item.meta}%</span>
                  </div>
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.progreso}%` }}
                      transition={{ duration: 0.5 }}
                      className="h-full bg-primary rounded-full"
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Savings Waterfall Chart */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-success" />
            Proyeccion de Ahorro (Waterfall)
          </CardTitle>
          <p className="text-sm text-muted-foreground">Reduccion proyectada por disminucion de consumo de agua, energia, CO2</p>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={waterfallData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="categoria" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => [`${Math.abs(value).toLocaleString()} kWh`, value < 0 ? 'Ahorro' : 'Valor']}
                />
                <Bar dataKey="valor" radius={[4, 4, 0, 0]}>
                  {waterfallData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.tipo === 'ahorro' ? 'hsl(var(--success))' : 'hsl(var(--primary))'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Sustainability and Pareto */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Sustainability Contribution */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TreeDeciduous className="w-5 h-5 text-success" />
              Contribucion a la Sostenibilidad
            </CardTitle>
            <p className="text-sm text-muted-foreground">Reduccion de huella de carbono</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center p-4 rounded-xl bg-success/10"
              >
                <TreeDeciduous className="w-8 h-8 text-success mx-auto mb-2" />
                <p className="text-2xl font-bold text-success">{sustainability.arboles_salvados}</p>
                <p className="text-xs text-muted-foreground">Arboles salvados</p>
              </motion.div>
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-center p-4 rounded-xl bg-info/10"
              >
                <Droplets className="w-8 h-8 text-info mx-auto mb-2" />
                <p className="text-2xl font-bold text-info">{sustainability.agua_ahorrada.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">m3 agua ahorrada</p>
              </motion.div>
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center p-4 rounded-xl bg-primary/10"
              >
                <Cloud className="w-8 h-8 text-primary mx-auto mb-2" />
                <p className="text-2xl font-bold text-primary">{sustainability.co2_reducido}</p>
                <p className="text-xs text-muted-foreground">ton CO2 reducido</p>
              </motion.div>
            </div>
          </CardContent>
        </Card>

        {/* Pareto Chart */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Analisis Pareto</CardTitle>
            <p className="text-sm text-muted-foreground">20% de causas que generan 80% del desperdicio</p>
          </CardHeader>
          <CardContent>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={pareto}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="causa" stroke="hsl(var(--muted-foreground))" fontSize={10} />
                  <YAxis yAxisId="left" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--muted-foreground))" fontSize={12} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar yAxisId="left" dataKey="porcentaje" fill="hsl(var(--chart-energy))" radius={[4, 4, 0, 0]} name="%" />
                  <Line yAxisId="right" type="monotone" dataKey="acumulado" stroke="hsl(var(--destructive))" strokeWidth={2} name="Acumulado" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* LLM Recommendations */}
      <Card className="chart-container">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-primary" />
                Recomendaciones Personalizadas (IA)
              </CardTitle>
              <p className="text-sm text-muted-foreground">Acciones generadas por el motor de recomendaciones LLM basadas en datos reales</p>
            </div>
            <Button 
              onClick={handleGenerateAIRecommendations} 
              disabled={aiLoading}
              className="flex items-center gap-2"
            >
              <Lightbulb className="w-4 h-4" />
              {aiLoading ? 'Generando...' : 'Generar con IA'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recommendations.length === 0 && !aiLoading && (
              <div className="text-center py-8 text-muted-foreground">
                <Lightbulb className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Haz clic en "Generar con IA" para obtener recomendaciones personalizadas</p>
                <p className="text-sm mt-2">OpenAI analizará los datos de consumo de {selectedSede === 'all' ? 'todas las sedes' : 'la sede seleccionada'}</p>
              </div>
            )}
            {recommendations.map((rec, index) => (
              <motion.div
                key={rec.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`badge-status ${getPriorityColor(rec.prioridad)}`}>
                      Prioridad {rec.prioridad}
                    </span>
                    <span className="text-xs text-muted-foreground">{rec.sede} - {rec.sector}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-success">Ahorro: {rec.ahorro_estimado} kWh/mes</p>
                  </div>
                </div>
                <p className="text-sm">{rec.descripcion}</p>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Chatbot />
    </div>
  );
}
