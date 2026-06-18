import { useEffect, useRef, useState } from 'react';
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
  const [backendDown, setBackendDown] = useState(false);
  const healthRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const check = () =>
      fetch('/health', { signal: AbortSignal.timeout(4000) })
        .then(r => setBackendDown(!r.ok))
        .catch(() => setBackendDown(true));
    check();
    healthRef.current = setInterval(check, 15000);
    return () => { if (healthRef.current) clearInterval(healthRef.current); };
  }, []);

  useEffect(() => {
    api.auth.status()
      .then((s) => { setBackendDown(false); setConfigured(s.configured); })
      .catch(() => { setBackendDown(true); setConfigured(false); });
  }, []);

  const backendBanner = backendDown ? (
    <div className="fixed inset-x-0 top-0 z-[9999] bg-red-600 px-4 py-3 text-center text-white shadow-lg">
      <span className="text-lg font-bold">⚠️ Backend Iracing no disponible</span>
      <span className="ml-3 text-sm opacity-90">Ejecutá: <code className="font-mono bg-red-800 rounded px-1">cd backend && source venv/bin/activate && python main.py</code></span>
    </div>
  ) : null;

  if (configured === null) {
    return (
      <>
        {backendBanner}
        <div className="flex h-screen items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      </>
    );
  }

  if (!configured) {
    return (
      <>
        {backendBanner}
        <Setup onConfigured={() => setConfigured(true)} />
      </>
    );
  }

  return (
    <>
      {backendBanner}
      <BrowserRouter>
        <AppShell onLogout={() => setConfigured(false)} />
      </BrowserRouter>
    </>
  );
}
