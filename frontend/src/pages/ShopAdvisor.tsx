import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/api/client';
import { ShoppingCart, TrendingUp, DollarSign, Package } from 'lucide-react';

function BundleCard({ bundle, index }: { bundle: any; index: number }) {
  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">Bundle #{index + 1}</CardTitle>
          <Badge variant="success">{(bundle.discount_pct * 100).toFixed(0)}% OFF</Badge>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="text-muted-foreground line-through">${bundle.total_price}</span>
          <span className="text-lg font-bold text-primary">${bundle.final_price}</span>
          <span className="text-emerald-400">Ahorrás ${bundle.savings}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {bundle.items.map((item: any) => (
          <div key={`${item.type}-${item.id}`} className="flex items-center justify-between rounded-lg bg-muted/50 px-3 py-2">
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">{item.type === 'car' ? '🏎️ Auto' : '🗺️ Pista'}</Badge>
              <span className="text-sm">{item.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span>{item.series_count} series</span>
              <span className="font-medium text-foreground">${item.price}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function TopItemRow({ item, rank }: { item: any; rank: number }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <div className="flex items-center gap-3">
        <span className="w-5 text-xs text-muted-foreground text-right">{rank}</span>
        <Badge variant="secondary" className="text-xs shrink-0">
          {item.type === 'car' ? 'Auto' : 'Pista'}
        </Badge>
        <span className="text-sm">{item.name}</span>
      </div>
      <div className="flex items-center gap-4 text-xs text-muted-foreground shrink-0">
        <span className="flex items-center gap-1">
          <TrendingUp size={11} />
          {item.series_count} series
        </span>
        <span className="font-medium text-foreground">${item.price}</span>
      </div>
    </div>
  );
}

export function ShopAdvisor() {
  const [data, setData] = useState<any>(null);
  const [bundleSize, setBundleSize] = useState(3);
  const [loading, setLoading] = useState(true);

  const load = async (size: number) => {
    setLoading(true);
    const res = await api.recommendations.get(size);
    setData(res);
    setLoading(false);
  };

  useEffect(() => { load(bundleSize); }, []);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-semibold">Shop Advisor</h1>
          <p className="text-sm text-muted-foreground">Optimizá tus compras con descuentos por bundle</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Tamaño del bundle:</span>
          {[3, 6].map((n) => (
            <Button
              key={n}
              variant={bundleSize === n ? 'default' : 'outline'}
              size="sm"
              onClick={() => { setBundleSize(n); load(n); }}
            >
              {n} items ({n === 3 ? '10%' : '15%'} OFF)
            </Button>
          ))}
        </div>
      </div>

      {/* Investment summary */}
      {data?.investment_summary && (
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-2">
                <DollarSign size={16} className="text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Total invertido</p>
                <p className="text-lg font-bold">${data.investment_summary.total_spent}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2">
                <ShoppingCart size={16} className="text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Autos propios</p>
                <p className="text-lg font-bold">{data.investment_summary.owned_cars}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2">
                <Package size={16} className="text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Pistas propias</p>
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
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Bundles */}
          <div className="space-y-4">
            <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Bundles recomendados</h2>
            {data?.bundles?.map((b: any, i: number) => (
              <BundleCard key={i} bundle={b} index={i} />
            ))}
          </div>

          {/* Top items by value */}
          <div>
            <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">Mejor valor (series disponibles)</h2>
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
