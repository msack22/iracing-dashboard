// Clasificación de autos por categoría/clase, usada para filtros locales en
// Garage, Series, Carreras, etc. Reemplaza al viejo RacingModeContext global
// (que dependía de listas de IDs hardcodeadas que no escalaban con el catálogo).

export type CarGroupKey = 'formula' | 'gt_sport' | 'oval_nascar' | 'dirt' | 'rallycross' | 'other';

export const CAR_GROUP_LABELS: Record<CarGroupKey, string> = {
  formula: '🏎️ Fórmula',
  gt_sport: '🚗 GT & Sport',
  oval_nascar: '🏁 Oval / NASCAR',
  dirt: '🟤 Dirt',
  rallycross: '🌲 Rallycross / Off-Road',
  other: '🔧 Otro',
};

export const CAR_GROUP_ORDER: CarGroupKey[] = ['formula', 'gt_sport', 'oval_nascar', 'dirt', 'rallycross', 'other'];

const FORMULA_TOKENS = ['formula', 'f1', 'f2', 'f3', 'f4', 'f5', 'indycar', 'skip barber', 'dallara', 'ir-01', 'ir01', 'lotus'];
const RALLYCROSS_TOKENS = ['rallycross', 'rally', 'off-road', 'off road', 'baja', 'lucas oil', 'crosskart', 'rx'];
const DIRT_TOKENS = ['dirt', 'sprint car', 'midget', 'micro sprint', 'dirtcar', 'ump', 'world of outlaws', 'silver crown'];
const OVAL_NASCAR_TOKENS = [
  'nascar', 'oval', 'late model', 'modified', 'legends', 'street stock', 'super late model',
  'arca', 'truck series', 'xfinity', 'cup series', 'sk modified', 'whelen',
];

/** Clasificación detallada (para Garage y filtros con varios grupos). */
export function getCarGroupKey(carClassName?: string | null, carName?: string | null): CarGroupKey {
  const l = `${carClassName ?? ''} ${carName ?? ''}`.toLowerCase();
  if (RALLYCROSS_TOKENS.some((t) => l.includes(t))) return 'rallycross';
  if (DIRT_TOKENS.some((t) => l.includes(t))) return 'dirt';
  if (OVAL_NASCAR_TOKENS.some((t) => l.includes(t))) return 'oval_nascar';
  if (FORMULA_TOKENS.some((t) => l.includes(t))) return 'formula';
  if (l.trim()) return 'gt_sport';
  return 'other';
}

/** Clasificación binaria (para series/carreras donde sólo tenemos un car_type/car_name). */
export function getCarGroup(carTypeOrName: string): 'formula' | 'sport' {
  const l = (carTypeOrName ?? '').toLowerCase();
  return FORMULA_TOKENS.some((t) => l.includes(t)) ? 'formula' : 'sport';
}
