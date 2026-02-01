import { useState } from 'react';
import { MapPin, Building2, Users, Zap, ChevronDown, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

export interface Sede {
  id: string;
  nombre: string;
  estudiantes?: number;
  consumo_energia?: number;
}

interface SedeSelectorProps {
  sedes: Sede[];
  selectedSede: string;
  onSedeChange: (sedeId: string) => void;
  showAllOption?: boolean;
  className?: string;
}

export function SedeSelector({
  sedes,
  selectedSede,
  onSedeChange,
  showAllOption = true,
  className,
}: SedeSelectorProps) {
  const [open, setOpen] = useState(false);

  const selectedSedeData = sedes.find(s => s.id === selectedSede);
  const displayName = selectedSede === 'all' 
    ? 'Todas las sedes' 
    : selectedSedeData?.nombre || 'Seleccionar sede';

  const handleSelect = (sedeId: string) => {
    onSedeChange(sedeId);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label="Seleccionar sede"
          className={cn(
            'justify-between gap-2 min-w-[200px] h-10',
            className
          )}
        >
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-primary" />
            <span className="truncate">{displayName}</span>
          </div>
          <ChevronDown className={cn(
            'w-4 h-4 text-muted-foreground transition-transform duration-200',
            open && 'rotate-180'
          )} />
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        className="w-[320px] p-0" 
        align="end"
        sideOffset={8}
      >
        <div className="p-3 border-b border-border">
          <p className="text-sm font-medium">Seleccionar Sede</p>
          <p className="text-xs text-muted-foreground">Filtra los datos por ubicacion</p>
        </div>
        
        <div className="p-2 max-h-[320px] overflow-y-auto">
          {/* All sedes option */}
          {showAllOption && (
            <button
              onClick={() => handleSelect('all')}
              className={cn(
                'w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left',
                'hover:bg-secondary/80 focus:bg-secondary/80 focus:outline-none',
                selectedSede === 'all' && 'bg-primary/10 border border-primary/20'
              )}
            >
              <div className={cn(
                'w-10 h-10 rounded-lg flex items-center justify-center',
                selectedSede === 'all' ? 'bg-primary text-primary-foreground' : 'bg-secondary'
              )}>
                <Building2 className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">Todas las sedes</p>
                <p className="text-xs text-muted-foreground">Vista consolidada</p>
              </div>
              {selectedSede === 'all' && (
                <Check className="w-4 h-4 text-primary" />
              )}
            </button>
          )}

          {/* Divider */}
          {showAllOption && sedes.length > 0 && (
            <div className="my-2 px-3">
              <div className="h-px bg-border" />
            </div>
          )}

          {/* Individual sedes */}
          <div className="space-y-1">
            {sedes.map((sede) => (
              <button
                key={sede.id}
                onClick={() => handleSelect(sede.id)}
                className={cn(
                  'w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left',
                  'hover:bg-secondary/80 focus:bg-secondary/80 focus:outline-none',
                  selectedSede === sede.id && 'bg-primary/10 border border-primary/20'
                )}
              >
                <div className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center',
                  selectedSede === sede.id ? 'bg-primary text-primary-foreground' : 'bg-secondary'
                )}>
                  <MapPin className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{sede.nombre}</p>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    {sede.estudiantes && (
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {sede.estudiantes.toLocaleString()}
                      </span>
                    )}
                    {sede.consumo_energia && (
                      <span className="flex items-center gap-1">
                        <Zap className="w-3 h-3" />
                        {(sede.consumo_energia / 1000).toFixed(1)}K kWh
                      </span>
                    )}
                  </div>
                </div>
                {selectedSede === sede.id && (
                  <Check className="w-4 h-4 text-primary flex-shrink-0" />
                )}
              </button>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
