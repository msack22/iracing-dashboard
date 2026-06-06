import { createContext, useContext, useState, ReactNode } from 'react';

export type RacingMode = 'all' | 'formula' | 'sport';

const FORMULA_CAR_IDS = [67, 99, 77, 139, 41];   // F3, F4, Skip Barber, iR-01, Lotus
const SPORT_CAR_IDS   = [120, 75, 84, 152, 88, 105, 137, 117, 33]; // GT3, GTP, LMP3, MX-5

interface RacingModeCtx {
  mode: RacingMode;
  setMode: (m: RacingMode) => void;
  filterRaces: (races: any[]) => any[];
}

const RacingModeContext = createContext<RacingModeCtx>({
  mode: 'all',
  setMode: () => {},
  filterRaces: (r) => r,
});

export function RacingModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<RacingMode>('all');

  const filterRaces = (races: any[]) => {
    if (mode === 'all') return races;
    if (mode === 'formula') return races.filter((r) => FORMULA_CAR_IDS.includes(r.car_id));
    return races.filter((r) => SPORT_CAR_IDS.includes(r.car_id));
  };

  return (
    <RacingModeContext.Provider value={{ mode, setMode, filterRaces }}>
      {children}
    </RacingModeContext.Provider>
  );
}

export const useRacingMode = () => useContext(RacingModeContext);
