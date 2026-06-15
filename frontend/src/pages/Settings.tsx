import { useRef, useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/api/client';
import { Upload, CheckCircle2, XCircle, RefreshCw, FileText, Loader2, Car, MapPin, Search, Database, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

// ──────────────────────────────────────────────────────────────────────────────

interface ParsedSeries {
  series_name: string;
  season: string;
  car_names: string[];
  car_type: string;
  car_class_ids: number[];
  license_class: string;
  tracks: { raw: string; track_id: number | null; name: string | null; owned: boolean }[];
  matched_count: number;
  total_tracks: number;
  likely_weekly_guide: boolean;
}

// ──────────────────────────────────────────────────────────────────────────────

function StatusBadge({ ok }: { ok: boolean }) {
  return ok
    ? <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
    : <XCircle size={13} className="text-amber-400 shrink-0" />;
}

function ParsedSeriesCard({
  s,
  checked,
  onToggle,
}: {
  s: ParsedSeries;
  checked: boolean;
  onToggle: () => void;
}) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);
  const matchPct = s.total_tracks > 0 ? Math.round((s.matched_count / s.total_tracks) * 100) : 0;

  return (
    <div className={cn(
      'rounded-lg border transition-colors',
      checked ? 'border-primary/40 bg-primary/5' : 'border-border bg-card'
    )}>
      <div className="flex items-center gap-3 px-3 py-2.5">
        <input
          type="checkbox"
          checked={checked}
          onChange={onToggle}
          className="h-4 w-4 rounded border-border accent-primary"
        />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate flex items-center gap-1.5">
            {s.series_name}
            {s.likely_weekly_guide && (
              <span title={t('settings.likelyWeeklyGuideBadge')}>
                <AlertTriangle size={13} className="text-amber-400 shrink-0" />
              </span>
            )}
          </p>
          <p className="text-xs text-muted-foreground">
            {s.car_names.join(', ')} · {s.license_class}
            {s.car_type && <span className="ml-1 text-foreground/70">{t('settings.carClass', { type: s.car_type })}</span>}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className={cn(
            'text-xs font-medium px-1.5 py-0.5 rounded',
            matchPct === 100 ? 'bg-emerald-500/20 text-emerald-400' :
            matchPct >= 50  ? 'bg-amber-500/20 text-amber-400' :
                              'bg-red-500/20 text-red-400'
          )}>
            {t('settings.tracksMatched', { matched: s.matched_count, total: s.total_tracks })}
          </span>
          <button
            onClick={() => setExpanded((v) => !v)}
            className="text-xs text-muted-foreground hover:text-foreground px-1"
          >
            {expanded ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-border px-3 py-2 space-y-0.5">
          {s.tracks.map((tr, i) => (
            <div key={i} className="flex items-center gap-1.5 text-xs">
              <StatusBadge ok={tr.track_id !== null} />
              <span className={tr.track_id !== null ? 'text-foreground' : 'text-muted-foreground'}>
                {tr.track_id !== null ? tr.name : tr.raw}
              </span>
              {tr.track_id !== null && tr.owned && (
                <span className="text-emerald-400 text-[10px]">{t('settings.ownedTrack')}</span>
              )}
              {tr.track_id === null && (
                <span className="text-amber-400 text-[10px]">{t('settings.noMatch')}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────
// Manual ownership panel (cars or tracks)
// ──────────────────────────────────────────────────────────────────────────────

function OwnershipPanel({
  type,
  items,
  ownedIds,
  onToggle,
}: {
  type: 'car' | 'track';
  items: any[];
  ownedIds: Set<number>;
  onToggle: (id: number, owned: boolean) => void;
}) {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const idKey = type === 'car' ? 'car_id' : 'track_id';

  const filtered = items.filter((it) =>
    it.name.toLowerCase().includes(search.toLowerCase())
  );

  const ownedCount = items.filter((it) => ownedIds.has(it[idKey]) || it.owned).length;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('settings.searchPlaceholder')}
            className="w-full pl-7 pr-3 py-1.5 text-xs bg-background border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <span className="text-xs text-muted-foreground whitespace-nowrap">
          {t('settings.ownedOf', { owned: ownedCount, total: items.length })}
        </span>
      </div>

      <div className="max-h-72 overflow-y-auto space-y-0.5 pr-1">
        {filtered.map((it) => {
          const id = it[idKey];
          const isOwned = ownedIds.has(id) || it.owned;
          return (
            <label
              key={id}
              className={cn(
                'flex items-center gap-2.5 rounded-lg px-3 py-2 cursor-pointer transition-colors',
                isOwned ? 'bg-emerald-500/8 hover:bg-emerald-500/12' : 'hover:bg-accent'
              )}
            >
              <input
                type="checkbox"
                checked={isOwned}
                onChange={() => onToggle(id, !isOwned)}
                className="h-3.5 w-3.5 rounded border-border accent-emerald-500"
              />
              <span className={cn('text-xs flex-1', isOwned ? 'text-foreground' : 'text-muted-foreground')}>
                {it.name}
              </span>
              {it.price > 0 && !isOwned && (
                <span className="text-xs text-muted-foreground">${it.price.toFixed(2)}</span>
              )}
              {type === 'track' && it.country && (
                <span className="text-[10px] text-muted-foreground">{it.country}</span>
              )}
            </label>
          );
        })}
        {filtered.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-4">{t('settings.noResults')}</p>
        )}
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────────────────────

export function Settings() {
  const { t } = useTranslation();
  const fileRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [parsed, setParsed] = useState<ParsedSeries[] | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [replaceExisting, setReplaceExisting] = useState(false);
  const [skipWeekly, setSkipWeekly] = useState(true);
  const [pdfWarning, setPdfWarning] = useState<string | null>(null);

  // Manual ownership state
  const [allCars, setAllCars] = useState<any[]>([]);
  const [allTracks, setAllTracks] = useState<any[]>([]);
  const [ownedCarIds, setOwnedCarIds] = useState<Set<number>>(new Set());
  const [ownedTrackIds, setOwnedTrackIds] = useState<Set<number>>(new Set());
  const [ownedLoading, setOwnedLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  const loadOwnership = useCallback(async () => {
    setOwnedLoading(true);
    try {
      const [carsRes, tracksRes, ownedRes] = await Promise.all([
        api.cars.all(),
        api.tracks.all(),
        api.owned.get(),
      ]);
      setAllCars((carsRes as any) ?? []);
      setAllTracks((tracksRes as any) ?? []);
      setOwnedCarIds(new Set((ownedRes as any).cars ?? []));
      setOwnedTrackIds(new Set((ownedRes as any).tracks ?? []));
    } catch {
      // silent
    }
    setOwnedLoading(false);
  }, []);

  useEffect(() => { loadOwnership(); }, [loadOwnership]);

  const toggleCar = async (id: number, owned: boolean) => {
    setOwnedCarIds((prev) => {
      const next = new Set(prev);
      if (owned) { next.add(id); } else { next.delete(id); }
      return next;
    });
    await api.owned.setCar(id, owned);
  };

  const toggleTrack = async (id: number, owned: boolean) => {
    setOwnedTrackIds((prev) => {
      const next = new Set(prev);
      if (owned) { next.add(id); } else { next.delete(id); }
      return next;
    });
    await api.owned.setTrack(id, owned);
  };

  // PDF upload logic
  const uploadFile = async (file: File) => {
    if (!file.name.endsWith('.pdf')) {
      setError(t('settings.onlyPdf'));
      return;
    }
    setLoading(true);
    setError(null);
    setParsed(null);
    setImportResult(null);
    setPdfWarning(null);

    const form = new FormData();
    form.append('file', file);
    form.append('skip_weekly', String(skipWeekly));

    try {
      const res = await fetch('/api/series/import-pdf', { method: 'POST', body: form });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const json = await res.json();
      const data: ParsedSeries[] = json.data ?? [];
      setParsed(data);
      setSelected(new Set(data.map((_, i) => i)));
      setPdfWarning(json.warning_type ?? null);
    } catch (e: any) {
      setError(e.message ?? t('settings.pdfError'));
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
    e.target.value = '';
  };

  const handleImport = async () => {
    if (!parsed) return;
    const toImport = parsed.filter((_, i) => selected.has(i));
    setImporting(true);
    setImportResult(null);
    try {
      const res = await fetch('/api/series/import-confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ series: toImport, replace_existing: replaceExisting }),
      });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const json = await res.json();
      setImportResult(t('settings.importSuccess', { count: json.imported }));
    } catch (e: any) {
      setImportResult(t('settings.syncError', { error: e.message }));
    } finally {
      setImporting(false);
    }
  };

  const handleCatalogSync = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const res = await fetch('/api/catalog/sync', { method: 'POST' });
      const json = await res.json();
      if (json.ok) {
        setSyncResult(t('settings.syncSuccess', { cars: json.cars, tracks: json.tracks }));
        await loadOwnership();
      } else {
        setSyncResult(t('settings.syncFail', { error: json.error ?? t('settings.syncFailUnknown') }));
      }
    } catch (e: any) {
      setSyncResult(t('settings.syncError', { error: e.message ?? t('settings.syncErrorDefault') }));
    }
    setSyncing(false);
  };

  const handleSeedDefault = async () => {
    setImporting(true);
    try {
      await api.series.seed();
      setImportResult(t('settings.resetSuccess'));
    } catch {
      setImportResult(t('settings.resetError'));
    }
    setImporting(false);
  };

  return (
    <div className="space-y-6 p-6 max-w-3xl">
      <div>
        <h1 className="text-xl font-semibold">{t('settings.title')}</h1>
        <p className="text-sm text-muted-foreground">{t('settings.subtitle')}</p>
      </div>

      {/* ── Manual Car Ownership ────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Car size={16} />
            {t('settings.carsInGarage')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {ownedLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground py-4">
              <Loader2 size={14} className="animate-spin" />
              {t('settings.loading')}
            </div>
          ) : (
            <>
              <p className="text-sm text-muted-foreground mb-3">
                {t('settings.carsInGarageDesc')}
              </p>
              <OwnershipPanel
                type="car"
                items={allCars}
                ownedIds={ownedCarIds}
                onToggle={toggleCar}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* ── Manual Track Ownership ───────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <MapPin size={16} />
            {t('settings.tracksIHave')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {ownedLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground py-4">
              <Loader2 size={14} className="animate-spin" />
              {t('settings.loading')}
            </div>
          ) : (
            <>
              <p className="text-sm text-muted-foreground mb-3">
                {t('settings.tracksIHaveDesc')}
              </p>
              <OwnershipPanel
                type="track"
                items={allTracks}
                ownedIds={ownedTrackIds}
                onToggle={toggleTrack}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* ── PDF Import ─────────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <FileText size={16} />
            {t('settings.importTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {t('settings.importDesc')}
          </p>

          <label className="flex items-start gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={skipWeekly}
              onChange={(e) => setSkipWeekly(e.target.checked)}
              className="mt-0.5"
            />
            <span className="text-sm">
              {t('settings.skipWeekly')}
              <span className="block text-xs text-muted-foreground">{t('settings.skipWeeklyHint')}</span>
            </span>
          </label>

          {/* Drop zone */}
          <div
            className={cn(
              'flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed py-10 cursor-pointer transition-colors',
              dragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/30'
            )}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
          >
            {loading ? (
              <Loader2 size={28} className="animate-spin text-primary" />
            ) : (
              <Upload size={28} className="text-muted-foreground" />
            )}
            <div className="text-center">
              <p className="text-sm font-medium">
                {loading ? t('settings.processingPdf') : t('settings.dropHint')}
              </p>
              <p className="text-xs text-muted-foreground">{t('settings.dropFile')}</p>
            </div>
          </div>
          <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={handleFileChange} />

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          {/* Results */}
          {parsed && (
            <div className="space-y-3">
              {pdfWarning === 'likely_weekly_guide' && (
                <div className="flex gap-2 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2.5">
                  <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-amber-400">{t('settings.weeklyGuideWarningTitle')}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{t('settings.weeklyGuideWarningBody')}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">
                  {t('settings.seriesFound', { count: parsed.length })}
                  <span className="ml-2 text-muted-foreground font-normal">
                    {t('settings.seriesSelected', { count: parsed.filter((_, i) => selected.has(i)).length })}
                  </span>
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelected(new Set(parsed.map((_, i) => i)))}
                    className="text-xs text-primary hover:underline"
                  >{t('settings.selectAll')}</button>
                  <span className="text-muted-foreground text-xs">·</span>
                  <button
                    onClick={() => setSelected(new Set())}
                    className="text-xs text-muted-foreground hover:underline"
                  >{t('settings.selectNone')}</button>
                </div>
              </div>

              <div className="space-y-1.5 max-h-96 overflow-y-auto pr-1">
                {parsed.map((s, i) => (
                  <ParsedSeriesCard
                    key={i}
                    s={s}
                    checked={selected.has(i)}
                    onToggle={() => setSelected((prev) => {
                      const next = new Set(prev);
                      if (next.has(i)) { next.delete(i); } else { next.add(i); }
                      return next;
                    })}
                  />
                ))}
              </div>

              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={replaceExisting}
                  onChange={(e) => setReplaceExisting(e.target.checked)}
                  className="mt-0.5"
                />
                <span className="text-sm">
                  {t('settings.replaceExisting')}
                  <span className="block text-xs text-muted-foreground">{t('settings.replaceExistingHint')}</span>
                </span>
              </label>

              <button
                onClick={handleImport}
                disabled={importing || selected.size === 0}
                className="w-full rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {importing ? t('settings.importing') : t('settings.importButton', { count: selected.size })}
              </button>
            </div>
          )}

          {importResult && (
            <p className="text-sm font-medium">{importResult}</p>
          )}
        </CardContent>
      </Card>

      {/* ── Catalog Sync ──────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Database size={16} />
            {t('settings.syncTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {t('settings.syncDesc')}
          </p>
          <button
            onClick={handleCatalogSync}
            disabled={syncing}
            className="rounded-lg border border-border px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:border-primary/40 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {syncing ? <Loader2 size={14} className="animate-spin" /> : <Database size={14} />}
            {syncing ? t('settings.syncing') : t('settings.syncNow')}
          </button>
          {syncResult && <p className="text-sm font-medium">{syncResult}</p>}
        </CardContent>
      </Card>

      {/* ── Reset a defaults ──────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <RefreshCw size={16} />
            {t('settings.resetTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {t('settings.resetDesc')}
          </p>
          <button
            onClick={handleSeedDefault}
            disabled={importing}
            className="rounded-lg border border-border px-4 py-2 text-sm text-muted-foreground hover:text-foreground hover:border-primary/40 disabled:opacity-50 transition-colors"
          >
            {importing ? t('settings.resetting') : t('settings.resetButton')}
          </button>
          {importResult && <p className="text-sm font-medium">{importResult}</p>}
        </CardContent>
      </Card>
    </div>
  );
}
