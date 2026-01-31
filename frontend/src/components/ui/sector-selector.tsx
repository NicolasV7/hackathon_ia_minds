import { useState } from 'react';
import { 
  Utensils, 
  FlaskConical, 
  GraduationCap, 
  Theater, 
  Briefcase, 
  LayoutGrid,
  ChevronDown,
  Check 
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

const SECTORS = [
  { id: 'all', nombre: 'Todos los sectores', icon: LayoutGrid, color: 'text-primary' },
  { id: 'comedores', nombre: 'Comedores', icon: Utensils, color: 'text-amber-400' },
  { id: 'laboratorios', nombre: 'Laboratorios', icon: FlaskConical, color: 'text-purple-400' },
  { id: 'salones', nombre: 'Salones', icon: GraduationCap, color: 'text-sky-400' },
  { id: 'auditorios', nombre: 'Auditorios', icon: Theater, color: 'text-rose-400' },
  { id: 'oficinas', nombre: 'Oficinas', icon: Briefcase, color: 'text-emerald-400' },
];

interface SectorSelectorProps {
  selectedSector: string;
  onSectorChange: (sectorId: string) => void;
  className?: string;
}

export function SectorSelector({
  selectedSector,
  onSectorChange,
  className,
}: SectorSelectorProps) {
  const [open, setOpen] = useState(false);

  const selectedSectorData = SECTORS.find(s => s.id === selectedSector) || SECTORS[0];
  const Icon = selectedSectorData.icon;

  const handleSelect = (sectorId: string) => {
    onSectorChange(sectorId);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          aria-label="Seleccionar sector"
          className={cn(
            'justify-between gap-2 min-w-[180px] h-10',
            className
          )}
        >
          <div className="flex items-center gap-2">
            <Icon className={cn('w-4 h-4', selectedSectorData.color)} />
            <span className="truncate">{selectedSectorData.nombre}</span>
          </div>
          <ChevronDown className={cn(
            'w-4 h-4 text-muted-foreground transition-transform duration-200',
            open && 'rotate-180'
          )} />
        </Button>
      </PopoverTrigger>
      <PopoverContent 
        className="w-[220px] p-2" 
        align="end"
        sideOffset={8}
      >
        <div className="space-y-1">
          {SECTORS.map((sector) => {
            const SectorIcon = sector.icon;
            const isSelected = selectedSector === sector.id;
            
            return (
              <button
                key={sector.id}
                onClick={() => handleSelect(sector.id)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-left',
                  'hover:bg-secondary/80 focus:bg-secondary/80 focus:outline-none',
                  isSelected && 'bg-primary/10'
                )}
              >
                <SectorIcon className={cn('w-4 h-4', sector.color)} />
                <span className={cn(
                  'flex-1 text-sm',
                  isSelected && 'font-medium'
                )}>
                  {sector.nombre}
                </span>
                {isSelected && (
                  <Check className="w-4 h-4 text-primary" />
                )}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}
