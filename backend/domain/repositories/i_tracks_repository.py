from abc import ABC, abstractmethod
from domain.entities.track import Track


class ITracksRepository(ABC):
    @abstractmethod
    async def get_all_tracks(self) -> list[Track]: ...

    @abstractmethod
    async def get_owned_tracks(self) -> list[Track]: ...

    @abstractmethod
    async def get_track_by_id(self, track_id: int) -> Track | None: ...

    @abstractmethod
    async def get_series_count_by_track_id(self, track_id: int) -> int: ...
