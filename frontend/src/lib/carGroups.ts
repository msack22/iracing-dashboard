// Clasificación de autos por categoría/clase, usada para filtros locales en
// Garage, Series, Carreras, etc. Reemplaza al viejo RacingModeContext global
// (que dependía de listas de IDs hardcodeadas que no escalaban con el catálogo).

export type CarGroupKey = 'formula' | 'gt_sport' | 'oval_nascar' | 'dirt' | 'rallycross' | 'other';

/** Claves de traducción i18n para cada grupo (ver src/i18n/locales/*.json → carGroups). */
export const CAR_GROUP_LABEL_KEYS: Record<CarGroupKey, string> = {
  formula: 'carGroups.formula',
  gt_sport: 'carGroups.gt_sport',
  oval_nascar: 'carGroups.oval_nascar',
  dirt: 'carGroups.dirt',
  rallycross: 'carGroups.rallycross',
  other: 'carGroups.other',
};

export const CAR_GROUP_ORDER: CarGroupKey[] = ['formula', 'gt_sport', 'oval_nascar', 'dirt', 'rallycross', 'other'];

/** Clases de licencia de iRacing, usadas para filtros por licencia en Series y Overlap. */
export const LICENSE_CLASSES = ['R', 'D', 'C', 'B', 'A'] as const;
export type LicenseClass = typeof LICENSE_CLASSES[number];

export const LICENSE_BADGE_CLASS: Record<LicenseClass, string> = {
  R: 'bg-red-500/15 text-red-400 border border-red-500/30',
  D: 'bg-orange-500/15 text-orange-400 border border-orange-500/30',
  C: 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30',
  B: 'bg-green-500/15 text-green-400 border border-green-500/30',
  A: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
};

// Mapa explícito car_type → grupo: tiene prioridad total sobre los tokens de nombre de serie.
// Evita falsos positivos como "Ford Mustang Challenge by Skip Barber" → formula.
const CAR_TYPE_TO_GROUP: Record<string, CarGroupKey> = {
  // GT & Sport
  'gt4': 'gt_sport', 'gt3': 'gt_sport', 'gt3 cup': 'gt_sport',
  'gte': 'gt_sport', 'gtp': 'gt_sport', 'lmp2': 'gt_sport', 'lmp3': 'gt_sport',
  'sports car': 'gt_sport', 'touring car': 'gt_sport', 'tcr': 'gt_sport',
  'supercars': 'gt_sport', 'stock car brasil': 'gt_sport',
  'mx-5 cup': 'gt_sport', 'spec racer': 'gt_sport', 'gt challenge': 'gt_sport',
  // Fórmula / open-wheel
  'formula': 'formula', 'formula 1': 'formula', 'formula 4': 'formula',
  'formula vee': 'formula', 'indycar': 'formula', 'indy pro 2000': 'formula',
  'super formula': 'formula', 'classic f1': 'formula',
  // Oval / NASCAR
  'arca': 'oval_nascar', 'nascar cup': 'oval_nascar', 'nascar cup legacy': 'oval_nascar',
  'nascar trucks': 'oval_nascar', 'late model': 'oval_nascar', 'legends': 'oval_nascar',
  'modified': 'oval_nascar', 'srx': 'oval_nascar', 'street stock': 'oval_nascar',
  'super late model': 'oval_nascar', 'mini stock': 'oval_nascar',
  // Dirt
  'dirt late model': 'dirt', 'dirt midget': 'dirt', 'dirt modified': 'dirt',
  'sprint car': 'dirt', 'micro sprint': 'dirt',
  // Rallycross / Off-Road
  'rallycross': 'rallycross', 'off-road truck': 'rallycross',
};

const FORMULA_TOKENS = ['formula', 'f1', 'f2', 'f3', 'f4', 'f5', 'indycar', 'skip barber', 'dallara', 'ir-01', 'ir01', 'lotus'];
const RALLYCROSS_TOKENS = ['rallycross', 'rally', 'off-road', 'off road', 'baja', 'lucas oil', 'crosskart', 'rx'];
const DIRT_TOKENS = ['dirt', 'sprint car', 'midget', 'micro sprint', 'dirtcar', 'ump', 'world of outlaws', 'silver crown'];
const OVAL_NASCAR_TOKENS = [
  'nascar', 'oval', 'late model', 'modified', 'legends', 'street stock', 'super late model',
  'arca', 'truck series', 'xfinity', 'cup series', 'sk modified', 'whelen',
];

/** Clasificación detallada (para Garage y filtros con varios grupos). */
export function getCarGroupKey(carClassName?: string | null, carName?: string | null): CarGroupKey {
  const carType = (carClassName ?? '').toLowerCase().trim();

  // El car_type tiene prioridad: un GT4 nunca es Fórmula aunque el nombre diga "Skip Barber".
  if (carType && CAR_TYPE_TO_GROUP[carType]) return CAR_TYPE_TO_GROUP[carType];

  // Fallback por tokens en el texto combinado (para car_types no reconocidos)
  const l = `${carType} ${(carName ?? '').toLowerCase()}`;
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
