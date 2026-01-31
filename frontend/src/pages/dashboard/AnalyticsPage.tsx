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



  // Fetch data when sede or sector changes
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      console.log(`[Analytics] Fetching data for sede: ${selectedSede}, sector: ${selectedSector}`);
      try {
        const [sedesData, sectorRes, hourlyRes, corrRes, academicRes, paretoRes, sustRes, oppRes] = await Promise.all([
          getSedesInfo(),
          getSectorBreakdown(selectedSede),
          getHourlyPatterns(selectedSede, selectedSector),
          getCorrelationMatrix(selectedSede),
          getAcademicPeriodConsumption(),
          getParetoAnalysis(selectedSede),
          getSustainabilityContribution(selectedSede),
          getOptimizationOpportunities(selectedSede),
        ]);
        console.log('[Analytics] Data received:', {
          sede: selectedSede,
          sector: selectedSector,
          sectorData: sectorRes,
          hourlyData: hourlyRes
        });
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
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedSede, selectedSector]);

  const pieData = sectorData.map(s => ({ name: s.sector, value: s.porcentaje }));
  
  // Debug: mostrar datos actuales
  console.log('[Analytics] Rendering with data:', {
    selectedSede,
    selectedSector,
    sectorDataCount: sectorData.length,
    hourlyDataCount: hourlyData.length,
    pieData
  });

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
            <CardTitle className="text-lg flex items-center gap-2">
              Distribucion por Sector
              <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-1 rounded">
                {selectedSede.toUpperCase()}
              </span>
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Consumo energetico por tipo de espacio
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]" key={`pie-${selectedSede}-${JSON.stringify(pieData)}`}>
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
                    {pieData.map((entry, index) => (
                      <Cell 
                        key={`cell-${selectedSede}-${index}-${entry.value}`} 
                        fill={COLORS[index % COLORS.length]} 
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number, name: string) => [`${value}%`, name]}
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
            <CardTitle className="text-lg flex items-center gap-2">
              Patrones Horarios
              <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-1 rounded">
                {selectedSede.toUpperCase()}
              </span>
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {selectedSector === 'all' 
                ? 'Distribucion del consumo a lo largo del dia - Todos los sectores'
                : `Distribucion del consumo - Sector: ${selectedSector.charAt(0).toUpperCase() + selectedSector.slice(1)}`
              }
            </p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]" key={`bar-${selectedSede}-${selectedSector}-${hourlyData.length}`}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="hora" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    formatter={(value: number) => [`${value} kWh`, 'Consumo']}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar 
                    dataKey="energia" 
                    fill="hsl(var(--chart-energy))" 
                    radius={[4, 4, 0, 0]}
                    key={`bar-data-${selectedSede}`}
                  />
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
            <CardTitle className="text-lg flex items-center gap-2">
              Correlacion entre Variables
              <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-1 rounded">
                {selectedSede.toUpperCase()}
              </span>
            </CardTitle>
            <p className="text-sm text-muted-foreground">Relacion entre Energia, Agua y CO2</p>
          </CardHeader>
          <CardContent key={`corr-${selectedSede}-${correlations.variables.join('-')}`}>
            <div className="space-y-3">
              {correlations.variables.length > 0 ? (
                correlations.variables.slice(0, 4).map((var1, i) => {
                  const var2 = correlations.variables[i + 1] || correlations.variables[0];
                  const value = correlations.matrix[i]?.[i + 1] || 0;
                  const pairName = `${var1} vs ${var2}`;
                  return (
                    <div key={`${selectedSede}-${pairName}`} className="flex items-center gap-4">
                      <span className="text-sm w-40">{pairName}</span>
                      <div className="flex-1 h-4 bg-secondary rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.abs(value) * 100}%` }}
                          transition={{ duration: 0.5 }}
                          className={`h-full ${value >= 0 ? 'bg-success' : 'bg-destructive'} rounded-full`}
                        />
                      </div>
                      <span className={`text-sm font-mono ${value < 0 ? 'text-destructive' : 'text-success'}`}>
                        {value > 0 ? '+' : ''}{value.toFixed(2)}
                      </span>
                    </div>
                  );
                })
              ) : (
                <p className="text-sm text-muted-foreground">No hay datos de correlacion disponibles</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Academic Period Consumption */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              Consumo por Periodo Academico
              <span className="text-xs font-normal text-muted-foreground bg-secondary px-2 py-1 rounded">
                {selectedSede.toUpperCase()}
              </span>
            </CardTitle>
            <p className="text-sm text-muted-foreground">Comparativo entre semestres y vacaciones</p>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]" key={`academic-${selectedSede}-${academicPeriods.length}`}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={academicPeriods} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis dataKey="periodo" type="category" stroke="hsl(var(--muted-foreground))" fontSize={11} width={100} />
                  <Tooltip
                    formatter={(value: number) => [`${value.toLocaleString()} kWh`, 'Consumo']}
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar 
                    dataKey="energia" 
                    fill="hsl(var(--chart-energy))" 
                    radius={[0, 4, 4, 0]} 
                    name="Energia (kWh)"
                    key={`academic-bar-${selectedSede}`}
                  />
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
