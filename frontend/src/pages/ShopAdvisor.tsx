import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { TrendingUp, DollarSign, Car, MapPin } from 'lucide-react';

// ── Sub-components ────────────────────────────────────────────────────────────

function BundleCard({ bundle, index }: { bundle: any; index: number }) {
  const { t } = useTranslation();
  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">{t('shopAdvisor.bundleTitle', { index: index + 1 })}</CardTitle>
          <Badge variant="success">{(bundle.discount_pct * 100).toFixed(0)}% OFF</Badge>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-muted-foreground line-through text-sm">${bundle.total_price}</span>
          <span className="text-xl font-bold text-primary">${bundle.final_price}</span>
          <span className="text-xs text-emerald-400">{t('shopAdvisor.save', { amount: bundle.savings })}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {bundle.items.map((item: any) => (
          <div
            key={`${item.type}-${item.id}`}
            className="flex items-center justify-between rounded-lg bg-muted/50 px-3 py-2"
          >
            <div className="flex items-center gap-2 min-w-0">
              {item.type === 'car'
                ? <Car size={13} className="shrink-0 text-primary" />
                : <MapPin size={13} className="shrink-0 text-blue-400" />
              }
              <span className="text-sm truncate">{item.name}</span>
              {item.car_type && (
                <Badge variant="secondary" className="text-xs shrink-0">{item.car_type}</Badge>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground shrink-0 ml-2">
              <span>{t('shopAdvisor.seriesCount', { count: item.series_count })}</span>
              <span className="font-medium text-foreground">${item.price}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function TopItemRow({ item, rank }: { item: any; rank: number }) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <div className="flex items-center gap-3 min-w-0">
        <span className="w-5 text-xs text-muted-foreground text-right shrink-0">{rank}</span>
        {item.type === 'car'
          ? <Car size={13} className="shrink-0 text-primary" />
          : <MapPin size={13} className="shrink-0 text-blue-400" />
        }
        <span className="text-sm truncate">{item.name}</span>
        {item.car_type && (
          <Badge variant="secondary" className="text-xs shrink-0">{item.car_type}</Badge>
        )}
      </div>
      <div className="flex items-center gap-4 text-xs text-muted-foreground shrink-0">
        <span className="flex items-center gap-1">
          <TrendingUp size={11} />
          {t('shopAdvisor.seriesCount', { count: item.series_count })}
        </span>
        <span className="font-medium text-foreground">${item.price}</span>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function ShopAdvisor() {
  const { t } = useTranslation();
  const [data, setData] = useState<any>(null);
  const [bundleSize, setBundleSize] = useState(3);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [includeCars, setIncludeCars] = useState(true);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (size: number, types: string[], cars: boolean) => {
    setLoading(true);
    const res = await api.recommendations.get(size, types, cars);
    setData(res);
    setLoading(false);
  }, []);

  useEffect(() => { load(bundleSize, selectedTypes, includeCars); }, []);

  const toggleType = (type: string) => {
    const next = selectedTypes.includes(type)
      ? selectedTypes.filter((t) => t !== type)
      : [...selectedTypes, type];
    setSelectedTypes(next);
    load(bundleSize, next, includeCars);
  };

  const handleBundleSize = (size: number) => {
    setBundleSize(size);
    load(size, selectedTypes, includeCars);
  };

  const handleIncludeCars = (val: boolean) => {
    setIncludeCars(val);
    load(bundleSize, selectedTypes, val);
  };

  const availableTypes: string[] = data?.available_car_types ?? [];

  return (
    <div className="space-y-5 p-6">

      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold">{t('shopAdvisor.title')}</h1>
        <p className="text-sm text-muted-foreground">
          {t('shopAdvisor.subtitle')}
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4 space-y-4">

          {/* Car type selector */}
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {t('shopAdvisor.categoryLabel')}
            </p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => { setSelectedTypes([]); load(bundleSize, [], includeCars); }}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                  selectedTypes.length === 0
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'border-border text-muted-foreground hover:bg-accent hover:text-foreground'
                }`}
              >
                {t('shopAdvisor.filterAll')}
              </button>
              {availableTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => toggleType(type)}
                  className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors border ${
                    selectedTypes.includes(type)
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border text-muted-foreground hover:bg-accent hover:text-foreground'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Series shown */}
          {selectedTypes.length > 0 && data?.selected_series?.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">{t('shopAdvisor.seriesIncluded')}</p>
              <div className="flex flex-wrap gap-1.5">
                {data.selected_series.map((s: any) => (
                  <Badge key={s.series_name} variant="outline" className="text-xs">
                    {s.series_name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center gap-6 pt-1 border-t border-border">
            {/* Bundle size */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">{t('shopAdvisor.bundleLabel')}</span>
              {[3, 6].map((n) => (
                <button
                  key={n}
                  onClick={() => handleBundleSize(n)}
                  className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors border ${
                    bundleSize === n
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border text-muted-foreground hover:bg-accent'
                  }`}
                >
                  {t('shopAdvisor.bundleItems', { count: n, discount: n === 3 ? '10%' : '15%' })}
                </button>
              ))}
            </div>

            {/* Include cars toggle */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">{t('shopAdvisor.includeCarsLabel')}</span>
              <button
                onClick={() => handleIncludeCars(!includeCars)}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                  includeCars ? 'bg-primary' : 'bg-muted'
                }`}
              >
                <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                  includeCars ? 'translate-x-4' : 'translate-x-1'
                }`} />
              </button>
              <span className="text-xs text-muted-foreground">
                {includeCars ? t('shopAdvisor.includeCarsYes') : t('shopAdvisor.includeCarsNo')}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Investment summary */}
      {data?.investment_summary && (
        <div className="grid grid-cols-3 gap-3">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-2 shrink-0">
                <DollarSign size={15} className="text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t('shopAdvisor.totalInvested')}</p>
                <p className="text-lg font-bold">${data.investment_summary.total_spent}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2 shrink-0">
                <Car size={15} className="text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t('shopAdvisor.ownedCars')}</p>
                <p className="text-lg font-bold">{data.investment_summary.owned_cars}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2 shrink-0">
                <MapPin size={15} className="text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t('shopAdvisor.ownedTracks')}</p>
                <p className="text-lg font-bold">{data.investment_summary.owned_tracks}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : data?.top_items?.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-sm text-muted-foreground">
            {t('shopAdvisor.noContent')}
            <br />
            <span className="text-xs">{t('shopAdvisor.mayHaveEverything')}</span>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-5 lg:grid-cols-2">
          {/* Bundles */}
          <div className="space-y-4">
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              {t('shopAdvisor.recommendedBundles')}
            </h2>
            {data?.bundles?.length > 0
              ? data.bundles.map((b: any, i: number) => (
                  <BundleCard key={i} bundle={b} index={i} />
                ))
              : (
                <p className="text-sm text-muted-foreground">
                  {t('shopAdvisor.notEnoughItems', { size: bundleSize })}
                </p>
              )
            }
          </div>

          {/* Top items by value */}
          <div>
            <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
              {t('shopAdvisor.bestValue')}
            </h2>
            <Card>
              <CardContent className="p-4">
                {data?.top_items?.slice(0, 15).map((item: any, i: number) => (
                  <TopItemRow key={`${item.type}-${item.id}`} item={item} rank={i + 1} />
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
