import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Car, MapPin, ShoppingCart, Flag, Calendar, Settings, LogOut, ListOrdered, GitMerge } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/api/client';

const links = [
  { to: '/',        icon: LayoutDashboard, label: 'Dashboard',   sub: false },
  { to: '/garage',  icon: Car,             label: 'Mi Garage',   sub: false },
  { to: '/tracks',  icon: MapPin,          label: 'Pistas',      sub: false },
  { to: '/calendar',icon: Calendar,        label: 'Series',      sub: false },
  { to: '/shop',    icon: ShoppingCart,    label: 'Shop Advisor',sub: false },
  { to: '/overlap', icon: GitMerge,        label: 'Overlap',     sub: false },
  { to: '/races',            icon: Flag,        label: 'Carreras',  sub: false },
  { to: '/races/by-series',  icon: ListOrdered, label: 'Por Serie', sub: true },
];

interface SidebarProps {
  onLogout: () => void;
}

export function Sidebar({ onLogout }: SidebarProps) {
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

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 p-3">
        {links.map(({ to, icon: Icon, label, sub }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg py-2 text-sm transition-colors',
                sub ? 'pl-8 pr-3' : 'px-3',
                isActive
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground',
              )
            }
          >
            <Icon size={sub ? 13 : 16} />
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
