from abc import ABC, abstractmethod
from domain.entities.race import Race


class IRacesRepository(ABC):
    @abstractmethod
    async def get_recent_races(self, cust_id: int | None = None, count: int = 20) -> list[Race]: ...

    @abstractmethod
    async def get_race_by_id(self, subsession_id: int) -> Race | None: ...
