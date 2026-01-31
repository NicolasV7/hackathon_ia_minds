import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { TrendingDown, TrendingUp, ArrowRight, TreeDeciduous, Droplets, Cloud, Lightbulb, Target } from 'lucide-react';
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
        // Mock data
        setSavings([
          { categoria: 'Consumo actual', valor: 100000, tipo: 'total' },
          { categoria: 'Reduccion energia', valor: -15000, tipo: 'ahorro' },
          { categoria: 'Reduccion agua', valor: -8000, tipo: 'ahorro' },
          { categoria: 'Reduccion CO2', valor: -12000, tipo: 'ahorro' },
          { categoria: 'Eficiencia operativa', valor: -5000, tipo: 'ahorro' },
          { categoria: 'Consumo proyectado', valor: 60000, tipo: 'total' },
        ]);
        setSustainability({ arboles_salvados: 847, agua_ahorrada: 12500, co2_reducido: 125.3 });
        setPareto([
          { causa: 'Climatizacion 24/7', porcentaje: 35, acumulado: 35 },
          { causa: 'Iluminacion sin uso', porcentaje: 25, acumulado: 60 },
          { causa: 'Equipos standby', porcentaje: 18, acumulado: 78 },
          { causa: 'Fugas de agua', porcentaje: 12, acumulado: 90 },
          { causa: 'Otros', porcentaje: 10, acumulado: 100 },
        ]);
        setOpportunities([
          { area: 'Climatizacion inteligente', potencial_ahorro: 15200, descripcion: 'Optimizar sistemas HVAC con sensores de ocupacion' },
          { area: 'Sensores de presencia', potencial_ahorro: 8500, descripcion: 'Iluminacion automatica en aulas y pasillos' },
          { area: 'Equipos eficientes', potencial_ahorro: 12300, descripcion: 'Reemplazo de equipos de laboratorio obsoletos' },
          { area: 'Paneles solares', potencial_ahorro: 22000, descripcion: 'Instalacion de energia solar en techos' },
        ]);
        setRecommendations([
          { id: '1', sede: 'Tunja', sector: 'Comedores', tipo: 'eficiencia', descripcion: 'Verificar termostatos de refrigeradores. Consumo nocturno 45% superior al esperado.', ahorro_estimado: 120, prioridad: 'alta', estado: 'pendiente' },
          { id: '2', sede: 'Duitama', sector: 'Laboratorios', tipo: 'mantenimiento', descripcion: 'Revisar sistema de ventilacion. Desbalance detectado entre entrada y salida.', ahorro_estimado: 85, prioridad: 'media', estado: 'pendiente' },
          { id: '3', sede: 'Sogamoso', sector: 'Oficinas', tipo: 'comportamiento', descripcion: 'Implementar politica de apagado de equipos en fin de semana.', ahorro_estimado: 200, prioridad: 'alta', estado: 'pendiente' },
        ]);
        setSedes([
          { id: 'tunja', nombre: 'Tunja', estudiantes: 18000, lat: 5.5353, lng: -73.3678, consumo_energia: 45000, consumo_agua: 9500, emisiones_co2: 68 },
          { id: 'duitama', nombre: 'Duitama', estudiantes: 5500, lat: 5.8267, lng: -73.0333, consumo_energia: 18200, consumo_agua: 3800, emisiones_co2: 27 },
          { id: 'sogamoso', nombre: 'Sogamoso', estudiantes: 6000, lat: 5.7147, lng: -72.9314, consumo_energia: 15500, consumo_agua: 3200, emisiones_co2: 23 },
          { id: 'chiquinquira', nombre: 'Chiquinquira', estudiantes: 2000, lat: 5.6167, lng: -73.8167, consumo_energia: 6800, consumo_agua: 1400, emisiones_co2: 10 },
        ]);
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
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Cargando balances...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Target className="w-6 h-6 text-primary" />
            Balances Energeticos
          </h1>
          <p className="text-muted-foreground">Comparativo entrada/salida, perdidas y evolucion del ahorro por sede</p>
        </div>
        <div className="flex gap-3">
          <Select value={selectedSede} onValueChange={setSelectedSede}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Seleccionar Sede" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las sedes</SelectItem>
              {sedes.map((sede) => (
                <SelectItem key={sede.id} value={sede.id}>{sede.nombre}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
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
