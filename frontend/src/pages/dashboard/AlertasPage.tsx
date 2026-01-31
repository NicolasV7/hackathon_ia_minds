import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { AlertTriangle, Clock, CheckCircle, Eye, Filter } from 'lucide-react';
import {
  getUnresolvedAnomalies,
  getAlertEvolution,
  getShapValues,
  getModelConfidence,
  getSedesInfo,
  updateAnomalyStatus,
  type Anomaly,
  type SedeInfo,
} from '@/services/api';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar,
} from 'recharts';
import Chatbot from '@/components/Chatbot';

export default function AlertasPage() {
  const [alerts, setAlerts] = useState<Anomaly[]>([]);
  const [sedes, setSedes] = useState<SedeInfo[]>([]);
  const [evolution, setEvolution] = useState<{ mes: string; anomalias: number; desbalances: number; criticas: number }[]>([]);
  const [shapValues, setShapValues] = useState<{ feature: string; value: number }[]>([]);
  const [confidence, setConfidence] = useState<{ confianza_prediccion: number; certeza_recomendacion: number; modelo_activo: string }>({ confianza_prediccion: 0, certeza_recomendacion: 0, modelo_activo: '' });
  const [selectedSede, setSelectedSede] = useState<string>('all');
  const [selectedEstado, setSelectedEstado] = useState<string>('all');
  const [selectedSeveridad, setSelectedSeveridad] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [alertsData, sedesData, evolutionData, shapData, confData] = await Promise.all([
          getUnresolvedAnomalies(),
          getSedesInfo(),
          getAlertEvolution(),
          getShapValues('energia'),
          getModelConfidence(),
        ]);
        setAlerts(alertsData);
        setSedes(sedesData);
        setEvolution(evolutionData);
        setShapValues(shapData);
        setConfidence(confData);
      } catch (error) {
        console.error('Error fetching alerts data:', error);
        // Mock data
        setAlerts([
          { id: 'ALT-001', sede: 'Tunja', sector: 'Comedores', fecha: '2025-01-30 03:45', tipo: 'anomalia', severidad: 'critica', estado: 'pendiente', descripcion: 'Consumo 45% superior al baseline detectado fuera de horario (2-5am)', valor_detectado: 4500, valor_esperado: 3100 },
          { id: 'ALT-002', sede: 'Duitama', sector: 'Laboratorios', fecha: '2025-01-30 10:20', tipo: 'desbalance', severidad: 'alta', estado: 'revisada', descripcion: 'Diferencia significativa entre entrada y salida de energia', valor_detectado: 1200, valor_esperado: 800 },
          { id: 'ALT-003', sede: 'Sogamoso', sector: 'Oficinas', fecha: '2025-01-29 14:30', tipo: 'anomalia', severidad: 'media', estado: 'pendiente', descripcion: 'Pico de consumo en fin de semana cuando deberia estar cerrado', valor_detectado: 890, valor_esperado: 200 },
        ]);
        setSedes([
          { id: 'tunja', nombre: 'Tunja', estudiantes: 18000, lat: 5.5353, lng: -73.3678, consumo_energia: 45000, consumo_agua: 9500, emisiones_co2: 68 },
          { id: 'duitama', nombre: 'Duitama', estudiantes: 5500, lat: 5.8267, lng: -73.0333, consumo_energia: 18200, consumo_agua: 3800, emisiones_co2: 27 },
          { id: 'sogamoso', nombre: 'Sogamoso', estudiantes: 6000, lat: 5.7147, lng: -72.9314, consumo_energia: 15500, consumo_agua: 3200, emisiones_co2: 23 },
          { id: 'chiquinquira', nombre: 'Chiquinquira', estudiantes: 2000, lat: 5.6167, lng: -73.8167, consumo_energia: 6800, consumo_agua: 1400, emisiones_co2: 10 },
        ]);
        setEvolution([
          { mes: 'Ene', anomalias: 8, desbalances: 4, criticas: 2 },
          { mes: 'Feb', anomalias: 10, desbalances: 5, criticas: 3 },
          { mes: 'Mar', anomalias: 12, desbalances: 6, criticas: 2 },
          { mes: 'Abr', anomalias: 15, desbalances: 8, criticas: 4 },
          { mes: 'May', anomalias: 11, desbalances: 5, criticas: 2 },
          { mes: 'Jun', anomalias: 9, desbalances: 4, criticas: 1 },
          { mes: 'Jul', anomalias: 13, desbalances: 6, criticas: 3 },
        ]);
        setShapValues([
          { feature: 'hora_del_dia', value: 18 },
          { feature: 'dia_semana', value: 15 },
          { feature: 'temperatura', value: 12 },
          { feature: 'ocupacion', value: 8 },
          { feature: 'historico', value: -5 },
          { feature: 'estacionalidad', value: -8 },
        ]);
        setConfidence({ confianza_prediccion: 94.2, certeza_recomendacion: 87.5, modelo_activo: 'XGBoost v2.0' });
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const filteredAlerts = alerts.filter(a => {
    if (selectedSede !== 'all' && a.sede.toLowerCase() !== selectedSede) return false;
    if (selectedEstado !== 'all' && a.estado !== selectedEstado) return false;
    if (selectedSeveridad !== 'all' && a.severidad !== selectedSeveridad) return false;
    return true;
  });

  const alertsByEstado = {
    pendientes: alerts.filter(a => a.estado === 'pendiente').length,
    revisadas: alerts.filter(a => a.estado === 'revisada').length,
    resueltas: alerts.filter(a => a.estado === 'resuelta').length,
    total: alerts.length,
  };

  const alertsBySeveridad = {
    criticas: alerts.filter(a => a.severidad === 'critica').length,
    altas: alerts.filter(a => a.severidad === 'alta').length,
    medias: alerts.filter(a => a.severidad === 'media').length,
    bajas: alerts.filter(a => a.severidad === 'baja').length,
  };

  const getSeverityIcon = (severidad: string) => {
    switch (severidad) {
      case 'critica': return <AlertTriangle className="w-4 h-4 text-destructive" />;
      case 'alta': return <AlertTriangle className="w-4 h-4 text-warning" />;
      case 'media': return <Clock className="w-4 h-4 text-info" />;
      default: return <CheckCircle className="w-4 h-4 text-success" />;
    }
  };

  const getSeverityBadge = (severidad: string) => {
    switch (severidad) {
      case 'critica': return 'badge-critical';
      case 'alta': return 'badge-pending';
      case 'media': return 'badge-in-progress';
      default: return 'badge-resolved';
    }
  };

  const getStatusBadge = (estado: string) => {
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
        <div className="text-muted-foreground">Cargando alertas...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-warning" />
            Gestion de Alertas
          </h1>
          <p className="text-muted-foreground">Deteccion de anomalias con Isolation Forest y explicabilidad de predicciones</p>
        </div>
      </div>

      {/* Alert Banner */}
      <div className="p-4 rounded-lg bg-warning/10 border border-warning/30 flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 text-warning" />
        <p className="text-sm">
          <span className="font-medium text-warning">Alertas criticas</span>{' '}
          <span className="text-muted-foreground">se notifican automaticamente por Telegram al equipo de mantenimiento</span>
        </p>
      </div>

      {/* Summary Cards */}
      <div className="space-y-4">
        <h3 className="font-medium">Resumen de Alertas</h3>
        
        {/* By Estado */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground mb-1">Por Estado</p>
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-warning" />
                <span className="text-muted-foreground text-xs">Pendientes</span>
              </div>
              <p className="text-3xl font-bold text-warning">{alertsByEstado.pendientes}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Eye className="w-4 h-4 text-info" />
                <span className="text-muted-foreground text-xs">Revisadas</span>
              </div>
              <p className="text-3xl font-bold text-info">{alertsByEstado.revisadas}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-success" />
                <span className="text-muted-foreground text-xs">Resueltas</span>
              </div>
              <p className="text-3xl font-bold text-success">{alertsByEstado.resueltas}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Filter className="w-4 h-4 text-primary" />
                <span className="text-muted-foreground text-xs">Total</span>
              </div>
              <p className="text-3xl font-bold text-primary">{alertsByEstado.total}</p>
            </CardContent>
          </Card>
        </div>

        {/* By Severidad */}
        <p className="text-xs text-muted-foreground">Por Severidad</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-destructive" />
                <span className="text-muted-foreground text-xs">Criticas</span>
              </div>
              <p className="text-3xl font-bold text-destructive">{alertsBySeveridad.criticas}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-warning" />
                <span className="text-muted-foreground text-xs">Altas</span>
              </div>
              <p className="text-3xl font-bold text-warning">{alertsBySeveridad.altas}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-info" />
                <span className="text-muted-foreground text-xs">Medias</span>
              </div>
              <p className="text-3xl font-bold text-info">{alertsBySeveridad.medias}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-success" />
                <span className="text-muted-foreground text-xs">Bajas</span>
              </div>
              <p className="text-3xl font-bold text-success">{alertsBySeveridad.bajas}</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Evolution Chart */}
      <Card className="chart-container">
        <CardHeader>
          <CardTitle className="text-lg">Evolucion de Alertas</CardTitle>
          <p className="text-sm text-muted-foreground">Cantidad de alertas generadas por tipo y mes</p>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={evolution}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="mes" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="anomalias" name="Anomalias" stroke="hsl(var(--chart-energy))" strokeWidth={2} />
                <Line type="monotone" dataKey="desbalances" name="Desbalances" stroke="hsl(var(--chart-water))" strokeWidth={2} />
                <Line type="monotone" dataKey="criticas" name="Criticas" stroke="hsl(var(--destructive))" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Anomaly Detection and Explainability */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Detected Anomalies */}
        <Card className="chart-container">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg">Deteccion de Anomalias</CardTitle>
              <p className="text-sm text-muted-foreground">Alertas predichas por Isolation Forest</p>
            </div>
            <div className="flex gap-2">
              <Select value={selectedSede} onValueChange={setSelectedSede}>
                <SelectTrigger className="w-28">
                  <SelectValue placeholder="Sede" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  {sedes.map((s) => (
                    <SelectItem key={s.id} value={s.id}>{s.nombre.split(' ')[0]}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={selectedEstado} onValueChange={setSelectedEstado}>
                <SelectTrigger className="w-28">
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="pendiente">Pendiente</SelectItem>
                  <SelectItem value="revisada">Revisada</SelectItem>
                  <SelectItem value="resuelta">Resuelta</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-[400px] overflow-y-auto">
              {filteredAlerts.map((alert) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0.8, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.15 }}
                  className="p-4 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(alert.severidad)}
                      <span className={`badge-status ${getSeverityBadge(alert.severidad)}`}>
                        {alert.severidad}
                      </span>
                      <span className={`badge-status ${getStatusBadge(alert.estado)}`}>
                        {alert.tipo === 'anomalia' ? 'Predictiva' : 'Desbalance'}
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground font-mono">{alert.id}</span>
                  </div>
                  <p className="text-sm font-medium mb-1">{alert.descripcion}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span>{alert.sede} - {alert.sector}</span>
                    <span>{alert.fecha}</span>
                  </div>
                  <div className="mt-2 text-xs">
                    <span className="text-destructive">Detectado: {alert.valor_detectado} kWh</span>
                    {' '}
                    <span className="text-success">Esperado: {alert.valor_esperado} kWh</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Explainability */}
        <div className="space-y-6">
          {/* Waterfall SHAP */}
          <Card className="chart-container">
            <CardHeader>
              <CardTitle className="text-lg">Explicabilidad - Waterfall Plot</CardTitle>
              <p className="text-sm text-muted-foreground">Contribucion de cada feature a la prediccion de anomalia</p>
            </CardHeader>
            <CardContent>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapValues} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <YAxis dataKey="feature" type="category" stroke="hsl(var(--muted-foreground))" fontSize={11} width={100} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar 
                      dataKey="value" 
                      fill="hsl(var(--success))"
                      radius={[0, 4, 4, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Confidence Panel */}
          <Card className="chart-container">
            <CardHeader>
              <CardTitle className="text-lg">Intervalo de Confianza</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center p-4 rounded-lg bg-success/10">
                  <p className="text-xs text-muted-foreground mb-1">Confianza prediccion</p>
                  <p className="text-3xl font-bold text-success">{confidence.confianza_prediccion}%</p>
                </div>
                <div className="text-center p-4 rounded-lg bg-primary/10">
                  <p className="text-xs text-muted-foreground mb-1">Certeza recomendacion</p>
                  <p className="text-3xl font-bold text-primary">{confidence.certeza_recomendacion}%</p>
                </div>
              </div>
              <div className="mt-4 p-3 rounded-lg bg-secondary/50 text-center">
                <p className="text-xs text-muted-foreground">Modelo activo</p>
                <p className="font-medium text-success">{confidence.modelo_activo}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Chatbot />
    </div>
  );
}
