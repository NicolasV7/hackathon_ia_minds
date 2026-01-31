import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Building2,
  Zap,
  Droplets,
  Cloud,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Activity,
  Gauge,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { getDashboardKPIs, getConsumptionTrends, getUnresolvedAnomalies, getSedesInfo, type DashboardKPIs, type ConsumptionTrend, type Anomaly, type SedeInfo } from '@/services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import Chatbot from '@/components/Chatbot';

  // Calculate trend percentage from trends data
const calculateTrend = (current: number, previous: number): number => {
  if (!previous || previous === 0) return 0;
  return Number(((current - previous) / previous * 100).toFixed(1));
};

// Stat cards configuration
const statCardsConfig = [
  { key: 'sedes_monitoreadas', label: 'Sedes Monitoreadas', icon: Building2, suffix: ' sedes', hasTrend: false },
  { key: 'promedio_energia', label: 'Promedio Consumo Energia', icon: Zap, suffix: ' kWh/mes', hasTrend: true },
  { key: 'promedio_agua', label: 'Promedio Consumo Agua', icon: Droplets, suffix: ' m3/mes', hasTrend: true },
  { key: 'alertas_activas', label: 'Alertas Activas', icon: AlertTriangle, suffix: ' alertas', hasTrend: false },
  { key: 'total_emisiones', label: 'Total Emisiones CO2', icon: Cloud, suffix: ' ton/mes', hasTrend: true },
  { key: 'huella_carbono', label: 'Huella de Carbono', icon: Cloud, suffix: ' kg CO2/estudiante', hasTrend: true },
  { key: 'score_sostenibilidad', label: 'Score Sostenibilidad', icon: Activity, suffix: '/100', hasTrend: false },
  { key: 'indice_eficiencia', label: 'Indice de Eficiencia', icon: Gauge, suffix: ' %', hasTrend: false },
];

export default function DashboardPage() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<ConsumptionTrend[]>([]);
  const [alerts, setAlerts] = useState<Anomaly[]>([]);
  const [sedes, setSedes] = useState<SedeInfo[]>([]);
  const [selectedSede, setSelectedSede] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [trendsData, setTrendsData] = useState<Record<string, number | null>>({
    promedio_energia: null,
    promedio_agua: null,
    total_emisiones: null,
    huella_carbono: null,
    score_sostenibilidad: null,
    indice_eficiencia: null,
    alertas_activas: null,
  });

  useEffect(() => {
    async function fetchData() {
      try {
        const [kpisData, trendsData, alertsData, sedesData] = await Promise.all([
          getDashboardKPIs(selectedSede === 'all' ? undefined : selectedSede),
          getConsumptionTrends(selectedSede === 'all' ? 'tunja' : selectedSede),
          getUnresolvedAnomalies(),
          getSedesInfo(),
        ]);
        setKpis(kpisData);
        setTrends(trendsData);
        setAlerts(alertsData);
        setSedes(sedesData);
        
        // Calculate trends from data
        if (trendsData && trendsData.length >= 2) {
          const last = trendsData[trendsData.length - 1];
          const prev = trendsData[trendsData.length - 2];
          
          setTrendsData({
            promedio_energia: calculateTrend(last.energia_real, prev.energia_real),
            promedio_agua: calculateTrend(last.agua_real, prev.agua_real),
            total_emisiones: calculateTrend(last.co2_real, prev.co2_real),
            huella_carbono: calculateTrend(last.co2_real, prev.co2_real),
            score_sostenibilidad: null,
            indice_eficiencia: null,
            alertas_activas: null,
          });
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Set mock data on error
        setKpis({
          sedes_monitoreadas: 4,
          promedio_energia: 21400,
          promedio_agua: 4200,
          huella_carbono: 3.98,
          score_sostenibilidad: 78,
          alertas_activas: 5,
          total_emisiones: 125.3,
          indice_eficiencia: 9.2,
        });
        setTrends([
          { fecha: 'Ene', energia_real: 28000, energia_predicha: 27500, agua_real: 5800, agua_predicha: 5600, co2_real: 42, co2_predicha: 41 },
          { fecha: 'Feb', energia_real: 30000, energia_predicha: 29800, agua_real: 6200, agua_predicha: 6000, co2_real: 45, co2_predicha: 44 },
          { fecha: 'Mar', energia_real: 32000, energia_predicha: 31500, agua_real: 6500, agua_predicha: 6300, co2_real: 48, co2_predicha: 47 },
          { fecha: 'Abr', energia_real: 35000, energia_predicha: 34000, agua_real: 7000, agua_predicha: 6800, co2_real: 52, co2_predicha: 51 },
          { fecha: 'May', energia_real: 38000, energia_predicha: 37500, agua_real: 7500, agua_predicha: 7300, co2_real: 57, co2_predicha: 56 },
          { fecha: 'Jun', energia_real: 42000, energia_predicha: 41000, agua_real: 8200, agua_predicha: 8000, co2_real: 63, co2_predicha: 62 },
          { fecha: 'Jul', energia_real: 45000, energia_predicha: 44500, agua_real: 8800, agua_predicha: 8600, co2_real: 68, co2_predicha: 67 },
          { fecha: 'Ago', energia_real: 48000, energia_predicha: 47000, agua_real: 9200, agua_predicha: 9000, co2_real: 72, co2_predicha: 71 },
          { fecha: 'Sep', energia_real: 50000, energia_predicha: 49500, agua_real: 9500, agua_predicha: 9300, co2_real: 75, co2_predicha: 74 },
        ]);
        setAlerts([
          { id: '1', sede: 'Tunja', sector: 'Comedores', fecha: '2025-01-30 08:30', tipo: 'anomalia', severidad: 'critica', estado: 'pendiente', descripcion: 'Consumo anomalo detectado: +45% respecto al baseline', valor_detectado: 4500, valor_esperado: 3100 },
          { id: '2', sede: 'Duitama', sector: 'Laboratorios', fecha: '2025-01-30 07:15', tipo: 'desbalance', severidad: 'alta', estado: 'revisada', descripcion: 'Desbalance en consumo entre horario laboral y nocturno', valor_detectado: 1200, valor_esperado: 800 },
          { id: '3', sede: 'Sogamoso', sector: 'Oficinas', fecha: '2025-01-29 14:20', tipo: 'anomalia', severidad: 'media', estado: 'pendiente', descripcion: 'Consumo elevado detectado en fin de semana', valor_detectado: 890, valor_esperado: 200 },
        ]);
        setSedes([
          { id: 'tunja', nombre: 'Tunja (Principal)', estudiantes: 18000, lat: 5.5353, lng: -73.3678, consumo_energia: 45000, consumo_agua: 9500, emisiones_co2: 68 },
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

  const getKpiValue = (key: string): string => {
    if (!kpis) return '-';
    const value = kpis[key as keyof DashboardKPIs];
    if (typeof value === 'number') {
      return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value.toString();
    }
    return String(value);
  };

  const getSeverityColor = (severidad: string) => {
    switch (severidad) {
      case 'critica': return 'badge-critical';
      case 'alta': return 'badge-pending';
      case 'media': return 'badge-in-progress';
      default: return 'badge-resolved';
    }
  };

  const getStatusColor = (estado: string) => {
    switch (estado) {
      case 'pendiente': return 'badge-pending';
      case 'revisada': return 'badge-in-progress';
      case 'resuelta': return 'badge-resolved';
      default: return '';
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Cargando dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard Ejecutivo</h1>
          <p className="text-muted-foreground">Vista general de KPIs y metricas principales del sistema de monitoreo energetico</p>
        </div>
        <Select value={selectedSede} onValueChange={setSelectedSede}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filtrar por Sede" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todas las sedes</SelectItem>
            {sedes.map((sede) => (
              <SelectItem key={sede.id} value={sede.id}>{sede.nombre}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCardsConfig.map((stat, index) => {
          const trendValue = trendsData[stat.key];
          const hasTrend = stat.hasTrend && trendValue !== null;
          
          return (
            <motion.div
              key={stat.key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="stat-card">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <stat.icon className="w-5 h-5 text-primary" />
                    {hasTrend && (
                      <div className={`flex items-center gap-1 text-xs ${trendValue > 0 ? 'text-destructive' : 'text-success'}`}>
                        {trendValue > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {Math.abs(trendValue)}%
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold">
                    {getKpiValue(stat.key)}
                    <span className="text-sm font-normal text-muted-foreground">{stat.suffix}</span>
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Consumption Evolution Chart */}
        <Card className="lg:col-span-2 chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Evolucion del Consumo Energetico</CardTitle>
            <p className="text-sm text-muted-foreground">Valores reales vs predicciones (Energia, Agua, CO2)</p>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="fecha" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="energia_real" name="Real" stroke="hsl(var(--chart-energy))" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="energia_predicha" name="Prediccion" stroke="hsl(var(--chart-prediction))" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Estado del Sistema</CardTitle>
            <p className="text-sm text-muted-foreground">Salud general de la red</p>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <div className="relative w-32 h-32 mb-4">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="hsl(var(--muted))"
                  strokeWidth="12"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="hsl(var(--success))"
                  strokeWidth="12"
                  strokeDasharray={`${(kpis?.score_sostenibilidad || 85) * 3.51} 351`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">{kpis?.score_sostenibilidad || 85}%</span>
                <span className="text-xs text-success">Excelente</span>
              </div>
            </div>
            <div className="w-full space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-success" />
                  <span>Sedes operando normalmente</span>
                </div>
                <span className="font-medium bg-success/20 text-success px-2 py-0.5 rounded">4</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-warning" />
                  <span>Sectores requieren monitoreo</span>
                </div>
                <span className="font-medium bg-warning/20 text-warning px-2 py-0.5 rounded">5</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-destructive" />
                  <span>Alertas en estado critico</span>
                </div>
                <span className="font-medium bg-destructive/20 text-destructive px-2 py-0.5 rounded">2</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts and Rankings */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Alerts */}
        <Card className="chart-container">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg">Alertas Recientes</CardTitle>
              <p className="text-sm text-muted-foreground">Monitoreo en tiempo real de anomalias</p>
            </div>
            <a href="/dashboard/alertas" className="text-sm text-primary hover:underline">Ver todas</a>
          </CardHeader>
          <CardContent className="space-y-3">
            {alerts.slice(0, 3).map((alert) => (
              <div key={alert.id} className="flex items-start gap-3 p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors">
                <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                  alert.severidad === 'critica' ? 'text-destructive' : 
                  alert.severidad === 'alta' ? 'text-warning' : 'text-info'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium">{alert.sede} - {alert.sector}</span>
                    <span className={`badge-status ${getStatusColor(alert.estado)}`}>
                      {alert.estado.charAt(0).toUpperCase() + alert.estado.slice(1)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground truncate">{alert.descripcion}</p>
                  <p className="text-xs text-muted-foreground mt-1">{alert.fecha}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Top 4 Sedes by Consumption */}
        <Card className="chart-container">
          <CardHeader>
            <CardTitle className="text-lg">Top 4 Sedes por Consumo</CardTitle>
            <p className="text-sm text-muted-foreground">Ranking de consumo energetico mensual</p>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="pb-3 font-medium">RANKING</th>
                    <th className="pb-3 font-medium">SEDE</th>
                    <th className="pb-3 font-medium">CONSUMO</th>
                    <th className="pb-3 font-medium">TENDENCIA</th>
                    <th className="pb-3 font-medium">ESTADO</th>
                  </tr>
                </thead>
                <tbody>
                  {sedes.sort((a, b) => b.consumo_energia - a.consumo_energia).map((sede, index) => (
                    <tr key={sede.id} className="border-b border-border/50">
                      <td className="py-3">
                        <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          index === 0 ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        }`}>
                          {index + 1}
                        </span>
                      </td>
                      <td className="py-3 font-medium">{sede.nombre.split(' ')[0]}</td>
                      <td className="py-3">{sede.consumo_energia.toLocaleString()} kWh</td>
                      <td className={`py-3 ${index === 0 ? 'text-destructive' : index === 3 ? 'text-success' : 'text-muted-foreground'}`}>
                        {index === 0 ? '+3%' : index === 1 ? '-2%' : index === 2 ? '0%' : '-5%'}
                      </td>
                      <td className="py-3">
                        <span className={`badge-status ${index === 0 ? 'badge-pending' : 'badge-resolved'}`}>
                          {index === 0 ? 'Alerta' : 'Normal'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Carbon Footprint Calculation Info */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle className="text-lg">Como se calcula la huella de carbono?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-4 rounded-lg bg-secondary/50">
              <h4 className="text-primary font-medium mb-2">1. Consumo Electrico</h4>
              <p className="text-sm text-muted-foreground">kWh x Factor de emision CO2 (0.5126 kg CO2/kWh para Colombia)</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary/50">
              <h4 className="text-info font-medium mb-2">2. Consumo de Agua</h4>
              <p className="text-sm text-muted-foreground">m3 x Factor tratamiento + Factor bombeo (0.376 kg CO2/m3)</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary/50">
              <h4 className="text-success font-medium mb-2">3. Per Capita</h4>
              <p className="text-sm text-muted-foreground">Total CO2 / Numero de estudiantes activos por sede</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Chatbot />
    </div>
  );
}
