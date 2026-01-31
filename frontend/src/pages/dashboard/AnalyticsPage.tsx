import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  getSectorBreakdown,
  getHourlyPatterns,
  getCorrelationMatrix,
  getAcademicPeriodConsumption,
  getParetoAnalysis,
  getSustainabilityContribution,
  getOptimizationOpportunities,
  getSedesInfo,
  type SectorBreakdown,
  type HourlyPattern,
  type SedeInfo,
} from '@/services/api';
import {
  PieChart, Pie, Cell, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart, Line,
} from 'recharts';
import Chatbot from '@/components/Chatbot';
import { TreeDeciduous, Droplets, Lightbulb, BarChart3 } from 'lucide-react';
import { LoadingScreen } from '@/components/ui/loading-screen';
import { SedeSelector } from '@/components/ui/sede-selector';
import { SectorSelector } from '@/components/ui/sector-selector';

const COLORS = ['hsl(45, 100%, 51%)', 'hsl(199, 89%, 48%)', 'hsl(142, 76%, 36%)', 'hsl(280, 65%, 60%)', 'hsl(0, 84%, 60%)'];

export default function AnalyticsPage() {
  const [sedes, setSedes] = useState<SedeInfo[]>([]);
  const [selectedSede, setSelectedSede] = useState<string>('tunja');
  const [selectedSector, setSelectedSector] = useState<string>('all');
  const [sectorData, setSectorData] = useState<SectorBreakdown[]>([]);
  const [hourlyData, setHourlyData] = useState<HourlyPattern[]>([]);
  const [correlations, setCorrelations] = useState<{ variables: string[]; matrix: number[][] }>({ variables: [], matrix: [] });
  const [academicPeriods, setAcademicPeriods] = useState<{ periodo: string; energia: number }[]>([]);
  const [paretoData, setParetoData] = useState<{ causa: string; porcentaje: number; acumulado: number }[]>([]);
  const [sustainability, setSustainability] = useState<{ arboles_salvados: number; agua_ahorrada: number; co2_reducido: number }>({ arboles_salvados: 0, agua_ahorrada: 0, co2_reducido: 0 });
  const [opportunities, setOpportunities] = useState<{ area: string; potencial_ahorro: number; descripcion: string }[]>([]);
  const [loading, setLoading] = useState(true);



  useEffect(() => {
    async function fetchData() {
      try {
        const [sedesData, sectorRes, hourlyRes, corrRes, academicRes, paretoRes, sustRes, oppRes] = await Promise.all([
          getSedesInfo(),
          getSectorBreakdown(selectedSede),
          getHourlyPatterns(selectedSede),
          getCorrelationMatrix(selectedSede),
          getAcademicPeriodConsumption(),
          getParetoAnalysis(selectedSede),
          getSustainabilityContribution(selectedSede),
          getOptimizationOpportunities(selectedSede),
        ]);
        console.log('[Analytics] Sector data received:', sectorRes);
        setSedes(sedesData);
        setSectorData(sectorRes);
        setHourlyData(hourlyRes);
        setCorrelations(corrRes);
        setAcademicPeriods(academicRes);
        setParetoData(paretoRes);
        setSustainability(sustRes);
        setOpportunities(oppRes);
      } catch (error) {
        console.error('[Analytics] Error fetching data:', error);
        // Mock data fallback
        setSedes([
          { id: 'tunja', nombre: 'Tunja', estudiantes: 18000, lat: 5.5353, lng: -73.3678, consumo_energia: 45000, consumo_agua: 9500, emisiones_co2: 68 },
          { id: 'duitama', nombre: 'Duitama', estudiantes: 5500, lat: 5.8267, lng: -73.0333, consumo_energia: 18200, consumo_agua: 3800, emisiones_co2: 27 },
          { id: 'sogamoso', nombre: 'Sogamoso', estudiantes: 6000, lat: 5.7147, lng: -72.9314, consumo_energia: 15500, consumo_agua: 3200, emisiones_co2: 23 },
          { id: 'chiquinquira', nombre: 'Chiquinquira', estudiantes: 2000, lat: 5.6167, lng: -73.8167, consumo_energia: 6800, consumo_agua: 1400, emisiones_co2: 10 },
        ]);
        setSectorData([
          { sector: 'Laboratorios', energia: 35, agua: 40, co2: 38, porcentaje: 35 },
          { sector: 'Comedores', energia: 25, agua: 30, co2: 25, porcentaje: 25 },
          { sector: 'Salones', energia: 20, agua: 15, co2: 18, porcentaje: 20 },
          { sector: 'Oficinas', energia: 12, agua: 10, co2: 12, porcentaje: 12 },
          { sector: 'Auditorios', energia: 8, agua: 5, co2: 7, porcentaje: 8 },
        ]);
        setHourlyData([
          { hora: '06:00', energia: 35, agua: 20, co2: 30 },
          { hora: '08:00', energia: 65, agua: 45, co2: 55 },
          { hora: '10:00', energia: 85, agua: 60, co2: 75 },
          { hora: '12:00', energia: 100, agua: 80, co2: 90 },
          { hora: '14:00', energia: 95, agua: 75, co2: 85 },
          { hora: '16:00', energia: 80, agua: 55, co2: 70 },
          { hora: '18:00', energia: 60, agua: 40, co2: 50 },
          { hora: '20:00', energia: 45, agua: 30, co2: 40 },
          { hora: '22:00', energia: 30, agua: 20, co2: 25 },
        ]);
        setCorrelations({
          variables: ['Energia', 'Agua', 'CO2', 'Temperatura'],
          matrix: [
            [1.0, 0.82, 0.95, -0.45],
            [0.82, 1.0, 0.78, -0.32],
            [0.95, 0.78, 1.0, -0.41],
            [-0.45, -0.32, -0.41, 1.0],
          ],
        });
        setAcademicPeriods([
          { periodo: 'Semestre 1 2024', energia: 55000 },
          { periodo: 'Vacaciones Jun', energia: 28000 },
          { periodo: 'Semestre 2 2024', energia: 52000 },
          { periodo: 'Vacaciones Dic', energia: 25000 },
          { periodo: 'Semestre 1 2025', energia: 48000 },
        ]);
        setParetoData([
          { causa: 'Climatizacion 24/7', porcentaje: 35, acumulado: 35 },
          { causa: 'Iluminacion sin uso', porcentaje: 25, acumulado: 60 },
          { causa: 'Equipos standby', porcentaje: 18, acumulado: 78 },
          { causa: 'Fugas de agua', porcentaje: 12, acumulado: 90 },
          { causa: 'Otros', porcentaje: 10, acumulado: 100 },
        ]);
        setSustainability({ arboles_salvados: 847, agua_ahorrada: 12500, co2_reducido: 125.3 });
        setOpportunities([
          { area: 'Climatizacion inteligente', potencial_ahorro: 15200, descripcion: 'Optimizar sistemas HVAC con sensores de ocupacion' },
          { area: 'Sensores de presencia', potencial_ahorro: 8500, descripcion: 'Iluminacion automatica en aulas y pasillos' },
        ]);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedSede]);

  const pieData = sectorData.map(s => ({ name: s.sector, value: s.porcentaje }));

  if (loading) {
    return (
      <div className="p-6">
        <LoadingScreen 
          variant="analytics"
          title="Cargando Analytics"
          description="Procesando datos de consumo y correlaciones..."
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
            <BarChart3 className="w-6 h-6 text-sky-400" />
            Analytics
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Analisis detallado de consumo, correlaciones y oportunidades</p>
        </div>
        <div className="flex gap-3">
          <SedeSelector
            sedes={sedes}
            selectedSede={selectedSede}
            onSedeChange={setSelectedSede}
            showAllOption={false}
          />
          <SectorSelector
            selectedSector={selectedSector}
            onSectorChange={setSelectedSector}
          />
        </div>
      </div>

      {/* Row 1: Distribution and Hourly Patterns */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Sector Distribution */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Distribucion por Sector</CardTitle>
            <p className="text-sm text-muted-foreground">Consumo energetico por tipo de espacio en {selectedSede}</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Hourly Patterns */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Patrones Horarios</CardTitle>
            <p className="text-sm text-muted-foreground">Distribucion del consumo a lo largo del dia</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="hora" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="energia" fill="hsl(var(--chart-energy))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Correlations and Academic Periods */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Correlation Matrix */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Correlacion entre Variables</CardTitle>
            <p className="text-sm text-muted-foreground">Relacion entre Energia, Agua y CO2</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { pair: 'Energia vs Agua', value: 0.82, color: 'bg-success' },
                { pair: 'Energia vs CO2', value: 0.95, color: 'bg-success' },
                { pair: 'Agua vs CO2', value: 0.78, color: 'bg-success' },
                { pair: 'Temperatura vs Consumo', value: -0.45, color: 'bg-destructive' },
              ].map((corr) => (
                <div key={corr.pair} className="flex items-center gap-4">
                  <span className="text-sm w-40">{corr.pair}</span>
                  <div className="flex-1 h-4 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.abs(corr.value) * 100}%` }}
                      transition={{ duration: 0.5 }}
                      className={`h-full ${corr.color} rounded-full`}
                    />
                  </div>
                  <span className={`text-sm font-mono ${corr.value < 0 ? 'text-destructive' : 'text-success'}`}>
                    {corr.value > 0 ? '+' : ''}{corr.value.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Academic Period Consumption */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Consumo por Periodo Academico</CardTitle>
            <p className="text-sm text-muted-foreground">Comparativo entre semestres y vacaciones</p>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={academicPeriods} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis dataKey="periodo" type="category" stroke="hsl(var(--muted-foreground))" fontSize={11} width={100} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="energia" fill="hsl(var(--chart-energy))" radius={[0, 4, 4, 0]} name="Energia (kWh)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Pareto Analysis */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-primary" />
            Analisis Pareto - Causas de Desperdicio
          </CardTitle>
          <p className="text-sm text-muted-foreground">20% de las causas generan 80% del desperdicio energetico</p>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={paretoData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="causa" stroke="hsl(var(--muted-foreground))" fontSize={11} />
                <YAxis yAxisId="left" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--muted-foreground))" fontSize={12} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Bar yAxisId="left" dataKey="porcentaje" fill="hsl(var(--chart-energy))" radius={[4, 4, 0, 0]} name="Desperdicio (%)" />
                <Line yAxisId="right" type="monotone" dataKey="acumulado" stroke="hsl(var(--destructive))" strokeWidth={2} name="Acumulado (%)" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Row 4: Sustainability and Opportunities */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Sustainability Contribution */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TreeDeciduous className="w-5 h-5 text-success" />
              Contribucion a Sostenibilidad
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-6">
              <motion.div
                initial={{ scale: 0.98, opacity: 0.8 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.15 }}
                className="text-center p-6 rounded-xl bg-success/10"
              >
                <TreeDeciduous className="w-12 h-12 text-success mx-auto mb-3" />
                <p className="text-4xl font-bold text-success">{sustainability.arboles_salvados}</p>
                <p className="text-sm text-muted-foreground">Arboles salvados</p>
              </motion.div>
              <motion.div
                initial={{ scale: 0.98, opacity: 0.8 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.05, duration: 0.15 }}
                className="text-center p-6 rounded-xl bg-info/10"
              >
                <Droplets className="w-12 h-12 text-info mx-auto mb-3" />
                <p className="text-4xl font-bold text-info">{sustainability.agua_ahorrada.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">m3 agua ahorrada</p>
              </motion.div>
            </div>
          </CardContent>
        </Card>

        {/* Optimization Opportunities */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-primary" />
              Oportunidades de Optimizacion
            </CardTitle>
            <p className="text-sm text-muted-foreground">Areas de mejora identificadas por el modelo</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {opportunities.map((opp, index) => (
                <motion.div
                  key={opp.area}
                  initial={{ x: -10, opacity: 0.8 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.05, duration: 0.15 }}
                  className="p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-medium">{opp.area}</h4>
                    <span className="text-sm text-primary font-medium">
                      Ahorro potencial: {opp.potencial_ahorro.toLocaleString()} kWh/ano
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{opp.descripcion}</p>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Chatbot />
    </div>
  );
}
