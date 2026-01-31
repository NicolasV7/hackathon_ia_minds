import { useEffect, useState } from 'react';
import { healthCheck } from '@/services/api';

interface ApiStatusProps {
  className?: string;
}

export default function ApiStatus({ className = '' }: ApiStatusProps) {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkApiStatus = async () => {
    try {
      setStatus('checking');
      const response = await healthCheck();
      setStatus(response.status === 'ok' || response.status === 'online' ? 'online' : 'offline');
    } catch (error) {
      console.warn('API Health check failed:', error);
      setStatus('offline');
    } finally {
      setLastCheck(new Date());
    }
  };

  useEffect(() => {
    checkApiStatus();
    // Check every 30 seconds
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'text-success';
      case 'offline': return 'text-destructive';
      case 'checking': return 'text-warning';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'online': return 'API Online';
      case 'offline': return 'API Offline (usando datos mock)';
      case 'checking': return 'Verificando...';
      default: return 'Desconocido';
    }
  };

  return (
    <div className={`flex items-center gap-2 text-sm ${className}`}>
      <div className={`w-2 h-2 rounded-full ${status === 'online' ? 'bg-success' : status === 'offline' ? 'bg-destructive' : 'bg-warning'} ${status === 'checking' ? 'animate-pulse' : ''}`} />
      <span className={getStatusColor()}>{getStatusText()}</span>
      {lastCheck && (
        <span className="text-muted-foreground text-xs">
          {lastCheck.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
}