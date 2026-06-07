import { NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, Car, MapPin, ShoppingCart, Flag, Calendar, Settings, LogOut, ListOrdered, GitMerge, Globe } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { api } from '@/api/client';
import { SUPPORTED_LANGUAGES } from '@/i18n';

const links = [
  { to: '/',        icon: LayoutDashboard, labelKey: 'sidebar.nav.dashboard',     sub: false },
  { to: '/garage',  icon: Car,             labelKey: 'sidebar.nav.garage',        sub: false },
  { to: '/tracks',  icon: MapPin,          labelKey: 'sidebar.nav.tracks',        sub: false },
  { to: '/calendar',icon: Calendar,        labelKey: 'sidebar.nav.series',        sub: false },
  { to: '/shop',    icon: ShoppingCart,    labelKey: 'sidebar.nav.shop',          sub: false },
  { to: '/overlap', icon: GitMerge,        labelKey: 'sidebar.nav.overlap',       sub: false },
  { to: '/races',            icon: Flag,        labelKey: 'sidebar.nav.races',         sub: false },
  { to: '/races/by-series',  icon: ListOrdered, labelKey: 'sidebar.nav.racesBySeries', sub: true },
];

interface SidebarProps {
  onLogout: () => void;
}

export function Sidebar({ onLogout }: SidebarProps) {
  const { t, i18n } = useTranslation();

  const handleLogout = async () => {
    await api.auth.clear();
    onLogout();
  };

  const currentLanguage = SUPPORTED_LANGUAGES.find((l) => l.code === i18n.language)
    ?? SUPPORTED_LANGUAGES.find((l) => i18n.language?.startsWith(l.code))
    ?? SUPPORTED_LANGUAGES[0];

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-border bg-card">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-bold text-primary-foreground">iR</span>
        </div>
        <span className="font-semibold text-sm tracking-wide">{t('sidebar.appName')}</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 p-3">
        {links.map(({ to, icon: Icon, labelKey, sub }) => (
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
            {t(labelKey)}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-border p-3 space-y-0.5">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              title={t('sidebar.language')}
            >
              <Globe size={16} />
              <span className="flex-1 text-left">{currentLanguage.label}</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" side="top">
            {SUPPORTED_LANGUAGES.map((lang) => (
              <DropdownMenuItem
                key={lang.code}
                onClick={() => i18n.changeLanguage(lang.code)}
                className={cn(lang.code === currentLanguage.code && 'text-primary font-medium')}
              >
                {lang.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
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
          {t('sidebar.settings')}
        </NavLink>
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
        >
          <LogOut size={16} />
          {t('sidebar.logout')}
        </button>
      </div>
    </aside>
  );
}
