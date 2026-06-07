const BASE = '/api';

async function get<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
  const url = new URL(BASE + path, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
  }
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const json = await res.json();
  return json.data ?? json;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function del<T>(path: string): Promise<T> {
  const res = await fetch(BASE + path, { method: 'DELETE' });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(BASE + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  auth: {
    status: () => get<{ configured: boolean }>('/auth/status'),
    save: (username: string, password: string) => post('/auth/credentials', { username, password }),
    clear: () => del('/auth/credentials'),
  },
  member: {
    profile: () => get<any>('/member/profile'),
    iratingHistory: (category = 'road') => get<any[]>('/member/irating-history', { category }),
  },
  cars: {
    all: (ownedOnly = false) => get<any[]>('/cars', { owned_only: ownedOnly }),
  },
  tracks: {
    all: (ownedOnly = false) => get<any[]>('/tracks', { owned_only: ownedOnly }),
  },
  races: {
    recent: (count = 20) => get<any[]>('/races/recent', { count }),
    bySeries: (count = 50) => get<any[]>('/races/by-series', { count }),
  },
  series: {
    all: () => get<any[]>('/series'),
    seed: () => post('/series/seed', {}),
    update: (id: number, payload: object) => put('/series/' + id, payload),
    remove: (id: number) => del('/series/' + id),
  },
  overlap: {
    get: (seriesIds?: number[]) => {
      const url = new URL('/api/overlap', window.location.origin);
      if (seriesIds?.length) seriesIds.forEach((id) => url.searchParams.append('series_ids', String(id)));
      return fetch(url.toString()).then((r) => r.json()).then((j) => j.data ?? j);
    },
  },
  wishlist: {
    get: () => get<{ cars: number[]; tracks: number[] }>('/wishlist'),
    summary: () => get<any>('/wishlist/summary'),
    addTrack: (id: number) => post('/wishlist/track/' + id, {}),
    removeTrack: (id: number) => del('/wishlist/track/' + id),
    addCar: (id: number) => post('/wishlist/car/' + id, {}),
    removeCar: (id: number) => del('/wishlist/car/' + id),
    clear: () => del('/wishlist'),
  },
  owned: {
    get: () => get<{ cars: number[]; tracks: number[] }>('/owned'),
    setCar: (id: number, owned: boolean) => put('/owned/car/' + id, { owned }),
    setTrack: (id: number, owned: boolean) => put('/owned/track/' + id, { owned }),
  },
  settings: {
    getCurrentWeek: () => get<{ current_week: number }>('/settings/current-week'),
    setCurrentWeek: (week: number) => post<{ ok: boolean; current_week: number }>('/settings/current-week', { week }),
  },
  recommendations: {
    get: (bundleSize = 3, carTypes: string[] = [], includeCars = true) => {
      const url = new URL('/api/recommendations', window.location.origin);
      url.searchParams.set('bundle_size', String(bundleSize));
      url.searchParams.set('include_cars', String(includeCars));
      carTypes.forEach((t) => url.searchParams.append('car_types', t));
      return fetch(url.toString())
        .then((r) => r.json())
        .then((j) => j.data ?? j);
    },
  },
};
