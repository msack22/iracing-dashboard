import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Setup } from '@/pages/Setup';
import { Dashboard } from '@/pages/Dashboard';
import { Garage } from '@/pages/Garage';
import { Tracks } from '@/pages/Tracks';
import { SeriesCalendar } from '@/pages/SeriesCalendar';
import { ShopAdvisor } from '@/pages/ShopAdvisor';
import { Races } from '@/pages/Races';
import { RacesBySeries } from '@/pages/RacesBySeries';
import { Overlap } from '@/pages/Overlap';
import { Settings } from '@/pages/Settings';
import { api } from '@/api/client';

function AppShell({ onLogout }: { onLogout: () => void }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar onLogout={onLogout} />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/"          element={<Dashboard />} />
          <Route path="/garage"    element={<Garage />} />
          <Route path="/tracks"    element={<Tracks />} />
          <Route path="/calendar"  element={<SeriesCalendar />} />
          <Route path="/shop"      element={<ShopAdvisor />} />
          <Route path="/races"     element={<Races />} />
          <Route path="/races/by-series" element={<RacesBySeries />} />
          <Route path="/overlap"       element={<Overlap />} />
          <Route path="/settings"      element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const [configured, setConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    api.auth.status().then((s) => setConfigured(s.configured));
  }, []);

  if (configured === null) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!configured) {
    return <Setup onConfigured={() => setConfigured(true)} />;
  }

  return (
    <BrowserRouter>
      <AppShell onLogout={() => setConfigured(false)} />
    </BrowserRouter>
  );
}
