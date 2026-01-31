import { cn } from '@/lib/utils';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showText?: boolean;
}

export function Logo({ size = 'md', className, showText = true }: LogoProps) {
  const sizes = {
    sm: { icon: 'w-8 h-8', bolt: 'w-4 h-4', leaf: 'scale-75' },
    md: { icon: 'w-10 h-10', bolt: 'w-5 h-5', leaf: 'scale-90' },
    lg: { icon: 'w-12 h-12', bolt: 'w-6 h-6', leaf: 'scale-100' },
  };

  const s = sizes[size];

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div 
        className={cn(
          'relative rounded-xl bg-[#111] border border-primary/30 flex items-center justify-center flex-shrink-0',
          s.icon
        )}
        aria-hidden="true"
      >
        {/* Lightning bolt */}
        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          className={cn('text-primary', s.bolt)}
        >
          <path 
            d="M13 2L4 14h7l-2 8 9-12h-7l2-8z" 
            fill="currentColor"
          />
        </svg>
        {/* Leaf accent */}
        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          className={cn('absolute bottom-0.5 right-0.5 w-2.5 h-2.5 text-emerald-500', s.leaf)}
        >
          <path 
            d="M17 8c-4 0-6 2-7 5 2-2 4-2 7-2v-3z" 
            fill="currentColor"
            opacity="0.9"
          />
        </svg>
      </div>
      {showText && (
        <div className="flex flex-col overflow-hidden">
          <span className="text-base font-semibold leading-tight tracking-tight">UPTC EcoEnergy</span>
          <span className="text-[11px] text-muted-foreground leading-tight">Gestion Energetica</span>
        </div>
      )}
    </div>
  );
}

export function LogoIcon({ size = 'md', className }: Omit<LogoProps, 'showText'>) {
  return <Logo size={size} className={className} showText={false} />;
}
