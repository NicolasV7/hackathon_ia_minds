import { Zap, BarChart3, Activity, Database } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LoadingScreenProps {
  title?: string;
  description?: string;
  variant?: 'default' | 'analytics' | 'balances' | 'models' | 'alerts';
}

const variants = {
  default: {
    icon: Zap,
    color: 'text-primary',
    bgColor: 'bg-primary/10',
  },
  analytics: {
    icon: BarChart3,
    color: 'text-sky-400',
    bgColor: 'bg-sky-400/10',
  },
  balances: {
    icon: Activity,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-400/10',
  },
  models: {
    icon: Database,
    color: 'text-purple-400',
    bgColor: 'bg-purple-400/10',
  },
  alerts: {
    icon: Activity,
    color: 'text-amber-400',
    bgColor: 'bg-amber-400/10',
  },
};

export function LoadingScreen({ 
  title = 'Cargando datos', 
  description = 'Conectando con el servidor...',
  variant = 'default' 
}: LoadingScreenProps) {
  const { icon: Icon, color, bgColor } = variants[variant];

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex flex-col items-center gap-6 text-center max-w-sm">
        {/* Animated icon container */}
        <div className={cn('relative p-6 rounded-2xl', bgColor)}>
          {/* Pulsing rings */}
          <div className={cn('absolute inset-0 rounded-2xl animate-ping opacity-20', bgColor)} />
          <div 
            className={cn('absolute inset-2 rounded-xl animate-pulse opacity-30', bgColor)} 
            style={{ animationDelay: '150ms' }}
          />
          
          {/* Icon */}
          <Icon className={cn('w-10 h-10 relative z-10 animate-pulse', color)} />
        </div>

        {/* Text */}
        <div className="space-y-2">
          <h3 className="text-lg font-medium">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>

        {/* Loading dots */}
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={cn('w-2 h-2 rounded-full', color.replace('text-', 'bg-'))}
              style={{
                animation: 'bounce 1s infinite',
                animationDelay: `${i * 150}ms`,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
