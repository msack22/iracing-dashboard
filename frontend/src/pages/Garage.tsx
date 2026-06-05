import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/api/client';
import { Car, Filter } from 'lucide-react';

const CATEGORIES = ['Todos', 'road', 'oval', 'dirt_road', 'dirt_oval'] as const;
const CAT_LABEL: Record<string, string> = { road: 'Road', oval: 'Oval', dirt_road: 'Dirt Road', dirt_oval: 'Dirt Oval' };

function CarCard({ car }: { car: any }) {
  const isFree = car.price === 0;
  return (
    <Card className="overflow-hidden transition-all hover:border-primary/40">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0">
            <p className="font-medium text-sm leading-tight">{car.name}</p>
            <p className="text-xs text-muted-foreground">{car.car_class_name}</p>
          </div>
          <Badge variant={isFree ? 'secondary' : 'outline'} className="shrink-0">
            {isFree ? 'Gratis' : `$${car.price}`}
          </Badge>
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {car.categories.map((c: string) => (
            <Badge key={c} variant="secondary" className="text-xs">
              {CAT_LABEL[c] ?? c}
            </Badge>
          ))}
          {car.owned && (
            <Badge variant="success" className="text-xs">Tenés</Badge>
          )}
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
