import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { api } from '@/api/client';
import { Car, Filter, Check, Plus, Search } from 'lucide-react';
import { CAR_GROUP_LABEL_KEYS, CAR_GROUP_ORDER, getCarGroupKey, type CarGroupKey } from '@/lib/carGroups';

const CAT_LABEL: Record<string, string> = { road: 'Road', oval: 'Oval', dirt_road: 'Dirt Road', dirt_oval: 'Dirt Oval' };
const GROUP_FILTER_KEYS: { value: 'Todos' | CarGroupKey; labelKey: string }[] = [
  { value: 'Todos', labelKey: 'garage.filterAll' },
  ...CAR_GROUP_ORDER.map((g) => ({ value: g, labelKey: CAR_GROUP_LABEL_KEYS[g] })),
];

function carTypeLabel(carClassName: string, carName: string): string {
  const name = (carClassName || carName).toLowerCase();
  if (name.includes('f4') || name.includes('formula 4')) return 'F4';
  if (name.includes('f3') || name.includes('formula 3')) return 'F3';
  if (name.includes('ir-01') || name.includes('ir01')) return 'Formula iR';
  if (name.includes('formula 2000') || name.includes('skip barber')) return 'Formula 2000';
  if (name.includes('lmp3')) return 'LMP3';
  if (name.includes('lmp2')) return 'LMP2';
  if (name.includes('gtp')) return 'GTP';
  if (name.includes('gt3 cup') || name.includes('cup')) return 'GT3 Cup';
  if (name.includes('gt3')) return 'GT3';
  if (name.includes('gt4')) return 'GT4';
  if (name.includes('gt2')) return 'GT2';
  if (name.includes('mx-5') || name.includes('mx5')) return 'MX-5';
  if (name.includes('classic formula') || name.includes('lotus')) return 'Classic F1';
  return carClassName || '—';
}

function CarCard({ car, onToggle }: { car: any; onToggle: (id: number, owned: boolean) => void }) {
  const { t } = useTranslation();
  const isFree = car.price === 0;
  const typeLabel = carTypeLabel(car.car_class_name, car.name);

  return (
    <Card className={`overflow-hidden transition-all ${car.owned ? 'border-emerald-500/30' : 'border-border hover:border-primary/40'}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0">
            <p className="font-medium text-sm leading-tight">{car.name}</p>
            <p className="text-xs text-muted-foreground">
              {car.categories.map((c: string) => CAT_LABEL[c] ?? c).join(' · ')}
            </p>
          </div>
          <Badge variant={isFree ? 'secondary' : 'outline'} className="shrink-0">
            {isFree ? t('garage.free') : `$${car.price}`}
          </Badge>
        </div>
        <div className="mt-3 flex items-center justify-between">
          <Badge variant="secondary" className="text-xs font-medium">
            {typeLabel}
          </Badge>
          <button
            onClick={() => onToggle(car.car_id, !car.owned)}
            className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors ${
              car.owned
                ? 'bg-emerald-500/15 text-emerald-400 hover:bg-red-500/15 hover:text-red-400'
                : 'bg-muted text-muted-foreground hover:bg-emerald-500/15 hover:text-emerald-400'
            }`}
            title={car.owned ? t('garage.markAsNotHave') : t('garage.markAsHave')}
          >
            {car.owned ? <Check size={11} /> : <Plus size={11} />}
            {car.owned ? t('garage.have') : t('garage.notHave')}
          </button>
        </div>
      </CardContent>
    </Card>
  );
}

export function Garage() {
  const { t } = useTranslation();
  const [cars, setCars] = useState<any[]>([]);
  const [filter, setFilter] = useState<'Todos' | CarGroupKey>('Todos');
  const [showAll, setShowAll] = useState(false);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadCars = useCallback(async () => {
    const [allCars, ownedData] = await Promise.all([
      api.cars.all(false),
      api.owned.get(),
    ]);
    const ownedSet = new Set(ownedData.cars);
    setCars(allCars.map((c: any) => ({
      ...c,
      owned: c.owned || ownedSet.has(c.car_id),
    })));
    setLoading(false);
  }, []);

  useEffect(() => { loadCars(); }, [loadCars]);

  const handleToggle = async (carId: number, owned: boolean) => {
    await api.owned.setCar(carId, owned);
    setCars((prev) => prev.map((c) => c.car_id === carId ? { ...c, owned } : c));
  };

  const q = search.trim().toLowerCase();
  const visible = (showAll ? cars : cars.filter((c) => c.owned))
    .filter((c) => filter === 'Todos' || getCarGroupKey(c.car_class_name, c.name) === filter)
    .filter((c) => !q || c.name.toLowerCase().includes(q) || c.car_class_name?.toLowerCase().includes(q));

  const ownedCount = cars.filter((c) => c.owned).length;

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">{t('garage.title')}</h1>
          <p className="text-sm text-muted-foreground">{t('garage.subtitle', { owned: ownedCount, total: cars.length })}</p>
        </div>
        <Car size={20} className="text-muted-foreground" />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex gap-1.5 flex-wrap">
          {GROUP_FILTER_KEYS.map((g) => (
            <button
              key={g.value}
              onClick={() => setFilter(g.value)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                filter === g.value
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-accent'
              }`}
            >
              {t(g.labelKey)}
            </button>
          ))}
        </div>
        <div className="relative shrink-0 w-full sm:w-56 sm:ml-auto">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('garage.searchPlaceholder')}
            className="h-8 pl-8 text-xs"
          />
        </div>
        <div>
          <button
            onClick={() => setShowAll((v) => !v)}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
              showAll ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground hover:bg-accent'
            }`}
          >
            <Filter size={12} />
            {showAll ? t('garage.showOwned') : t('garage.showAll')}
          </button>
        </div>
      </div>

      {/* Info banner */}
      {!loading && (
        <p className="text-xs text-muted-foreground bg-muted/40 rounded-lg px-3 py-2">
          {t('garage.infoBanner')}
        </p>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {visible.map((car) => (
            <CarCard key={car.car_id} car={car} onToggle={handleToggle} />
          ))}
          {visible.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
              {q ? t('garage.noResultsFor', { query: search }) : t('garage.noResults')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
