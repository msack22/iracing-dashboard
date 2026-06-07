import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { TrendingUp, TrendingDown, Shield, Trophy, AlertTriangle, DollarSign, Car, MapPin } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell,
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
  const { t } = useTranslation();
  const [profile, setProfile] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [allRaces, setAllRaces] = useState<any[]>([]);
  const [recs, setRecs] = useState<any>(null);
  const [allCars, setAllCars] = useState<any[]>([]);
  const [allTracks, setAllTracks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.member.profile(),
      api.member.iratingHistory(),
      api.races.recent(20),
      api.recommendations.get(),
      api.cars.all(),
      api.tracks.all(),
    ]).then(([p, h, r, rec, cars, tracks]) => {
      setProfile(p);
      setHistory(h);
      setAllRaces(r);
      setRecs(rec);
      setAllCars((cars as any) ?? []);
      setAllTracks((tracks as any) ?? []);
      setLoading(false);
    });
  }, []);

  const races = allRaces.slice(0, 5);

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
          <h1 className="text-xl font-semibold">{profile?.display_name ?? t('dashboard.driverFallback')}</h1>
          <p className="text-sm text-muted-foreground">{t('dashboard.memberSince', { club: profile?.club, year: profile?.member_since?.slice(0,4) })}</p>
        </div>
        <div className="flex items-center gap-3">
          {roadLicense && (
            <div className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${licenseColor(roadLicense.group_name)}`} />
              <span className="text-sm font-medium">{roadLicense.group_name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          title={t('dashboard.statIRatingRoad')}
          value={roadLicense?.irating?.toLocaleString() ?? '—'}
          sub={irDelta !== 0 ? t('dashboard.lastRaceDelta', { delta: `${irDelta > 0 ? '+' : ''}${irDelta}` }) : undefined}
          icon={irDelta >= 0 ? TrendingUp : TrendingDown}
          trend={irDelta > 0 ? 'up' : irDelta < 0 ? 'down' : 'neutral'}
        />
        <StatCard
          title={t('dashboard.statSafetyRating')}
          value={roadLicense?.safety_rating?.toFixed(2) ?? '—'}
          icon={Shield}
          trend={roadLicense?.safety_rating >= 3.0 ? 'up' : 'down'}
        />
        <StatCard
          title={t('dashboard.statOwnedCars')}
          value={recs?.investment_summary?.owned_cars ?? '—'}
          icon={Trophy}
          trend="neutral"
        />
        <StatCard
          title={t('dashboard.statInvestedContent')}
          value={`$${recs?.investment_summary?.total_spent?.toFixed(2) ?? '0'}`}
          sub={t('dashboard.tracksCount', { count: recs?.investment_summary?.owned_tracks ?? 0 })}
          icon={DollarSign}
          trend="neutral"
        />
      </div>

      {/* Content purchased breakdown */}
      {(() => {
        const ownedCars  = allCars.filter((c: any) => c.owned && c.price > 0);
        const ownedTracks = allTracks.filter((t: any) => t.owned && t.price > 0);
        const carSpend   = ownedCars.reduce((s: number, c: any) => s + c.price, 0);
        const trackSpend = ownedTracks.reduce((s: number, t: any) => s + t.price, 0);
        const total      = carSpend + trackSpend;
        if (total === 0) return null;

        const ownedCarsCount = allCars.filter((c: any) => c.owned).length;
        const ownedTracksCount = allTracks.filter((t: any) => t.owned).length;
        const pieData = [
          { name: t('dashboard.cars'), value: carSpend, color: '#60a5fa' },
          { name: t('dashboard.tracksLabel'), value: trackSpend, color: '#34d399' },
        ].filter((d) => d.value > 0);

        return (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">{t('dashboard.contentPurchased')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr]">
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-blue-500/10 p-2">
                      <Car size={16} className="text-blue-400" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">{t('dashboard.cars')}</p>
                      <p className="text-lg font-bold">{ownedCars.length} <span className="text-xs font-normal text-muted-foreground">{t('dashboard.ofYouHave', { count: ownedCarsCount })}</span></p>
                      <p className="text-xs text-muted-foreground">{t('dashboard.spentCatalog', { spend: carSpend.toFixed(2), total: allCars.length })}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-emerald-500/10 p-2">
                      <MapPin size={16} className="text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">{t('dashboard.tracksLabel')}</p>
                      <p className="text-lg font-bold">{ownedTracks.length} <span className="text-xs font-normal text-muted-foreground">{t('dashboard.ofYouHave', { count: ownedTracksCount })}</span></p>
                      <p className="text-xs text-muted-foreground">{t('dashboard.spentCatalog', { spend: trackSpend.toFixed(2), total: allTracks.length })}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-amber-500/10 p-2">
                      <DollarSign size={16} className="text-amber-400" />
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">{t('dashboard.totalInvested')}</p>
                      <p className="text-lg font-bold">${total.toFixed(2)}</p>
                      <p className="text-xs text-muted-foreground">{t('dashboard.paidItems', { count: ownedCars.length + ownedTracks.length })}</p>
                    </div>
                  </div>
                </div>

                <div className="hidden md:block w-px bg-border" />

                <div className="flex items-center gap-4">
                  <ResponsiveContainer width={120} height={120}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={36}
                        outerRadius={56}
                        paddingAngle={2}
                        stroke="none"
                      >
                        {pieData.map((d) => <Cell key={d.name} fill={d.color} />)}
                      </Pie>
                      <Tooltip
                        formatter={(v: number) => `$${v.toFixed(2)}`}
                        contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 12 }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-2 text-xs">
                    {pieData.map((d) => (
                      <div key={d.name} className="flex items-center gap-2">
                        <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                        <span className="text-muted-foreground">{d.name}</span>
                        <span className="font-semibold">{((d.value / total) * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                    <p className="text-muted-foreground pt-1">{t('dashboard.spendDistribution')}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })()}

      {/* iRating chart */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{t('dashboard.iratingEvolution')}</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(v) => new Date(v).toLocaleDateString(t('common.dateLocale'), { month: 'short', day: 'numeric' })}
                tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                width={45}
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 8, fontSize: 12 }}
                labelFormatter={(v) => new Date(v).toLocaleDateString(t('common.dateLocale'))}
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
          <CardTitle className="text-sm">{t('dashboard.lastRaces')}</CardTitle>
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
                      <p className="text-xs text-muted-foreground">{t('dashboard.position')}</p>
                      <p className="text-sm font-semibold">{r.finish_position}/{r.num_drivers}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">{t('dashboard.bestLap')}</p>
                      <p className="text-sm font-mono">{formatLapTime(r.best_lap_time)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">{t('dashboard.ir')}</p>
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
