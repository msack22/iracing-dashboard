import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Car, MapPin, ShoppingCart, Flag, Calendar, Settings, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/api/client';
import { useRacingMode, RacingMode } from '@/context/RacingModeContext';

const links = [
  { to: '/',               icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/garage',         icon: Car,             label: 'Mi Garage' },
  { to: '/tracks',         icon: MapPin,          label: 'Mis Pistas' },
  { to: '/calendar',       icon: Calendar,        label: 'Series' },
  { to: '/shop',           icon: ShoppingCart,    label: 'Shop Advisor' },
  { to: '/races',          icon: Flag,            label: 'Carreras' },
];

interface SidebarProps {
  onLogout: () => void;
}

const MODE_OPTIONS: { value: RacingMode; label: string; color: string }[] = [
  { value: 'all',     label: 'Todo',       color: 'bg-muted text-muted-foreground' },
  { value: 'formula', label: '🏎️ Fórmula', color: 'bg-orange-500/20 text-orange-400' },
  { value: 'sport',   label: '🚗 Sport',   color: 'bg-blue-500/20 text-blue-400' },
];

export function Sidebar({ onLogout }: SidebarProps) {
  const { mode, setMode } = useRacingMode();

  const handleLogout = async () => {
    await api.auth.clear();
    onLogout();
  };

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-border bg-card">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-bold text-primary-foreground">iR</span>
        </div>
        <span className="font-semibold text-sm tracking-wide">Dashboard</span>
      </div>

      {/* Racing mode selector */}
      <div className="px-3 pt-3 pb-1">
        <p className="px-1 mb-1.5 text-xs text-muted-foreground">Vista</p>
        <div className="flex flex-col gap-0.5">
          {MODE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setMode(opt.value)}
              className={cn(
                'flex items-center rounded-lg px-3 py-1.5 text-xs font-medium transition-colors text-left',
                mode === opt.value
                  ? opt.color
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground',
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 p-3">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground',
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-3 space-y-0.5">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
              isActive
                ? 'bg-primary/10 text-primary font-medium'
                : 'text-muted-foreground hover:bg-accent hover:text-foreground',
            )
          }
        >
          <Settings size={16} />
          Configuración
        </NavLink>
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
        >
          <LogOut size={16} />
          Cerrar sesión
        </button>
      </div>
    </aside>
  );
}
