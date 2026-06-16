import { useEffect, useState, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import {
  ShoppingCart, CheckCircle2, XCircle,
  RefreshCw, Trash2, DollarSign
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { CAR_GROUP_LABEL_KEYS, CAR_GROUP_ORDER, getCarGroupKey, type CarGroupKey, LICENSE_CLASSES, LICENSE_BADGE_CLASS } from '@/lib/carGroups';
import { Search, Award, Tag } from 'lucide-react';

const GROUP_BADGE_CLASS: Record<CarGroupKey, string> = {
  formula: 'bg-orange-500/20 text-orange-400 border border-orange-500/30',
  gt_sport: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
  oval_nascar: 'bg-red-500/10 text-red-400 border border-red-500/20',
  dirt: 'bg-amber-700/15 text-amber-500 border border-amber-700/30',
  rallycross: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
  other: 'bg-muted text-muted-foreground border border-border',
};

// ──────────────────────────────────────────────────────────────────────────────

interface SeriesOption {
  series_id: number;
  series_name: string;
  car_type: string;
  license_class: string;
}

interface TrackOverlap {
  track_id: number;
  name: string;
  country: string;
  price: number;
  owned: boolean;
  series_count: number;
  used_by: { series_id: number; series_name: string; car_type: string }[];
}

interface WishlistSummary {
  tracks: { track_id: number; name: string; price: number; country: string }[];
  cars: { car_id: number; name: string; price: number }[];
  total_cost: number;
  total_items: number;
}

// ──────────────────────────────────────────────────────────────────────────────

function FlagEmoji({ country }: { country: string }) {
  const map: Record<string, string> = {
    Belgium: '🇧🇪', Italy: '🇮🇹', UK: '🇬🇧', USA: '🇺🇸', Japan: '🇯🇵',
    Germany: '🇩🇪', France: '🇫🇷', Spain: '🇪🇸', Australia: '🇦🇺',
    Netherlands: '🇳🇱', Canada: '🇨🇦', Austria: '🇦🇹', Mexico: '🇲🇽',
    Hungary: '🇭🇺', Portugal: '🇵🇹', Norway: '🇳🇴', Brazil: '🇧🇷',
  };
  return <span title={country}>{map[country] ?? '🏁'}</span>;
}

function SeriesTag({ name, carType }: { name: string; carType: string }) {
  const isGT3 = carType.includes('GT3');
  const isGT4 = carType.includes('GT4');
  const isMX5 = carType.includes('MX-5');
  const isCup = carType.includes('Cup') || carType.includes('Spec');
  return (
    <span className={cn(
      'inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium',
      isGT3 ? 'bg-red-500/20 text-red-400' :
      isGT4 ? 'bg-blue-500/20 text-blue-400' :
      isMX5 ? 'bg-amber-500/20 text-amber-400' :
      isCup ? 'bg-purple-500/20 text-purple-400' :
              'bg-muted text-muted-foreground'
    )}>
      {name.length > 22 ? name.slice(0, 22) + '…' : name}
    </span>
  );
}

// ──────────────────────────────────────────────────────────────────────────────

export function Overlap() {
  const { t } = useTranslation();
  const [allSeries, setAllSeries] = useState<SeriesOption[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<CarGroupKey[]>([]);
  const [licenseByCategory, setLicenseByCategory] = useState<Partial<Record<CarGroupKey, string[]>>>({});
  const [carTypeByCategory, setCarTypeByCategory] = useState<Partial<Record<CarGroupKey, string[]>>>({});
  const [seriesSearch, setSeriesSearch] = useState('');
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [tracks, setTracks] = useState<TrackOverlap[]>([]);
  const [wishlist, setWishlist] = useState<Set<number>>(new Set());
  const [summary, setSummary] = useState<WishlistSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [showOwned, setShowOwned] = useState(false);
  const [currentWeek, setCurrentWeek] = useState<number | null>(null);

  // Load current race week
  useEffect(() => {
    api.settings.getCurrentWeek().then((d) => setCurrentWeek(d.current_week));
  }, []);

  const toggleCategory = (g: CarGroupKey) => setCategoryFilter((prev) =>
    prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]
  );
  const toggleCategoryLicense = (g: CarGroupKey, lic: string) => setLicenseByCategory((prev) => {
    const current = prev[g] ?? [];
    return { ...prev, [g]: current.includes(lic) ? current.filter((x) => x !== lic) : [...current, lic] };
  });
  const toggleCategoryCarType = (g: CarGroupKey, ct: string) => setCarTypeByCategory((prev) => {
    const current = prev[g] ?? [];
    return { ...prev, [g]: current.includes(ct) ? current.filter((x) => x !== ct) : [...current, ct] };
  });

  const sq = seriesSearch.trim().toLowerCase();

  // Car_types disponibles por categoría (para mostrar los botones del subfiltro)
  const carTypesByCategory = useMemo(() => {
    const result: Partial<Record<CarGroupKey, string[]>> = {};
    for (const s of allSeries) {
      const cat = getCarGroupKey(s.car_type, s.series_name);
      if (!result[cat]) result[cat] = [];
      if (!result[cat]!.includes(s.car_type)) result[cat]!.push(s.car_type);
    }
    for (const key of Object.keys(result) as CarGroupKey[]) {
      result[key] = result[key]!.sort();
    }
    return result;
  }, [allSeries]);

  // Series que entran al análisis de overlap según categoría/licencia/car_type (sin búsqueda).
  // La búsqueda solo filtra los chips visibles, no el análisis.
  const filteredForOverlap = useMemo(() => allSeries.filter((s) => {
    if (categoryFilter.length === 0) return true;
    const cat = getCarGroupKey(s.car_type, s.series_name);
    if (!categoryFilter.includes(cat)) return false;
    const lics = licenseByCategory[cat];
    if (lics && lics.length > 0 && !lics.includes(s.license_class)) return false;
    const carTypes = carTypeByCategory[cat];
    if (carTypes && carTypes.length > 0 && !carTypes.includes(s.car_type)) return false;
    return true;
  }), [allSeries, categoryFilter, licenseByCategory, carTypeByCategory]);

  // Lo que se muestra en los chips: filteredForOverlap + búsqueda de texto
  const seriesOptions = useMemo(() =>
    filteredForOverlap.filter((s) =>
      !sq || s.series_name.toLowerCase().includes(sq) || s.car_type.toLowerCase().includes(sq)
    ),
  [filteredForOverlap, sq]);

  // Load series options
  useEffect(() => {
    api.series.all().then((data: any[]) => {
      const mapped = data.map((s) => ({
        series_id: s.series_id,
        series_name: s.series_name,
        car_type: s.car_type,
        license_class: s.license_class ?? '',
      }));
      setAllSeries(mapped);
      setSelected(new Set(mapped.map((s) => s.series_id)));
    });
  }, []);

  // Load wishlist
  const loadWishlist = useCallback(async () => {
    const wl = await api.wishlist.get();
    setWishlist(new Set(wl.tracks));
    const sum = await api.wishlist.summary();
    setSummary(sum);
  }, []);

  useEffect(() => { loadWishlist(); }, [loadWishlist]);

  // Load overlap data: solo las series que coinciden con el filtro activo Y están seleccionadas
  const loadOverlap = useCallback(async () => {
    setLoading(true);
    const filteredIds = new Set(filteredForOverlap.map((s) => s.series_id));
    const ids = [...selected].filter((id) => filteredIds.has(id));
    const data = await api.overlap.get(ids);
    setTracks(data);
    setLoading(false);
  }, [selected, filteredForOverlap]);

  useEffect(() => { loadOverlap(); }, [loadOverlap]);

  const updateCurrentWeek = async (week: number) => {
    if (week < 1) return;
    setCurrentWeek(week);
    await api.settings.setCurrentWeek(week);
    loadOverlap();
  };

  const toggleSeries = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) { next.delete(id); } else { next.add(id); }
      return next;
    });
  };

  const toggleWishlist = async (trackId: number) => {
    if (wishlist.has(trackId)) {
      await api.wishlist.removeTrack(trackId);
    } else {
      await api.wishlist.addTrack(trackId);
    }
    loadWishlist();
  };

  const clearWishlist = async () => {
    await api.wishlist.clear();
    loadWishlist();
  };

  const displayed = tracks.filter((t) => showOwned || !t.owned);

  const maxCount = Math.max(1, ...tracks.map((t) => t.series_count));

  return (
    <div className="flex gap-5 p-6 h-full">
      {/* Left: controls + track list */}
      <div className="flex-1 min-w-0 space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">{t('overlap.title')}</h1>
            <p className="text-sm text-muted-foreground">
              {t('overlap.subtitle')}
            </p>
          </div>
          <button
            onClick={loadOverlap}
            className="flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <RefreshCw size={13} />
            {t('overlap.refresh')}
          </button>
        </div>

        {/* Current week control */}
        <div className="flex items-center justify-between gap-4 rounded-lg border border-border bg-card px-4 py-3">
          <div className="min-w-0">
            <p className="text-sm font-medium">{t('overlap.currentWeekTitle')}</p>
            <p className="text-xs text-muted-foreground">
              {t('overlap.currentWeekDesc')}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => currentWeek != null && updateCurrentWeek(currentWeek - 1)}
              disabled={currentWeek == null || currentWeek <= 1}
              className="flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground hover:text-foreground disabled:opacity-40 transition-colors"
            >
              −
            </button>
            <span className="w-8 text-center text-sm font-semibold tabular-nums">
              {currentWeek ?? '—'}
            </span>
            <button
              onClick={() => currentWeek != null && updateCurrentWeek(currentWeek + 1)}
              disabled={currentWeek == null}
              className="flex h-7 w-7 items-center justify-center rounded-md border border-border text-muted-foreground hover:text-foreground disabled:opacity-40 transition-colors"
            >
              +
            </button>
          </div>
        </div>

        {/* Series filter */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between gap-2">
              <CardTitle className="text-sm font-medium shrink-0">
                {t('overlap.seriesIncluded')} <span className="text-muted-foreground font-normal">{t('overlap.seriesSelected', { count: selected.size })}</span>
              </CardTitle>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input
                    value={seriesSearch}
                    onChange={(e) => setSeriesSearch(e.target.value)}
                    placeholder={t('overlap.searchSeriesPlaceholder')}
                    className="h-7 w-40 rounded-md border border-border bg-transparent pl-7 pr-2 text-xs outline-none focus:border-primary/50"
                  />
                </div>
                <button
                  onClick={() => setSelected((prev) => new Set([...prev, ...seriesOptions.map((s) => s.series_id)]))}
                  className="text-xs text-primary hover:underline shrink-0"
                >{t('overlap.selectAll')}</button>
                <span className="text-muted-foreground text-xs">·</span>
                <button
                  onClick={() => setSelected((prev) => {
                    const next = new Set(prev);
                    seriesOptions.forEach((s) => next.delete(s.series_id));
                    return next;
                  })}
                  className="text-xs text-muted-foreground hover:underline shrink-0"
                >{t('overlap.selectNone')}</button>
              </div>
            </div>
            <div className="flex gap-1.5 flex-wrap pt-1">
              {/* Car category filter (multiselección) */}
              <button
                onClick={() => { setCategoryFilter([]); setLicenseByCategory({}); setCarTypeByCategory({}); }}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors border ${
                  categoryFilter.length === 0
                    ? 'bg-primary text-primary-foreground'
                    : 'border-border/50 text-muted-foreground hover:bg-accent'
                }`}
              >
                {t('overlap.filterAll')}
              </button>
              {CAR_GROUP_ORDER.map((g) => (
                <button
                  key={g}
                  onClick={() => toggleCategory(g)}
                  className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors border ${
                    categoryFilter.includes(g)
                      ? GROUP_BADGE_CLASS[g]
                      : 'border-border/50 text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {t(CAR_GROUP_LABEL_KEYS[g])}
                </button>
              ))}
            </div>
            {/* Subfiltro de licencia + car_type por cada categoría seleccionada */}
            {categoryFilter.length > 0 && (
              <div className="space-y-1.5 pt-1.5">
                {categoryFilter.map((g) => (
                  <div key={g} className="space-y-1">
                    {/* Fila licencia */}
                    <div className="flex items-center gap-1.5 flex-wrap">
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
                    {/* Fila car_type (solo si hay más de 1 tipo en la categoría) */}
                    {(carTypesByCategory[g] ?? []).length > 1 && (
                      <div className="flex items-center gap-1.5 flex-wrap pl-1">
                        <Tag size={11} className="text-muted-foreground shrink-0" />
                        <div className="flex gap-1 flex-wrap">
                          {(carTypesByCategory[g] ?? []).map((ct) => (
                            <button
                              key={ct}
                              onClick={() => toggleCategoryCarType(g, ct)}
                              className={`rounded-md px-2 py-0.5 text-xs font-medium transition-colors border ${
                                (carTypeByCategory[g] ?? []).includes(ct)
                                  ? 'bg-primary/15 text-primary border-primary/30'
                                  : 'border-border/50 text-muted-foreground hover:bg-accent'
                              }`}
                            >
                              {ct}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1.5">
              {seriesOptions.map((s) => (
                <button
                  key={s.series_id}
                  onClick={() => toggleSeries(s.series_id)}
                  className={cn(
                    'rounded-lg border px-2.5 py-1 text-xs transition-colors',
                    selected.has(s.series_id)
                      ? 'border-primary/50 bg-primary/10 text-primary font-medium'
                      : 'border-border text-muted-foreground hover:border-primary/30'
                  )}
                >
                  {s.series_name.replace(/ by .+/, '').replace(/ Fixed/, '').replace(/ Challenge/, '')}
                  <span className="ml-1 opacity-60">{s.license_class}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Toggle owned */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowOwned((v) => !v)}
            className={cn(
              'rounded-lg border px-3 py-1.5 text-xs transition-colors',
              showOwned
                ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400'
                : 'border-border text-muted-foreground hover:border-primary/30'
            )}
          >
            {showOwned ? t('overlap.showingAll') : t('overlap.onlyToBuy')}
          </button>
          <span className="text-xs text-muted-foreground">
            {t('overlap.tracksToBuy', { count: displayed.filter((tr) => !tr.owned).length })}
            {displayed.filter((tr) => tr.owned).length > 0 && !showOwned ? '' :
              showOwned ? ` ${t('overlap.alreadyOwned', { count: displayed.filter((tr) => tr.owned).length })}` : ''}
          </span>
        </div>

        {/* Track list */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : (
          <div className="space-y-2">
            {displayed.map((track) => {
              const inWishlist = wishlist.has(track.track_id);
              const barWidth = Math.round((track.series_count / maxCount) * 100);
              return (
                <Card key={track.track_id} className={cn(
                  'transition-colors',
                  track.owned ? 'border-emerald-800/40 bg-emerald-950/10' : ''
                )}>
                  <CardContent className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      {/* Series count bar */}
                      <div className="w-8 shrink-0 text-center">
                        <span className={cn(
                          'text-lg font-bold',
                          track.series_count >= 3 ? 'text-amber-400' :
                          track.series_count === 2 ? 'text-blue-400' : 'text-muted-foreground'
                        )}>
                          {track.series_count}
                        </span>
                        <p className="text-[9px] text-muted-foreground leading-none">{t('overlap.seriesUnit')}</p>
                      </div>

                      {/* Main info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <FlagEmoji country={track.country} />
                          <span className="text-sm font-medium truncate">{track.name}</span>
                          {track.owned ? (
                            <span className="flex items-center gap-0.5 text-[10px] text-emerald-400 font-medium">
                              <CheckCircle2 size={10} /> {t('overlap.owned')}
                            </span>
                          ) : track.price === 0 ? (
                            <span className="text-[10px] text-blue-400">{t('overlap.free')}</span>
                          ) : (
                            <span className="text-[10px] text-muted-foreground">${track.price.toFixed(2)}</span>
                          )}
                        </div>
                        {/* Progress bar */}
                        <div className="mt-1.5 h-1 rounded-full bg-muted overflow-hidden w-full max-w-48">
                          <div
                            className={cn(
                              'h-full rounded-full transition-all',
                              track.owned ? 'bg-emerald-500' :
                              track.series_count >= 3 ? 'bg-amber-400' : 'bg-blue-400'
                            )}
                            style={{ width: `${barWidth}%` }}
                          />
                        </div>
                        {/* Series tags */}
                        <div className="mt-1.5 flex flex-wrap gap-1">
                          {track.used_by.map((s) => (
                            <SeriesTag key={s.series_id} name={s.series_name} carType={s.car_type} />
                          ))}
                        </div>
                      </div>

                      {/* Actions */}
                      {!track.owned && (
                        <button
                          onClick={() => toggleWishlist(track.track_id)}
                          className={cn(
                            'shrink-0 flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs transition-colors',
                            inWishlist
                              ? 'border-primary/50 bg-primary/10 text-primary'
                              : 'border-border text-muted-foreground hover:border-primary/30 hover:text-foreground'
                          )}
                        >
                          <ShoppingCart size={11} />
                          {inWishlist ? t('overlap.inList') : t('overlap.addToList')}
                        </button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
            {displayed.length === 0 && (
              <Card>
                <CardContent className="py-10 text-center text-sm text-muted-foreground">
                  {selected.size === 0
                    ? t('overlap.selectAtLeastOne')
                    : t('overlap.noTracksPending')}
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Right: Wishlist sidebar */}
      <div className="w-64 shrink-0">
        <Card className="sticky top-0">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <ShoppingCart size={14} />
                {t('overlap.wishlistTitle')}
              </CardTitle>
              {(summary?.total_items ?? 0) > 0 && (
                <button
                  onClick={clearWishlist}
                  className="text-xs text-muted-foreground hover:text-destructive transition-colors"
                  title={t('overlap.clearList')}
                >
                  <Trash2 size={12} />
                </button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {!summary || summary.total_items === 0 ? (
              <p className="text-xs text-muted-foreground text-center py-4">
                {t('overlap.addTracksHint')}
              </p>
            ) : (
              <>
                {/* Tracks */}
                {summary.tracks.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wide font-medium">
                      {t('overlap.tracksLabel', { count: summary.tracks.length })}
                    </p>
                    {summary.tracks.map((track) => (
                      <div key={track.track_id} className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <FlagEmoji country={track.country} />
                          <span className="text-xs truncate">{track.name}</span>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <span className="text-xs text-muted-foreground">
                            {track.price === 0 ? t('overlap.free') : `$${track.price.toFixed(2)}`}
                          </span>
                          <button
                            onClick={() => toggleWishlist(track.track_id)}
                            className="text-muted-foreground hover:text-destructive transition-colors"
                          >
                            <XCircle size={12} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Cars */}
                {summary.cars.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wide font-medium">
                      {t('overlap.carsLabel', { count: summary.cars.length })}
                    </p>
                    {summary.cars.map((c) => (
                      <div key={c.car_id} className="flex items-center justify-between gap-2">
                        <span className="text-xs truncate">{c.name}</span>
                        <span className="text-xs text-muted-foreground shrink-0">${c.price.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Total */}
                <div className="border-t border-border pt-2 flex items-center justify-between">
                  <span className="text-sm font-medium flex items-center gap-1">
                    <DollarSign size={12} /> {t('overlap.total')}
                  </span>
                  <span className="text-sm font-bold text-primary">
                    ${summary.total_cost.toFixed(2)}
                  </span>
                </div>

                {/* Series coverage hint */}
                {summary.tracks.length > 0 && (
                  <div className="rounded-lg bg-muted/50 p-2">
                    <p className="text-[10px] text-muted-foreground leading-relaxed">
                      {t('overlap.coverageHint')}
                    </p>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
