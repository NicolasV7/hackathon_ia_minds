import { useEffect, useState } from 'react';
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
  ArrowRight,
  RefreshCw,
  LayoutDashboard,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { getDashboardKPIs, getConsumptionTrends, getUnresolvedAnomalies, getSedesInfo, type DashboardKPIs, type ConsumptionTrend, type Anomaly, type SedeInfo } from '@/services/api';
import {
  ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Area,
} from 'recharts';
import Chatbot from '@/components/Chatbot';
import { LoadingScreen } from '@/components/ui/loading-screen';
import { SedeSelector } from '@/components/ui/sede-selector';

// Calculate trend percentage from trends data
const calculateTrend = (current: number, previous: number): number => {
  if (!previous || previous === 0) return 0;
  return Number(((current - previous) / previous * 100).toFixed(1));
};

// KPI card configuration with semantic grouping
const primaryKPIs = [
  { key: 'promedio_energia', label: 'Consumo Energia', icon: Zap, suffix: 'kWh', color: 'text-amber-400', hasTrend: true },
  { key: 'promedio_agua', label: 'Consumo Agua', icon: Droplets, suffix: 'm3', color: 'text-sky-400', hasTrend: true },
  { key: 'total_emisiones', label: 'Emisiones CO2', icon: Cloud, suffix: 'ton', color: 'text-emerald-400', hasTrend: true },
  { key: 'alertas_activas', label: 'Alertas Activas', icon: AlertTriangle, suffix: '', color: 'text-rose-400', hasTrend: false },
];

const secondaryKPIs = [
  { key: 'sedes_monitoreadas', label: 'Sedes', icon: Building2, suffix: '' },
  { key: 'huella_carbono', label: 'Huella Carbono', icon: Cloud, suffix: 'kg/est' },
  { key: 'score_sostenibilidad', label: 'Score', icon: Activity, suffix: '/100' },
  { key: 'indice_eficiencia', label: 'Eficiencia', icon: Gauge, suffix: '%' },
];

export default function DashboardPage() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<ConsumptionTrend[]>([]);
  const [alerts, setAlerts] = useState<Anomaly[]>([]);
  const [sedes, setSedes] = useState<SedeInfo[]>([]);
  const [selectedSede, setSelectedSede] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [trendsData, setTrendsData] = useState<Record<string, number | null>>({
    promedio_energia: null,
    promedio_agua: null,
    total_emisiones: null,
    huella_carbono: null,
  });

  const fetchData = async () => {
    setLoading(true);
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
      setLastUpdate(new Date());
      
      if (trendsData && trendsData.length >= 2) {
        const last = trendsData[trendsData.length - 1];
        const prev = trendsData[trendsData.length - 2];
        
        setTrendsData({
          promedio_energia: calculateTrend(last.energia_real, prev.energia_real),
          promedio_agua: calculateTrend(last.agua_real, prev.agua_real),
          total_emisiones: calculateTrend(last.co2_real, prev.co2_real),
          huella_carbono: calculateTrend(last.co2_real, prev.co2_real),
        });
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedSede]);

  const formatValue = (key: string): string => {
    if (!kpis) return '-';
    const value = kpis[key as keyof DashboardKPIs];
    if (typeof value === 'number') {
      if (value >= 10000) return `${(value / 1000).toFixed(1)}K`;
      if (value >= 1000) return value.toLocaleString();
      return value.toString();
    }
    return String(value);
  };

  const getStatusLabel = (score: number): { label: string; color: string } => {
    if (score >= 80) return { label: 'Excelente', color: 'text-emerald-400' };
    if (score >= 60) return { label: 'Bueno', color: 'text-amber-400' };
    return { label: 'Requiere atencion', color: 'text-rose-400' };
  };

  const getSeverityStyles = (severidad: string) => {
    switch (severidad) {
      case 'critica': return { bg: 'bg-rose-500/10', text: 'text-rose-400', border: 'border-rose-500/20' };
      case 'alta': return { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' };
      case 'media': return { bg: 'bg-sky-500/10', text: 'text-sky-400', border: 'border-sky-500/20' };
      default: return { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/20' };
    }
  };

  if (loading) {
    return (
      <main className="p-6" aria-busy="true" aria-label="Cargando dashboard">
        <LoadingScreen 
          variant="default"
          title="Cargando Dashboard"
          description="Obteniendo KPIs y metricas del sistema..."
        />
      </main>
    );
  }

  const systemStatus = getStatusLabel(kpis?.score_sostenibilidad || 0);

  return (
    <main className="p-6 space-y-8" role="main" aria-label="Dashboard ejecutivo">
      {/* Header */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
            <LayoutDashboard className="w-6 h-6 text-primary" />
            Dashboard Ejecutivo
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Ultima actualizacion: <time className="tabular-nums">{lastUpdate.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}</time>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchData}
            aria-label="Actualizar datos"
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Actualizar</span>
          </Button>
          <SedeSelector
            sedes={sedes}
            selectedSede={selectedSede}
            onSedeChange={setSelectedSede}
            showAllOption={true}
          />
        </div>
      </header>

      {/* Primary KPIs */}
      <section aria-labelledby="kpis-title">
        <h2 id="kpis-title" className="sr-only">Indicadores principales</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {primaryKPIs.map((kpi) => {
            const trendValue = trendsData[kpi.key];
            const hasTrend = kpi.hasTrend && trendValue !== null;
            const isNegativeTrend = trendValue && trendValue > 0;
            
            return (
              <Card key={kpi.key} className="relative overflow-hidden group hover:border-primary/30 transition-colors">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-2 rounded-lg bg-secondary ${kpi.color}`}>
                      <kpi.icon className="w-5 h-5" aria-hidden="true" />
                    </div>
                    {hasTrend && (
                      <div 
                        className={`flex items-center gap-1 text-xs font-medium tabular-nums ${isNegativeTrend ? 'text-rose-400' : 'text-emerald-400'}`}
                        aria-label={`Tendencia: ${isNegativeTrend ? 'aumento' : 'disminucion'} de ${Math.abs(trendValue)}%`}
                      >
                        {isNegativeTrend ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                        {Math.abs(trendValue)}%
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mb-1">{kpi.label}</p>
                  <p className="text-3xl font-semibold tracking-tight tabular-nums">
                    {formatValue(kpi.key)}
                    {kpi.suffix && <span className="text-base font-normal text-muted-foreground ml-1">{kpi.suffix}</span>}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Secondary KPIs - Compact row */}
      <section aria-labelledby="secondary-kpis" className="flex flex-wrap gap-3">
        <h2 id="secondary-kpis" className="sr-only">Indicadores secundarios</h2>
        {secondaryKPIs.map((kpi) => (
          <div 
            key={kpi.key}
            className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-secondary/50 border border-border/50"
          >
            <kpi.icon className="w-4 h-4 text-muted-foreground" aria-hidden="true" />
            <div className="flex items-baseline gap-2">
              <span className="text-sm text-muted-foreground">{kpi.label}</span>
              <span className="font-semibold tabular-nums">{formatValue(kpi.key)}{kpi.suffix}</span>
            </div>
          </div>
        ))}
      </section>

      {/* Charts Section */}
      <section className="grid lg:grid-cols-3 gap-6" aria-labelledby="charts-title">
        <h2 id="charts-title" className="sr-only">Graficos de consumo</h2>
        
        {/* Main Chart - Energy Consumption */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-medium">Consumo Energetico</CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">Real vs Prediccion - Ultimos 7 meses</p>
              </div>
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                  <span className="text-muted-foreground">Real</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-0.5 bg-purple-400" style={{ borderStyle: 'dashed' }} />
                  <span className="text-muted-foreground">Prediccion</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]" role="img" aria-label="Grafico de lineas mostrando consumo energetico real vs prediccion">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={trends}>
                  <defs>
                    <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(45, 100%, 51%)" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="hsl(45, 100%, 51%)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis 
                    dataKey="fecha" 
                    stroke="hsl(var(--muted-foreground))" 
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis 
                    stroke="hsl(var(--muted-foreground))" 
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(v) => `${(v/1000).toFixed(0)}K`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                    formatter={(value: number, name: string) => [
                      `${value.toLocaleString()} kWh`, 
                      name === 'energia_real' ? 'Real' : 'Prediccion'
                    ]}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="energia_real" 
                    stroke="hsl(45, 100%, 51%)" 
                    strokeWidth={2} 
                    fill="url(#energyGradient)"
                    name="energia_real"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="energia_predicha" 
                    stroke="hsl(280, 65%, 60%)" 
                    strokeWidth={2} 
                    strokeDasharray="5 5" 
                    dot={false}
                    name="energia_predicha"
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-medium">Estado del Sistema</CardTitle>
            <p className="text-xs text-muted-foreground">Salud general de la red</p>
          </CardHeader>
          <CardContent className="flex flex-col items-center pt-4">
            {/* Circular Progress */}
            <div className="relative w-36 h-36 mb-6" role="progressbar" aria-valuenow={kpis?.score_sostenibilidad || 0} aria-valuemin={0} aria-valuemax={100}>
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 128 128">
                <circle
                  cx="64"
                  cy="64"
                  r="54"
                  fill="none"
                  stroke="hsl(var(--muted))"
                  strokeWidth="10"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="54"
                  fill="none"
                  stroke="hsl(var(--success))"
                  strokeWidth="10"
                  strokeDasharray={`${(kpis?.score_sostenibilidad || 0) * 3.39} 339`}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-semibold tabular-nums">{kpis?.score_sostenibilidad || 0}</span>
                <span className={`text-xs font-medium ${systemStatus.color}`}>{systemStatus.label}</span>
              </div>
            </div>

            {/* Status List */}
            <ul className="w-full space-y-3 text-sm" aria-label="Estado de componentes">
              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" aria-hidden="true" />
                  <span>Sedes operativas</span>
                </div>
                <span className="font-medium tabular-nums bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded">4</span>
              </li>
              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-amber-400" aria-hidden="true" />
                  <span>Sectores monitoreados</span>
                </div>
                <span className="font-medium tabular-nums bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded">12</span>
              </li>
              <li className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-rose-400" aria-hidden="true" />
                  <span>Alertas criticas</span>
                </div>
                <span className="font-medium tabular-nums bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded">
                  {alerts.filter(a => a.severidad === 'critica').length}
                </span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </section>

      {/* Alerts and Rankings */}
      <section className="grid lg:grid-cols-2 gap-6" aria-labelledby="alerts-rankings">
        <h2 id="alerts-rankings" className="sr-only">Alertas y ranking de sedes</h2>

        {/* Alerts */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base font-medium">Alertas Recientes</CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">Anomalias detectadas por Isolation Forest</p>
              </div>
              <a 
                href="/dashboard/alertas" 
                className="text-xs text-primary hover:underline inline-flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
              >
                Ver todas <ArrowRight className="w-3 h-3" />
              </a>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3" aria-label="Lista de alertas recientes">
              {alerts.slice(0, 3).map((alert) => {
                const styles = getSeverityStyles(alert.severidad);
                return (
                  <li 
                    key={alert.id} 
                    className={`p-3 rounded-lg border ${styles.bg} ${styles.border} transition-colors hover:bg-secondary/80`}
                  >
                    <div className="flex items-start gap-3">
                      <AlertTriangle className={`w-4 h-4 mt-0.5 ${styles.text}`} aria-hidden="true" />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-sm">{alert.sede}</span>
                          <span className="text-muted-foreground">-</span>
                          <span className="text-sm text-muted-foreground">{alert.sector}</span>
                          <span className={`text-[10px] font-medium uppercase px-1.5 py-0.5 rounded ${styles.bg} ${styles.text}`}>
                            {alert.severidad}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-1">{alert.descripcion}</p>
                        <div className="flex items-center gap-3 mt-2 text-xs">
                          <span className="text-muted-foreground tabular-nums">{alert.fecha}</span>
                          <span className="text-rose-400 tabular-nums">{alert.valor_detectado.toLocaleString()} kWh</span>
                          <span className="text-muted-foreground">/</span>
                          <span className="text-emerald-400 tabular-nums">{alert.valor_esperado.toLocaleString()} kWh esperado</span>
                        </div>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>

        {/* Rankings */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-medium">Ranking de Sedes</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Ordenadas por consumo energetico mensual</p>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm" aria-label="Ranking de sedes por consumo">
                <thead>
                  <tr className="text-left text-xs text-muted-foreground border-b border-border">
                    <th className="pb-3 font-medium w-12">#</th>
                    <th className="pb-3 font-medium">Sede</th>
                    <th className="pb-3 font-medium text-right">Consumo</th>
                    <th className="pb-3 font-medium text-right">Tendencia</th>
                    <th className="pb-3 font-medium text-right">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {[...sedes].sort((a, b) => b.consumo_energia - a.consumo_energia).map((sede, index) => {
                    const trendValues = ['+3.2%', '-1.8%', '+0.5%', '-4.1%'];
                    const isHighConsumption = index === 0;
                    
                    return (
                      <tr key={sede.id} className="border-b border-border/50 hover:bg-secondary/30 transition-colors">
                        <td className="py-3">
                          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                            index === 0 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
                          }`}>
                            {index + 1}
                          </span>
                        </td>
                        <td className="py-3 font-medium">{sede.nombre.split(' ')[0]}</td>
                        <td className="py-3 text-right tabular-nums">{sede.consumo_energia.toLocaleString()} kWh</td>
                        <td className={`py-3 text-right tabular-nums ${trendValues[index].startsWith('+') ? 'text-rose-400' : 'text-emerald-400'}`}>
                          {trendValues[index]}
                        </td>
                        <td className="py-3 text-right">
                          <span className={`text-[10px] font-medium uppercase px-2 py-1 rounded ${
                            isHighConsumption 
                              ? 'bg-amber-500/10 text-amber-400' 
                              : 'bg-emerald-500/10 text-emerald-400'
                          }`}>
                            {isHighConsumption ? 'Alerta' : 'Normal'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Carbon Footprint Info */}
      <section aria-labelledby="carbon-info">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle id="carbon-info" className="text-base font-medium">Calculo de Huella de Carbono</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Metodologia de calculo segun estandares colombianos</p>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-3 gap-4">
              <article className="p-4 rounded-lg bg-secondary/50 border border-border/50">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="w-4 h-4 text-amber-400" aria-hidden="true" />
                  <h3 className="font-medium text-sm">Consumo Electrico</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  kWh x Factor de emision <span className="tabular-nums text-foreground">(0.5126 kg CO2/kWh)</span> segun UPME Colombia
                </p>
              </article>
              <article className="p-4 rounded-lg bg-secondary/50 border border-border/50">
                <div className="flex items-center gap-2 mb-2">
                  <Droplets className="w-4 h-4 text-sky-400" aria-hidden="true" />
                  <h3 className="font-medium text-sm">Consumo de Agua</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  m3 x Factor tratamiento + bombeo <span className="tabular-nums text-foreground">(0.376 kg CO2/m3)</span>
                </p>
              </article>
              <article className="p-4 rounded-lg bg-secondary/50 border border-border/50">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                  <h3 className="font-medium text-sm">Per Capita</h3>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Total CO2 / Estudiantes activos por sede
                </p>
              </article>
            </div>
          </CardContent>
        </Card>
      </section>

      <Chatbot />
    </main>
  );
}
