import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { Calendar, Car, MapPin, CheckCircle2, XCircle, Filter } from 'lucide-react';

// ── Constants ──────────────────────────────────────────────────────────────────

const FORMULA_TYPES = ['F4', 'F3', 'Formula iR', 'Formula 2000', 'Classic F1'];
const SPORT_TYPES   = ['GT3', 'GT3 Cup', 'GT4', 'GTP', 'LMP3', 'LMP2', 'MX-5'];

function getCarGroup(carType: string): 'formula' | 'sport' {
  return FORMULA_TYPES.includes(carType) ? 'formula' : 'sport';
}

// ── Sub-components ────────────────────────────────────────────────────────────

function TrackDot({ track }: { track: any }) {
  return (
    <div
      title={`${track.name} · ${track.owned ? 'Tenés' : `$${track.price}`}`}
      className={`flex items-center gap-1.5 rounded-md px-2 py-1 text-xs ${
        track.owned
          ? 'bg-emerald-500/10 text-emerald-400'
          : 'bg-muted text-muted-foreground'
      }`}
    >
      <div className={`h-1.5 w-1.5 rounded-full shrink-0 ${track.owned ? 'bg-emerald-400' : 'bg-muted-foreground/40'}`} />
      {track.name}
      {!track.owned && <span className="text-muted-foreground/60">${track.price}</span>}
    </div>
  );
}

function SeriesCard({ series }: { series: any }) {
  const group = getCarGroup(series.car_type);
  const isFormula = group === 'formula';

  return (
    <Card className={`transition-all hover:border-primary/30 ${
      series.can_race ? 'border-emerald-500/20' : ''
    }`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Badge
                variant={isFormula ? 'default' : 'secondary'}
                className={`text-xs ${isFormula ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}
              >
                {isFormula ? '🏎️ Fórmula' : '🚗 Sport Car'}
              </Badge>
              <Badge variant="outline" className="text-xs">{series.car_type}</Badge>
            </div>
            <CardTitle className="text-sm">{series.series_name}</CardTitle>
          </div>
          {series.can_race ? (
            <CheckCircle2 size={18} className="text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <XCircle size={18} className="text-muted-foreground/40 shrink-0 mt-0.5" />
          )}
        </div>

        <p className={`text-xs font-medium ${series.can_race ? 'text-emerald-400' : 'text-amber-400'}`}>
          {series.can_race
            ? 'Listo para correr'
            : `Faltan: ${series.missing_cars.length > 0 ? `${series.missing_cars.length} auto(s)` : ''} ${series.missing_tracks.length > 0 ? `· ${series.missing_tracks.length} pista(s)` : ''}`
          }
        </p>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Cars */}
        <div>
          <p className="text-xs text-muted-foreground mb-1.5 flex items-center gap-1">
            <Car size={11} /> Autos ({series.owned_cars_count}/{series.cars.length} propios)
          </p>
          <div className="flex flex-wrap gap-1.5">
            {series.cars.map((car: any) => (
              <span
                key={car.car_id}
                className={`text-xs rounded-md px-2 py-0.5 ${
                  car.owned
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-muted text-muted-foreground line-through'
                }`}
              >
                {car.name}
              </span>
            ))}
          </div>
        </div>

        {/* Tracks */}
        <div>
          <p className="text-xs text-muted-foreground mb-1.5 flex items-center gap-1">
            <MapPin size={11} /> Pistas esta temporada ({series.owned_tracks_count}/{series.season_tracks.length})
          </p>
          <div className="flex flex-wrap gap-1.5">
            {series.season_tracks.map((t: any) => (
              <TrackDot key={t.track_id} track={t} />
            ))}
          </div>
        </div>

        {/* Missing items summary */}
        {!series.can_race && (series.missing_cars.length > 0 || series.missing_tracks.length > 0) && (
          <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-2 space-y-1">
            <p className="text-xs font-medium text-amber-400">Para poder correr necesitás:</p>
            {series.missing_cars.map((c: any) => (
              <p key={c.car_id} className="text-xs text-muted-foreground">
                🏎️ {c.name} — <span className="text-foreground">${c.price}</span>
              </p>
            ))}
            {series.missing_tracks.slice(0, 3).map((t: any) => (
              <p key={t.track_id} className="text-xs text-muted-foreground">
                🗺️ {t.name} — <span className="text-foreground">${t.price}</span>
              </p>
            ))}
            {series.missing_tracks.length > 3 && (
              <p className="text-xs text-muted-foreground">
                + {series.missing_tracks.length - 3} pistas más…
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

type GroupFilter = 'all' | 'formula' | 'sport';

export function SeriesCalendar() {
  const [series, setSeries] = useState<any[]>([]);
  const [groupFilter, setGroupFilter] = useState<GroupFilter>('all');
  const [typeFilter, setTypeFilter] = useState<string[]>([]);
  const [readyOnly, setReadyOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.series.all().then((data) => {
      setSeries(data);
      setLoading(false);
    });
  }, []);

  const allTypes = [...new Set(series.map((s) => s.car_type))];
  const formulaTypes = allTypes.filter((t) => FORMULA_TYPES.includes(t));
  const sportTypes   = allTypes.filter((t) => SPORT_TYPES.includes(t));

  const filtered = series.filter((s) => {
    if (readyOnly && !s.can_race) return false;
    if (groupFilter === 'formula' && !FORMULA_TYPES.includes(s.car_type)) return false;
    if (groupFilter === 'sport' && !SPORT_TYPES.includes(s.car_type)) return false;
    if (typeFilter.length > 0 && !typeFilter.includes(s.car_type)) return false;
    return true;
  });

  const readyCount = series.filter((s) => s.can_race).length;

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Calendario de Series</h1>
          <p className="text-sm text-muted-foreground">
            {readyCount}/{series.length} series listas para correr con tu contenido actual
          </p>
        </div>
        <Calendar size={20} className="text-muted-foreground" />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4 space-y-3">
          {/* Group filter */}
          <div className="flex items-center gap-2">
            <Filter size={13} className="text-muted-foreground shrink-0" />
            <div className="flex gap-1.5 flex-wrap">
              {([['all', 'Todas'], ['formula', '🏎️ Fórmula'], ['sport', '🚗 Sport Car']] as [GroupFilter, string][]).map(([val, label]) => (
                <button
                  key={val}
                  onClick={() => { setGroupFilter(val); setTypeFilter([]); }}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                    groupFilter === val
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border text-muted-foreground hover:bg-accent hover:text-foreground'
                  }`}
                >
                  {label}
                </button>
              ))}

              <div className="w-px bg-border mx-1" />

              {/* "Solo listas" toggle */}
              <button
                onClick={() => setReadyOnly(!readyOnly)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                  readyOnly
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : 'border-border text-muted-foreground hover:bg-accent'
                }`}
              >
                ✓ Solo listas para correr
              </button>
            </div>
          </div>

          {/* Specific type chips */}
          {(groupFilter === 'formula' ? formulaTypes : groupFilter === 'sport' ? sportTypes : allTypes).length > 1 && (
            <div className="flex flex-wrap gap-1.5 pl-5">
              {(groupFilter === 'formula' ? formulaTypes : groupFilter === 'sport' ? sportTypes : allTypes).map((t) => (
                <button
                  key={t}
                  onClick={() => setTypeFilter(
                    typeFilter.includes(t) ? typeFilter.filter((x) => x !== t) : [...typeFilter, t]
                  )}
                  className={`rounded-md px-2.5 py-1 text-xs transition-colors border ${
                    typeFilter.includes(t)
                      ? 'bg-primary/20 text-primary border-primary/40'
                      : 'border-border/50 text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((s) => (
            <SeriesCard key={s.series_id} series={s} />
          ))}
          {filtered.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
              No hay series con los filtros seleccionados.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
