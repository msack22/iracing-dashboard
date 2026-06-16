import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { CAR_GROUP_LABEL_KEYS, CAR_GROUP_ORDER, getCarGroupKey, type CarGroupKey, LICENSE_CLASSES, LICENSE_BADGE_CLASS } from '@/lib/carGroups';

const GROUP_BADGE_CLASS: Record<CarGroupKey, string> = {
  formula: 'bg-orange-500/20 text-orange-400 border border-orange-500/30',
  gt_sport: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  oval_nascar: 'bg-red-500/10 text-red-400 border border-red-500/20',
  dirt: 'bg-amber-700/15 text-amber-500 border border-amber-700/30',
  rallycross: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  other: 'bg-muted text-muted-foreground border border-border',
};
import { Calendar, Car, MapPin, CheckCircle2, XCircle, Filter, Award, Search } from 'lucide-react';

// ── Sub-components ────────────────────────────────────────────────────────────

function TrackDot({ track }: { track: any }) {
  const { t } = useTranslation();
  return (
    <div
      title={`${track.name} · ${track.owned ? t('seriesCalendar.trackOwned') : `$${track.price}`}`}
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
  const { t } = useTranslation();
  const group = getCarGroupKey(series.car_type, series.series_name);

  const missingParts = [
    series.missing_cars.length > 0 ? t('seriesCalendar.missingCarsCount', { count: series.missing_cars.length }) : '',
    series.missing_tracks.length > 0 ? t('seriesCalendar.missingTracksCount', { count: series.missing_tracks.length }) : '',
  ].filter(Boolean).join(' ');

  return (
    <Card className={`transition-all hover:border-primary/30 ${
      series.can_race ? 'border-emerald-500/20' : ''
    }`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className={`text-xs ${GROUP_BADGE_CLASS[group]}`}>
                {t(CAR_GROUP_LABEL_KEYS[group])}
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
            ? t('seriesCalendar.readyToRace')
            : `${t('seriesCalendar.missingPrefix')} ${missingParts}`
          }
        </p>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Cars */}
        <div>
          <p className="text-xs text-muted-foreground mb-1.5 flex items-center gap-1">
            <Car size={11} /> {t('seriesCalendar.ownCars', { owned: series.owned_cars_count, total: series.cars.length })}
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
            <MapPin size={11} /> {t('seriesCalendar.seasonTracks', { owned: series.owned_tracks_count, total: series.season_tracks.length })}
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
            <p className="text-xs font-medium text-amber-400">{t('seriesCalendar.needToRace')}</p>
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
                {t('seriesCalendar.moreTracksEllipsis', { count: series.missing_tracks.length - 3 })}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function SeriesCalendar() {
  const { t } = useTranslation();
  const [allSeries, setAllSeries] = useState<any[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<CarGroupKey[]>([]);
  const [licenseByCategory, setLicenseByCategory] = useState<Partial<Record<CarGroupKey, string[]>>>({});
  const [typeFilter, setTypeFilter] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [readyOnly, setReadyOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.series.all().then((data) => {
      setAllSeries(data);
      setLoading(false);
    });
  }, []);

  const toggleCategory = (g: CarGroupKey) => setCategoryFilter((prev) =>
    prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]
  );
  const toggleCategoryLicense = (g: CarGroupKey, lic: string) => setLicenseByCategory((prev) => {
    const current = prev[g] ?? [];
    return { ...prev, [g]: current.includes(lic) ? current.filter((x) => x !== lic) : [...current, lic] };
  });

  // Filtro local por categoría de auto (multiselección), cada una con su propio
  // subfiltro de licencia (ej. Fórmula + C, Sport + D), luego refinamientos
  const sq = search.trim().toLowerCase();
  const groupFiltered = allSeries.filter((s: any) => {
    if (sq && !s.series_name.toLowerCase().includes(sq) && !s.car_type.toLowerCase().includes(sq)) return false;
    if (categoryFilter.length === 0) return true;
    const cat = getCarGroupKey(s.car_type, s.series_name);
    if (!categoryFilter.includes(cat)) return false;
    const lics = licenseByCategory[cat];
    if (lics && lics.length > 0 && !lics.includes(s.license_class)) return false;
    return true;
  });
  const allTypes = [...new Set(groupFiltered.map((s: any) => s.car_type))];

  const filtered = groupFiltered.filter((s: any) => {
    if (readyOnly && !s.can_race) return false;
    if (typeFilter.length > 0 && !typeFilter.includes(s.car_type)) return false;
    return true;
  });

  const readyCount = groupFiltered.filter((s: any) => s.can_race).length;

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">{t('seriesCalendar.title')}</h1>
          <p className="text-sm text-muted-foreground">
            {t('seriesCalendar.subtitle', { ready: readyCount, total: groupFiltered.length })}
          </p>
        </div>
        <Calendar size={20} className="text-muted-foreground" />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4 space-y-3">
          {/* Search */}
          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('seriesCalendar.searchPlaceholder')}
              className="h-8 w-full rounded-md border border-border bg-transparent pl-8 pr-3 text-sm outline-none focus:border-primary/50"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter size={13} className="text-muted-foreground shrink-0" />
            <div className="flex gap-1.5 flex-wrap">
              {/* Car category filter (multiselección) */}
              <button
                onClick={() => { setCategoryFilter([]); setLicenseByCategory({}); }}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                  categoryFilter.length === 0
                    ? 'bg-primary text-primary-foreground'
                    : 'border-border text-muted-foreground hover:bg-accent'
                }`}
              >
                {t('seriesCalendar.filterAll')}
              </button>
              {CAR_GROUP_ORDER.map((g) => (
                <button
                  key={g}
                  onClick={() => toggleCategory(g)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                    categoryFilter.includes(g)
                      ? GROUP_BADGE_CLASS[g]
                      : 'border-border text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {t(CAR_GROUP_LABEL_KEYS[g])}
                </button>
              ))}
              {/* "Solo listas" toggle */}
              <button
                onClick={() => setReadyOnly(!readyOnly)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                  readyOnly
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    : 'border-border text-muted-foreground hover:bg-accent'
                }`}
              >
                {t('seriesCalendar.readyOnly')}
              </button>
            </div>
          </div>

          {/* Subfiltro de licencia por cada categoría seleccionada (ej. Fórmula + C, Sport + D) */}
          {categoryFilter.length > 0 && (
            <div className="space-y-1.5 pl-5">
              {categoryFilter.map((g) => (
                <div key={g} className="flex items-center gap-2 flex-wrap">
                  <Badge variant="secondary" className={`text-xs shrink-0 ${GROUP_BADGE_CLASS[g]}`}>
                    {t(CAR_GROUP_LABEL_KEYS[g])}
                  </Badge>
                  <Award size={12} className="text-muted-foreground shrink-0" />
                  <div className="flex gap-1 flex-wrap">
                    {LICENSE_CLASSES.map((lic) => (
                      <button
                        key={lic}
                        onClick={() => toggleCategoryLicense(g, lic)}
                        className={`rounded-md px-2 py-0.5 text-xs font-medium transition-colors border ${
                          (licenseByCategory[g] ?? []).includes(lic)
                            ? LICENSE_BADGE_CLASS[lic]
                            : 'border-border/50 text-muted-foreground hover:bg-accent'
                        }`}
                      >
                        {lic}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Specific type chips */}
          {allTypes.length > 1 && (
            <div className="flex flex-wrap gap-1.5 pl-5">
              {allTypes.map((t) => (
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
              {t('seriesCalendar.noResults')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
