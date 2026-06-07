from domain.entities.race import Race
from domain.repositories.i_races_repository import IRacesRepository
from infrastructure.iracing.mock.mock_data import MOCK_RACES


class MockRacesRepository(IRacesRepository):
    async def get_recent_races(self, cust_id: int | None = None, count: int = 20) -> list[Race]:
        return MOCK_RACES[:count]

    async def get_race_by_id(self, subsession_id: int) -> Race | None:
        return next((r for r in MOCK_RACES if r.subsession_id == subsession_id), None)


class IracingRacesRepository(IRacesRepository):
    def __init__(self, client, default_cust_id: int) -> None:
        self._client = client
        self._cust_id = default_cust_id

    async def get_recent_races(self, cust_id: int | None = None, count: int = 20) -> list[Race]:
        cid = cust_id or self._cust_id
        try:
            raw = self._client.stats_member_recent_races(cust_id=cid)
            # API returns a list directly or a dict with 'races' key
            if isinstance(raw, list):
                races_raw = raw[:count]
            else:
                races_raw = raw.get("races", [])[:count]
            return [self._map(r) for r in races_raw]
        except Exception as e:
            print(f"[races] Error: {e}")
            return []

    async def get_race_by_id(self, subsession_id: int) -> Race | None:
        races = await self.get_recent_races()
        return next((r for r in races if r.subsession_id == subsession_id), None)

    def _map(self, r: dict) -> Race:
        track = r.get("track", {})
        return Race(
            subsession_id=r.get("subsession_id", 0),
            series_id=r.get("series_id", 0),
            series_name=r.get("series_name", ""),
            season_name=r.get("season_name", ""),
            car_id=r.get("car_id", 0),
            car_name=r.get("car_name", ""),
            track_name=track.get("track_name", r.get("track_name", "")),
            track_config=track.get("config_name", r.get("track_config_name", "")),
            start_time=r.get("start_time", ""),
            finish_position=r.get("finish_position_in_class", r.get("finish_position", 0)),
            finish_position_in_class=r.get("finish_position_in_class", 0),
            num_drivers=r.get("field_strength", r.get("num_drivers", 0)),
            best_lap_time=r.get("best_lap_time", 0),
            avg_lap_time=0,
            laps_led=r.get("laps_led", 0),
            laps_complete=r.get("laps_complete", 0),
            incidents=r.get("incidents", 0),
            new_irating=r.get("newi_rating", r.get("new_irating", 0)),
            old_irating=r.get("oldi_rating", r.get("old_irating", 0)),
            new_safety_rating=r.get("new_cpi", 0.0),
            old_safety_rating=r.get("old_cpi", 0.0),
            category=r.get("category", "road"),
        )
