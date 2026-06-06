from __future__ import annotations
from typing import Dict, List, Optional
from domain.entities.track import Track, TrackConfig
from domain.repositories.i_tracks_repository import ITracksRepository
from infrastructure.iracing.mock.mock_data import MOCK_TRACKS, MOCK_SERIES_COUNT


class MockTracksRepository(ITracksRepository):
    async def get_all_tracks(self) -> List[Track]:
        return MOCK_TRACKS

    async def get_owned_tracks(self) -> List[Track]:
        return [t for t in MOCK_TRACKS if t.owned]

    async def get_track_by_id(self, track_id: int) -> Optional[Track]:
        return next((t for t in MOCK_TRACKS if t.track_id == track_id), None)

    async def get_series_count_by_track_id(self, track_id: int) -> int:
        return MOCK_SERIES_COUNT.get(f"track_{track_id}", 0)


class IracingTracksRepository(ITracksRepository):
    def __init__(self, client) -> None:
        self._client = client

    async def get_all_tracks(self) -> List[Track]:
        raw = self._client.get_tracks()
        grouped: dict[int, list[dict]] = {}
        for t in raw:
            pid = t.get("package_id") or t["track_id"]
            grouped.setdefault(pid, []).append(t)
        result = []
        for configs_raw in grouped.values():
            first = configs_raw[0]
            configs = [
                TrackConfig(
                    track_id=c["track_id"],
                    config_name=c.get("config_name", "Default"),
                    owned=c.get("owned", False),
                    price=c.get("price", 0.0),
                    package_id=c.get("package_id"),
                )
                for c in configs_raw
            ]
            result.append(
                Track(
                    track_id=first["track_id"],
                    name=first["track_name"],
                    city=first.get("city", ""),
                    country=first.get("country_code", ""),
                    configs=configs,
                    owned=any(c.owned for c in configs),
                    price=first.get("price", 0.0),
                    package_id=first.get("package_id"),
                )
            )
        return result

    async def get_owned_tracks(self) -> List[Track]:
        return [t for t in await self.get_all_tracks() if t.owned]

    async def get_track_by_id(self, track_id: int) -> Optional[Track]:
        return next((t for t in await self.get_all_tracks() if t.track_id == track_id), None)

    async def get_series_count_by_track_id(self, _track_id: int) -> int:
        return 0
