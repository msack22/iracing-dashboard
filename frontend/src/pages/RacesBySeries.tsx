import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { getCarGroup } from '@/lib/carGroups';
import { Flag, TrendingUp, TrendingDown, AlertTriangle, ChevronDown, ChevronRight, Filter } from 'lucide-react';
import { formatLapTime } from '@/lib/utils';

function RaceRow({ r }: { r: any }) {
  const delta = r.new_irating - r.old_irating;
  return (
    <div className="flex items-center justify-between px-4 py-2.5 hover:bg-muted/30 transition-colors">
      <div className="space-y-0.5 min-w-0">
        <p className="text-sm font-medium truncate">{r.track_name} <span className="text-muted-foreground font-normal text-xs">· {r.track_config}</span></p>
        <p className="text-xs text-muted-foreground">{new Date(r.start_time).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Pos.</p>
          <p className="text-sm font-semibold">{r.finish_position}<span className="text-xs text-muted-foreground">/{r.num_drivers}</span></p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Vuelta</p>
          <p className="text-xs font-mono">{formatLapTime(r.best_lap_time)}</p>
        </div>
        <div className="text-right w-14">
          <p className="text-xs text-muted-foreground">iR</p>
          <p className={`text-xs font-semibold flex items-center justify-end gap-0.5 ${delta >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {delta >= 0 ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
            {delta >= 0 ? '+' : ''}{delta}
          </p>
        </div>
        {r.incidents > 0 && (
          <span className={`flex items-center gap-0.5 text-xs ${r.incidents >= 4 ? 'text-red-400' : 'text-amber-400'}`}>
            <AlertTriangle size={10} /> {r.incidents}
          </span>
        )}
      </div>
    </div>
  );
}

function SeriesGroup({ group }: { group: any }) {
  const [open, setOpen] = useState(true);
  const isFormula = getCarGroup(group.races[0]?.car_name ?? group.series_name) === 'formula';

  return (
    <Card>
      <CardHeader className="pb-0 cursor-pointer" onClick={() => setOpen((v) => !v)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-base">{isFormula ? '🏎️' : '🚗'}</span>
            <CardTitle className="text-sm font-semibold">{group.series_name}</CardTitle>
            <Badge variant="outline" className="text-xs">{group.total_races} carrera{group.total_races !== 1 ? 's' : ''}</Badge>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex gap-4 text-xs text-muted-foreground">
              {group.best_position !== null && (
                <span>Mejor pos: <span className="font-semibold text-foreground">{group.best_position}</span></span>
              )}
              <span>Incidentes: <span className="font-semibold text-foreground">{group.total_incidents}x</span></span>
            </div>
            {open ? <ChevronDown size={14} className="text-muted-foreground" /> : <ChevronRight size={14} className="text-muted-foreground" />}
          </div>
        </div>
      </CardHeader>
      {open && (
        <CardContent className="p-0 mt-3">
          <div className="divide-y divide-border border-t border-border">
            {group.races.map((r: any) => <RaceRow key={r.subsession_id} r={r} />)}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

type CarFilter = 'all' | 'formula' | 'sport';

const CAR_FILTERS: { value: CarFilter; label: string; activeClass: string }[] = [
  { value: 'all',     label: 'Todos',         activeClass: 'bg-primary text-primary-foreground' },
  { value: 'formula', label: '🏎️ Fórmula',   activeClass: 'bg-orange-500/20 text-orange-400 border border-orange-500/30' },
  { value: 'sport',   label: '🚗 Sport Car',  activeClass: 'bg-blue-500/20 text-blue-400 border border-blue-500/30' },
];

export function RacesBySeries() {
  const [groups, setGroups] = useState<any[]>([]);
  const [carFilter, setCarFilter] = useState<CarFilter>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.races.bySeries(50).then((data) => {
      setGroups(data);
      setLoading(false);
    });
  }, []);

  const filtered = groups
    .map((g) => ({
      ...g,
      races: carFilter === 'all' ? g.races : g.races.filter((r: any) => getCarGroup(r.car_name) === carFilter),
    }))
    .filter((g) => g.races.length > 0);

  const totalRaces = filtered.reduce((s, g) => s + g.total_races, 0);

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Carreras por Serie</h1>
          <p className="text-sm text-muted-foreground">{filtered.length} series · {totalRaces} carreras</p>
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

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            No hay carreras registradas.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filtered.map((g) => <SeriesGroup key={g.series_id} group={g} />)}
        </div>
      )}
    </div>
  );
}
