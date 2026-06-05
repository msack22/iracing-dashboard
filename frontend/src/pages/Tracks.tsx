import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { MapPin } from 'lucide-react';

function TrackCard({ track }: { track: any }) {
  return (
    <Card className="overflow-hidden transition-all hover:border-primary/40">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="font-medium text-sm leading-tight">{track.name}</p>
            <p className="text-xs text-muted-foreground">{track.city}, {track.country}</p>
          </div>
          <Badge variant={track.price === 0 ? 'secondary' : 'outline'} className="shrink-0">
            {track.price === 0 ? 'Gratis' : `$${track.price}`}
          </Badge>
        </div>
        <div className="space-y-1">
          {track.configs.map((cfg: any) => (
            <div key={cfg.track_id} className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{cfg.config_name}</span>
              <Badge variant={cfg.owned ? 'success' : 'outline'} className="text-xs">
                {cfg.owned ? 'Tenés' : 'No tenés'}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function Tracks() {
  const [tracks, setTracks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.tracks.all(true).then((data) => {
      setTracks(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Mis Pistas</h1>
          <p className="text-sm text-muted-foreground">{tracks.length} pistas en tu colección</p>
        </div>
        <MapPin size={20} className="text-muted-foreground" />
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tracks.map((t) => (
            <TrackCard key={t.track_id} track={t} />
          ))}
        </div>
      )}
    </div>
  );
}
