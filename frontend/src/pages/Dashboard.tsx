import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { TrendingUp, TrendingDown, Shield, Trophy, AlertTriangle, DollarSign } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import { formatLapTime } from '@/lib/utils';

function StatCard({ title, value, sub, icon: Icon, trend }: {
  title: string; value: string | number; sub?: string; icon: any; trend?: 'up' | 'down' | 'neutral';
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold tabular-nums">{value}</p>
            {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
          </div>
          <div className={`rounded-lg p-2 ${
            trend === 'up' ? 'bg-emerald-500/10' :
            trend === 'down' ? 'bg-red-500/10' : 'bg-muted'
          }`}>
            <Icon size={18} className={
              trend === 'up' ? 'text-emerald-400' :
              trend === 'down' ? 'text-red-400' : 'text-muted-foreground'
            } />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function licenseColor(group: string) {
  const g = group.toLowerCase();
  if (g.includes('rookie')) return 'bg-red-500';
  if (g.includes('d')) return 'bg-orange-500';
  if (g.includes('c')) return 'bg-yellow-500';
  if (g.includes('b')) return 'bg-green-500';
  if (g.includes('a')) return 'bg-blue-500';
  if (g.includes('pro')) return 'bg-purple-500';
  return 'bg-muted';
}

export function Dashboard() {
  const [profile, setProfile] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [races, setRaces] = useState<any[]>([]);
  const [recs, setRecs] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.member.profile(),
      api.member.iratingHistory(),
      api.races.recent(5),
      api.recommendations.get(),
    ]).then(([p, h, r, rec]) => {
      setProfile(p);
      setHistory(h);
      setRaces(r);
      setRecs(rec);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  const roadLicense = profile?.licenses?.find((l: any) => l.category === 'road');
  const lastRace = races[0];
  const irDelta = lastRace ? lastRace.new_irating - lastRace.old_irating : 0;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">{profile?.display_name ?? 'Driver'}</h1>
          <p className="text-sm text-muted-foreground">{profile?.club} · Member since {profile?.member_since?.slice(0,4)}</p>
        </div>
        {roadLicense && (
          <div className="flex items-center gap-2">
            <div className={`h-3 w-3 rounded-full ${licenseColor(roadLicense.group_name)}`} />
            <span className="text-sm font-medium">{roadLicense.group_name}</span>
          </div>
        )}
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          title="iRating Road"
          value={roadLicense?.irating?.toLocaleString() ?? '—'}
          sub={irDelta !== 0 ? `${irDelta > 0 ? '+' : ''}${irDelta} última carrera` : undefined}
          icon={irDelta >= 0 ? TrendingUp : TrendingDown}
          trend={irDelta > 0 ? 'up' : irDelta < 0 ? 'down' : 'neutral'}
        />
        <StatCard
          title="Safety Rating"
          value={roadLicense?.safety_rating?.toFixed(2) ?? '—'}
          icon={Shield}
          trend={roadLicense?.safety_rating >= 3.0 ? 'up' : 'down'}
        />
        <StatCard
          title="Autos propios"
          value={recs?.investment_summary?.owned_cars ?? '—'}
          icon={Trophy}
          trend="neutral"
        />
        <StatCard
          title="Invertido en contenido"
          value={`$${recs?.investment_summary?.total_spent?.toFixed(2) ?? '0'}`}
          sub={`${recs?.investment_summary?.owned_tracks ?? 0} pistas`}
          icon={DollarSign}
          trend="neutral"
        />
      </div>

      {/* iRating chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Evolución iRating (Road)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(v) => new Date(v).toLocaleDateString('es-AR', { month: 'short', day: 'numeric' })}
                tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                width={45}
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 12 }}
                labelFormatter={(v) => new Date(v).toLocaleDateString('es-AR')}
              />
              <Line
                type="monotone"
                dataKey="irating"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Last 5 races */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Últimas carreras</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-border">
            {races.map((r: any) => {
              const delta = r.new_irating - r.old_irating;
              return (
                <div key={r.subsession_id} className="flex items-center justify-between px-6 py-3">
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium">{r.track_name} <span className="text-muted-foreground font-normal">· {r.track_config}</span></p>
                    <p className="text-xs text-muted-foreground">{r.series_name} · {r.car_name}</p>
                  </div>
                  <div className="flex items-center gap-4 text-right">
                    <div>
                      <p className="text-xs text-muted-foreground">Posición</p>
                      <p className="text-sm font-semibold">{r.finish_position}/{r.num_drivers}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Mejor vuelta</p>
                      <p className="text-sm font-mono">{formatLapTime(r.best_lap_time)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">iR</p>
                      <p className={`text-sm font-semibold ${delta >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {delta >= 0 ? '+' : ''}{delta}
                      </p>
                    </div>
                    {r.incidents > 0 && (
                      <Badge variant="warning" className="gap-1">
                        <AlertTriangle size={10} />
                        {r.incidents}x
                      </Badge>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
