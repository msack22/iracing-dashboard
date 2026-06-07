import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { api } from '@/api/client';
import { MapPin, Check, Plus, Filter, Search } from 'lucide-react';

function TrackCard({ track, onToggle }: { track: any; onToggle: (id: number, owned: boolean) => void }) {
  const { t } = useTranslation();
  return (
    <Card className={`overflow-hidden transition-all ${track.owned ? 'border-emerald-500/30' : 'border-border hover:border-primary/40'}`}>
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="font-medium text-sm leading-tight">{track.name}</p>
            <p className="text-xs text-muted-foreground">{track.city}, {track.country}</p>
          </div>
          <Badge variant={track.price === 0 ? 'secondary' : 'outline'} className="shrink-0">
            {track.price === 0 ? t('tracks.free') : `$${track.price}`}
          </Badge>
        </div>
        <div className="space-y-1">
          {track.configs.map((cfg: any) => (
            <div key={cfg.track_id} className="flex items-center gap-2 text-xs">
              <div className={`h-1.5 w-1.5 rounded-full shrink-0 ${cfg.owned || track.owned ? 'bg-emerald-400' : 'bg-muted-foreground/30'}`} />
              <span className={cfg.owned || track.owned ? 'text-foreground' : 'text-muted-foreground'}>
                {cfg.config_name}
              </span>
            </div>
          ))}
        </div>
        <button
          onClick={() => onToggle(track.track_id, !track.owned)}
          className={`flex w-full items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-colors ${
            track.owned
              ? 'bg-emerald-500/15 text-emerald-400 hover:bg-red-500/15 hover:text-red-400'
              : 'bg-muted text-muted-foreground hover:bg-emerald-500/15 hover:text-emerald-400'
          }`}
        >
          {track.owned ? <Check size={11} /> : <Plus size={11} />}
          {track.owned ? t('tracks.owned') : t('tracks.markAsOwned')}
        </button>
      </CardContent>
    </Card>
  );
}

export function Tracks() {
  const { t } = useTranslation();
  const [tracks, setTracks] = useState<any[]>([]);
  const [showAll, setShowAll] = useState(false);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadTracks = useCallback(async () => {
    const [allTracks, ownedData] = await Promise.all([
      api.tracks.all(false),
      api.owned.get(),
    ]);
    const ownedSet = new Set(ownedData.tracks);
    setTracks(allTracks.map((t: any) => ({
      ...t,
      owned: t.owned || ownedSet.has(t.track_id),
    })));
    setLoading(false);
  }, []);

  useEffect(() => { loadTracks(); }, [loadTracks]);

  const handleToggle = async (trackId: number, owned: boolean) => {
    await api.owned.setTrack(trackId, owned);
    setTracks((prev) => prev.map((t) =>
      t.track_id === trackId
        ? { ...t, owned, configs: t.configs.map((c: any) => ({ ...c, owned })) }
        : t
    ));
  };

  const q = search.trim().toLowerCase();
  const visible = (showAll ? tracks : tracks.filter((t) => t.owned))
    .filter((t) => !q || t.name.toLowerCase().includes(q) || t.city?.toLowerCase().includes(q) || t.country?.toLowerCase().includes(q));
  const ownedCount = tracks.filter((t) => t.owned).length;

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">{t('tracks.title')}</h1>
          <p className="text-sm text-muted-foreground">{t('tracks.subtitle', { owned: ownedCount, total: tracks.length })}</p>
        </div>
        <MapPin size={20} className="text-muted-foreground" />
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <p className="text-xs text-muted-foreground bg-muted/40 rounded-lg px-3 py-2 flex-1 min-w-[200px]">
          {t('tracks.infoBanner')}
        </p>
        <div className="relative shrink-0 w-full sm:w-56">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('tracks.searchPlaceholder')}
            className="h-8 pl-8 text-xs"
          />
        </div>
        <button
          onClick={() => setShowAll((v) => !v)}
          className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors shrink-0 ${
            showAll ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground hover:bg-accent'
          }`}
        >
          <Filter size={12} />
          {showAll ? t('tracks.showOwned') : t('tracks.showAll')}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {visible.map((track) => (
            <TrackCard key={track.track_id} track={track} onToggle={handleToggle} />
          ))}
          {visible.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
              {q
                ? t('tracks.noResultsFor', { query: search })
                : showAll ? t('tracks.none') : t('tracks.noneOwned')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
