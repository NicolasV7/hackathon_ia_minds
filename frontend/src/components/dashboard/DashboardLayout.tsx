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
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Logo, LogoIcon } from '@/components/ui/logo';
import ApiStatus from '@/components/ui/api-status';

const mainMenuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: BarChart3, label: 'Analytics', path: '/dashboard/analytics' },
  { icon: Scale, label: 'Balances', path: '/dashboard/balances' },
  { icon: Boxes, label: 'Modelos', path: '/dashboard/modelos' },
  { icon: AlertTriangle, label: 'Alertas', path: '/dashboard/alertas' },
  { icon: Brain, label: 'Explicabilidad', path: '/dashboard/explicabilidad' },
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
          collapsed ? 'w-[68px]' : 'w-[240px]'
        )}
        role="navigation"
        aria-label="Menu principal"
      >
        {/* Logo Section */}
        <div className={cn(
          'h-16 flex items-center border-b border-border/50',
          collapsed ? 'justify-center' : 'px-4'
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
        <nav className={cn(
          'flex-1 py-4 space-y-1 overflow-y-auto',
          collapsed ? 'px-2' : 'px-3'
        )}>
          {mainMenuItems.map((item) => {
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'group flex items-center gap-3 rounded-lg transition-all duration-150',
                  'text-muted-foreground hover:text-foreground hover:bg-secondary/80',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  collapsed 
                    ? 'justify-center p-3' 
                    : 'px-3 py-2.5',
                  isActive && !collapsed && 'bg-primary/10 text-primary border-l-2 border-primary -ml-[2px] pl-[14px]',
                  isActive && collapsed && 'bg-primary/10 text-primary'
                )}
                title={collapsed ? item.label : undefined}
                aria-current={isActive ? 'page' : undefined}
              >
                <item.icon className={cn(
                  'w-5 h-5 flex-shrink-0 transition-colors',
                  isActive ? 'text-primary' : 'text-muted-foreground group-hover:text-foreground'
                )} />
                {!collapsed && (
                  <span className={cn(
                    'text-sm font-medium',
                    isActive && 'text-primary'
                  )}>
                    {item.label}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom Section */}
        <div className={cn(
          'border-t border-border/50',
          collapsed ? 'p-2' : 'p-3'
        )}>
          {/* API Status */}
          {!collapsed && (
            <div className="mb-2 px-1">
              <ApiStatus />
            </div>
          )}
          
          {/* Collapse Toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
            className={cn(
              'w-full text-muted-foreground hover:text-foreground',
              collapsed ? 'h-10 justify-center' : 'h-9 justify-between'
            )}
            aria-label={collapsed ? 'Expandir menu' : 'Colapsar menu'}
          >
            {!collapsed && <span className="text-xs">Colapsar</span>}
            <ChevronLeft className={cn(
              'w-4 h-4 transition-transform duration-200',
              collapsed && 'rotate-180'
            )} />
          </Button>
          
          {/* Exit Button */}
          <Link to="/" className="block mt-1">
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                'w-full text-muted-foreground hover:text-foreground hover:bg-destructive/10 hover:text-destructive',
                collapsed ? 'h-10 justify-center' : 'h-9 justify-start gap-2'
              )}
            >
              <LogOut className="w-4 h-4" />
              {!collapsed && <span className="text-xs">Salir</span>}
            </Button>
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main
        className={cn(
          'flex-1 transition-all duration-200 ease-out min-h-screen',
          collapsed ? 'ml-[68px]' : 'ml-[240px]'
        )}
        role="main"
      >
        {children}
      </main>
    </div>
  );
}
