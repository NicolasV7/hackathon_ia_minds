import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  BarChart3,
  Boxes,
  AlertTriangle,
  Scale,
  Brain,
  ChevronLeft,
  Zap,
  LogOut,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import ApiStatus from '@/components/ui/api-status';

const menuItems = [
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
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 80 : 240 }}
        transition={{ duration: 0.15, ease: "easeOut" }}
        className="fixed left-0 top-0 h-screen bg-sidebar border-r border-sidebar-border flex flex-col z-40"
      >
        {/* Logo */}
        <div className="p-4 border-b border-sidebar-border">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
              <Zap className="w-6 h-6 text-primary-foreground" />
            </div>
            {!collapsed && (
              <div className="overflow-hidden">
                <h1 className="font-bold text-lg text-foreground">UPTC Energy</h1>
                <p className="text-xs text-muted-foreground">IA Platform</p>
              </div>
            )}
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path || 
              (item.path === '/dashboard' && location.pathname === '/dashboard');
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  'sidebar-item',
                  isActive && 'active'
                )}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse Button */}
        <div className="p-3 border-t border-sidebar-border">
          <ApiStatus className="mb-3" />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
            className="w-full justify-center"
          >
            <ChevronLeft className={cn(
              'w-5 h-5 transition-transform',
              collapsed && 'rotate-180'
            )} />
          </Button>
          
          <Link to="/">
            <Button
              variant="ghost"
              size="sm"
              className="w-full mt-2 gap-2 text-muted-foreground hover:text-foreground"
            >
              <LogOut className="w-4 h-4" />
              {!collapsed && <span>Salir</span>}
            </Button>
          </Link>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main
        className={cn(
          'flex-1 transition-all duration-150 ease-out',
          collapsed ? 'ml-20' : 'ml-60'
        )}
      >
        {children}
      </main>
    </div>
  );
}
