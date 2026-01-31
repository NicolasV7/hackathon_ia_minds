import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  healthCheck, 
  getSedesInfo, 
  getDashboardKPIs, 
  getUnresolvedAnomalies,
  sendChatMessage 
} from '@/services/api';
import { CheckCircle, XCircle, AlertCircle, Loader2, Database, MessageSquare, Activity } from 'lucide-react';

export default function ApiTestPage() {
  const [tests, setTests] = useState<Record<string, 'pending' | 'success' | 'error' | 'loading'>>({});
  const [results, setResults] = useState<Record<string, any>>({});

  const runTest = async (testName: string, testFn: () => Promise<any>) => {
    setTests(prev => ({ ...prev, [testName]: 'loading' }));
    try {
      const result = await testFn();
      setTests(prev => ({ ...prev, [testName]: 'success' }));
      setResults(prev => ({ ...prev, [testName]: result }));
      return result;
    } catch (error) {
      setTests(prev => ({ ...prev, [testName]: 'error' }));
      setResults(prev => ({ ...prev, [testName]: error }));
      throw error;
    }
  };

  const testEndpoints = [
    {
      name: 'health',
      title: 'Health Check',
      icon: Activity,
      description: 'Verifica si el backend está en línea',
      test: () => healthCheck(),
    },
    {
      name: 'sedes',
      title: 'Información de Sedes',
      icon: Database,
      description: 'Obtiene datos de las sedes UPTC',
      test: () => getSedesInfo(),
    },
    {
      name: 'dashboard',
      title: 'Dashboard KPIs',
      icon: Database,
      description: 'Obtiene métricas del dashboard',
      test: () => getDashboardKPIs(),
    },
    {
      name: 'anomalies',
      title: 'Anomalías',
      icon: AlertCircle,
      description: 'Obtiene anomalías no resueltas',
      test: () => getUnresolvedAnomalies(),
    },
    {
      name: 'chat',
      title: 'Chat IA',
      icon: MessageSquare,
      description: 'Prueba el chatbot de IA',
      test: () => sendChatMessage('Hola, ¿cómo estás?'),
    },
  ];

  const runAllTests = async () => {
    for (const endpoint of testEndpoints) {
      try {
        await runTest(endpoint.name, endpoint.test);
        await new Promise(resolve => setTimeout(resolve, 500)); // Small delay between tests
      } catch (error) {
        console.error(`Test ${endpoint.name} failed:`, error);
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-5 h-5 text-success" />;
      case 'error': return <XCircle className="w-5 h-5 text-destructive" />;
      case 'loading': return <Loader2 className="w-5 h-5 text-warning animate-spin" />;
      default: return <AlertCircle className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success': return <Badge variant="default" className="bg-success text-success-foreground">OK</Badge>;
      case 'error': return <Badge variant="destructive">Error</Badge>;
      case 'loading': return <Badge variant="secondary">Cargando...</Badge>;
      default: return <Badge variant="outline">Pendiente</Badge>;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pruebas de Conectividad API</h1>
          <p className="text-muted-foreground">
            Verifica la conexión entre el frontend y el backend FastAPI
          </p>
        </div>
        <Button onClick={runAllTests} size="lg">
          Ejecutar Todas las Pruebas
        </Button>
      </div>

      <Alert>
        <Activity className="h-4 w-4" />
        <AlertDescription>
          <strong>API Endpoint:</strong> {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {testEndpoints.map((endpoint) => (
          <Card key={endpoint.name} className="relative">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <endpoint.icon className="w-5 h-5" />
                  {endpoint.title}
                </div>
                {getStatusIcon(tests[endpoint.name] || 'pending')}
              </CardTitle>
              <p className="text-sm text-muted-foreground">{endpoint.description}</p>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                {getStatusBadge(tests[endpoint.name] || 'pending')}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => runTest(endpoint.name, endpoint.test)}
                  disabled={tests[endpoint.name] === 'loading'}
                >
                  Probar
                </Button>
              </div>
              
              {results[endpoint.name] && (
                <div className="mt-3">
                  <details>
                    <summary className="text-xs font-medium cursor-pointer hover:text-primary">
                      Ver resultado
                    </summary>
                    <pre className="text-xs mt-2 p-2 bg-secondary rounded overflow-auto max-h-32">
                      {JSON.stringify(results[endpoint.name], null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Configuración de Entorno</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>VITE_API_URL:</strong> {import.meta.env.VITE_API_URL || 'No configurado'}
            </div>
            <div>
              <strong>VITE_NODE_ENV:</strong> {import.meta.env.VITE_NODE_ENV || 'No configurado'}
            </div>
            <div>
              <strong>VITE_DEBUG:</strong> {import.meta.env.VITE_DEBUG || 'No configurado'}
            </div>
            <div>
              <strong>Modo de desarrollo:</strong> {import.meta.env.DEV ? 'Sí' : 'No'}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}