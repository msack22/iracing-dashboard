from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.race import Race


class IRacesRepository(ABC):
    @abstractmethod
    async def get_recent_races(self, cust_id: Optional[int] = None, count: int = 20) -> List[Race]: ...

    @abstractmethod
    async def get_race_by_id(self, subsession_id: int) -> Optional[Race]: ...
