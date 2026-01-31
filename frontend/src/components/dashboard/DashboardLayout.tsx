import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  Boxes,
  AlertTriangle,
  Scale,
  Brain,
  ChevronLeft,
  LogOut,
  Settings,
  HelpCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Logo, LogoIcon } from '@/components/ui/logo';
import ApiStatus from '@/components/ui/api-status';

const mainMenuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard', description: 'Vista general' },
  { icon: BarChart3, label: 'Analytics', path: '/dashboard/analytics', description: 'Analisis detallado' },
  { icon: Scale, label: 'Balances', path: '/dashboard/balances', description: 'Balance energetico' },
  { icon: Boxes, label: 'Modelos', path: '/dashboard/modelos', description: 'ML Models' },
  { icon: AlertTriangle, label: 'Alertas', path: '/dashboard/alertas', description: 'Anomalias' },
  { icon: Brain, label: 'Explicabilidad', path: '/dashboard/explicabilidad', description: 'SHAP values' },
];

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 h-screen bg-[#0a0a0a] border-r border-border/50 flex flex-col z-40 transition-all duration-200 ease-out',
          collapsed ? 'w-[72px]' : 'w-[260px]'
        )}
        role="navigation"
        aria-label="Menu principal"
      >
        {/* Logo Section */}
        <div className={cn(
          'h-16 flex items-center border-b border-border/50',
          collapsed ? 'justify-center px-2' : 'px-4'
        )}>
          <Link 
            to="/" 
            className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-lg"
            aria-label="Ir al inicio"
          >
            {collapsed ? (
              <LogoIcon size="sm" />
            ) : (
              <Logo size="sm" />
            )}
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          <p className={cn(
            'text-[10px] font-medium text-muted-foreground uppercase tracking-wider mb-3',
            collapsed ? 'sr-only' : 'px-3'
          )}>
            Menu
          </p>
          
          {mainMenuItems.map((item) => {
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150',
                  'text-muted-foreground hover:text-foreground hover:bg-secondary/80',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  isActive && 'bg-primary/10 text-primary border-l-2 border-primary -ml-[2px] pl-[14px]',
                  collapsed && 'justify-center px-0'
                )}
                title={collapsed ? item.label : undefined}
                aria-current={isActive ? 'page' : undefined}
              >
                <item.icon className={cn(
                  'w-5 h-5 flex-shrink-0 transition-colors',
                  isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'
                )} />
                {!collapsed && (
                  <div className="flex flex-col min-w-0">
                    <span className={cn(
                      'text-sm font-medium truncate',
                      isActive && 'text-primary'
                    )}>
                      {item.label}
                    </span>
                    <span className="text-[10px] text-muted-foreground truncate">
                      {item.description}
                    </span>
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom Section */}
        <div className="p-3 border-t border-border/50 space-y-2">
          {/* API Status */}
          <div className={cn(
            'rounded-lg bg-secondary/30 p-2',
            collapsed && 'flex justify-center'
          )}>
            <ApiStatus className={collapsed ? '' : ''} />
          </div>

          {/* Secondary Actions */}
          {!collapsed && (
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="flex-1 justify-start gap-2 text-muted-foreground hover:text-foreground h-9"
                disabled
              >
                <Settings className="w-4 h-4" />
                <span className="text-xs">Ajustes</span>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="flex-1 justify-start gap-2 text-muted-foreground hover:text-foreground h-9"
                disabled
              >
                <HelpCircle className="w-4 h-4" />
                <span className="text-xs">Ayuda</span>
              </Button>
            </div>
          )}

          {/* Collapse Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
            className={cn(
              'w-full h-9 text-muted-foreground hover:text-foreground',
              collapsed ? 'justify-center' : 'justify-between'
            )}
            aria-label={collapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}
          >
            {!collapsed && <span className="text-xs">Colapsar</span>}
            <ChevronLeft className={cn(
              'w-4 h-4 transition-transform duration-200',
              collapsed && 'rotate-180'
            )} />
          </Button>
          
          {/* Exit Button */}
          <Link to="/" className="block">
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                'w-full h-9 text-muted-foreground hover:text-foreground hover:bg-destructive/10 hover:text-destructive',
                collapsed ? 'justify-center' : 'justify-start gap-2'
              )}
            >
              <LogOut className="w-4 h-4" />
              {!collapsed && <span className="text-xs">Salir al inicio</span>}
            </Button>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={cn(
          'flex-1 transition-all duration-200 ease-out min-h-screen',
          collapsed ? 'ml-[72px]' : 'ml-[260px]'
        )}
        role="main"
      >
        {children}
      </main>
    </div>
  );
}
