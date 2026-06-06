from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.track import Track


class ITracksRepository(ABC):
    @abstractmethod
    async def get_all_tracks(self) -> List[Track]: ...

    @abstractmethod
    async def get_owned_tracks(self) -> List[Track]: ...

    @abstractmethod
    async def get_track_by_id(self, track_id: int) -> Optional[Track]: ...

    @abstractmethod
    async def get_series_count_by_track_id(self, track_id: int) -> int: ...
