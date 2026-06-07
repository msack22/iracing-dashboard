import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/api/client';
import { getCarGroup } from '@/lib/carGroups';
import { Flag, TrendingUp, TrendingDown, AlertTriangle, Filter } from 'lucide-react';
import { formatLapTime } from '@/lib/utils';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';

type CarFilter = 'all' | 'formula' | 'sport';

const CAR_FILTERS: { value: CarFilter; label: string; activeClass: string }[] = [
  { value: 'all',     label: 'Todos',         activeClass: 'bg-primary text-primary-foreground' },
  { value: 'formula', label: '🏎️ Fórmula',   activeClass: 'bg-orange-500/20 text-orange-400 border border-orange-500/30' },
  { value: 'sport',   label: '🚗 Sport Car',  activeClass: 'bg-blue-500/20 text-blue-400 border border-blue-500/30' },
];

export function Races() {
  const [allRaces, setAllRaces] = useState<any[]>([]);
  const [carFilter, setCarFilter] = useState<CarFilter>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.races.recent(20).then((data) => {
      setAllRaces(data);
      setLoading(false);
    });
  }, []);

  const races = carFilter === 'all'
    ? allRaces
    : allRaces.filter((r) => getCarGroup(r.car_name) === carFilter);

  const incidentData = races.slice().reverse().map((r, i) => ({
    name: `C${i + 1}`,
    incidents: r.incidents,
    position: r.finish_position,
  }));

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Carreras</h1>
          <p className="text-sm text-muted-foreground">{races.length} carreras{carFilter !== 'all' ? ' en esta categoría' : ' recientes'}</p>
        </div>
        <Flag size={20} className="text-muted-foreground" />
      </div>

      {/* Local car-class filter */}
      <div className="flex items-center gap-2">
        <Filter size={13} className="text-muted-foreground shrink-0" />
        <div className="flex gap-1.5 flex-wrap">
          {CAR_FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setCarFilter(f.value)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                carFilter === f.value
                  ? f.activeClass
                  : 'border-border text-muted-foreground hover:bg-accent'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Incidents chart */}
      {races.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Incidentes por carrera</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={incidentData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} width={25} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 12 }}
                />
                <Bar dataKey="incidents" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Races table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : races.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            No hay carreras registradas para {carFilter === 'formula' ? 'Fórmula' : 'Sport Car'}.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Fecha</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Serie / Pista</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Auto</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-muted-foreground">Pos.</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">Mejor vuelta</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground">iR</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-muted-foreground">Inc.</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {races.map((r: any) => {
                    const irDelta = r.new_irating - r.old_irating;
                    const isP1 = r.finish_position === 1;
                    return (
                      <tr key={r.subsession_id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                          {new Date(r.start_time).toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium">{r.track_name}</div>
                          <div className="text-xs text-muted-foreground">{r.series_name}</div>
                        </td>
                        <td className="px-4 py-3 text-xs text-muted-foreground">{r.car_name}</td>
                        <td className="px-4 py-3 text-center">
                          <span className={`font-bold ${isP1 ? 'text-amber-400' : ''}`}>
                            {r.finish_position}
                          </span>
                          <span className="text-xs text-muted-foreground">/{r.num_drivers}</span>
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-xs">{formatLapTime(r.best_lap_time)}</td>
                        <td className="px-4 py-3 text-right">
                          <span className={`flex items-center justify-end gap-0.5 text-xs font-medium ${irDelta >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {irDelta >= 0 ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
                            {irDelta >= 0 ? '+' : ''}{irDelta}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {r.incidents > 0 ? (
                            <span className={`inline-flex items-center gap-0.5 text-xs ${r.incidents >= 4 ? 'text-red-400' : 'text-amber-400'}`}>
                              <AlertTriangle size={11} />
                              {r.incidents}
                            </span>
                          ) : (
                            <span className="text-xs text-emerald-400">✓</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
