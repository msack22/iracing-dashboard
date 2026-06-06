import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { Car, Filter } from 'lucide-react';

const CATEGORIES = ['Todos', 'road', 'oval', 'dirt_road', 'dirt_oval'] as const;
const CAT_LABEL: Record<string, string> = { road: 'Road', oval: 'Oval', dirt_road: 'Dirt Road', dirt_oval: 'Dirt Oval' };

// Map car_class_name to a short display label
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

function CarCard({ car }: { car: any }) {
  const isFree = car.price === 0;
  const typeLabel = carTypeLabel(car.car_class_name, car.name);

  return (
    <Card className="overflow-hidden transition-all hover:border-primary/40">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0">
            <p className="font-medium text-sm leading-tight">{car.name}</p>
            <p className="text-xs text-muted-foreground">
              {car.categories.map((c: string) => CAT_LABEL[c] ?? c).join(' · ')}
            </p>
          </div>
          <Badge variant={isFree ? 'secondary' : 'outline'} className="shrink-0">
            {isFree ? 'Gratis' : `$${car.price}`}
          </Badge>
        </div>
        <div className="mt-3">
          <Badge variant="secondary" className="text-xs font-medium">
            {typeLabel}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}

export function Garage() {
  const [cars, setCars] = useState<any[]>([]);
  const [filter, setFilter] = useState('Todos');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.cars.all(true).then((data) => {
      setCars(data);
      setLoading(false);
    });
  }, []);

  const filtered = filter === 'Todos' ? cars : cars.filter((c) => c.categories.includes(filter));

  return (
    <div className="space-y-5 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Mi Garage</h1>
          <p className="text-sm text-muted-foreground">{cars.length} autos en tu colección</p>
        </div>
        <Car size={20} className="text-muted-foreground" />
      </div>

      {/* Category filter */}
      <div className="flex items-center gap-2">
        <Filter size={14} className="text-muted-foreground" />
        <div className="flex gap-1.5 flex-wrap">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                filter === cat
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-accent'
              }`}
            >
              {cat === 'Todos' ? 'Todos' : CAT_LABEL[cat]}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-7 w-7 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((car) => (
            <CarCard key={car.car_id} car={car} />
          ))}
          {filtered.length === 0 && (
            <div className="col-span-full py-12 text-center text-sm text-muted-foreground">
              No hay autos en esta categoría
            </div>
          )}
        </div>
      )}
    </div>
  );
}
