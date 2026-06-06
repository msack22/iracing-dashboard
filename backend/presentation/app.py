from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import asdict
from typing import List, Optional

from domain.repositories.i_cars_repository import ICarsRepository
from domain.repositories.i_tracks_repository import ITracksRepository
from domain.repositories.i_member_repository import IMemberRepository
from domain.repositories.i_races_repository import IRacesRepository
from application.use_cases.recommendations.get_purchase_recommendations import GetPurchaseRecommendationsUseCase
from infrastructure.auth.credentials_store import (
    save_credentials, credentials_exist, delete_credentials
)
from pydantic import BaseModel


class CredentialsPayload(BaseModel):
    username: str
    password: str


def create_app(
    cars_repo: ICarsRepository,
    tracks_repo: ITracksRepository,
    member_repo: IMemberRepository,
    races_repo: IRacesRepository,
) -> FastAPI:
    app = FastAPI(title="iRacing Dashboard API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Auth ─────────────────────────────────────────────────────────────────
    @app.get("/api/auth/status")
    def auth_status():
        return {"configured": credentials_exist()}

    @app.post("/api/auth/credentials")
    def set_credentials(payload: CredentialsPayload):
        save_credentials(payload.username, payload.password)
        return {"ok": True}

    @app.delete("/api/auth/credentials")
    def clear_credentials():
        delete_credentials()
        return {"ok": True}

    # ── Health ────────────────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # ── Member ────────────────────────────────────────────────────────────────
    @app.get("/api/member/profile")
    async def member_profile():
        profile = await member_repo.get_member_profile()
        return {"data": asdict(profile)}

    @app.get("/api/member/irating-history")
    async def irating_history(category: str = "road"):
        history = await member_repo.get_irating_history(category=category)
        return {"data": history}

    # ── Cars ──────────────────────────────────────────────────────────────────
    @app.get("/api/cars")
    async def get_cars(owned_only: bool = False):
        cars = await (cars_repo.get_owned_cars() if owned_only else cars_repo.get_all_cars())
        return {"data": [asdict(c) for c in cars]}

    @app.get("/api/cars/category/{category}")
    async def cars_by_category(category: str):
        if category not in ("road", "oval", "dirt_road", "dirt_oval"):
            return {"error": "Invalid category"}, 400
        cars = await cars_repo.get_cars_by_category(category)  # type: ignore[arg-type]
        return {"data": [asdict(c) for c in cars]}

    # ── Tracks ────────────────────────────────────────────────────────────────
    @app.get("/api/tracks")
    async def get_tracks(owned_only: bool = False):
        tracks = await (tracks_repo.get_owned_tracks() if owned_only else tracks_repo.get_all_tracks())
        return {"data": [asdict(t) for t in tracks]}

    # ── Races ─────────────────────────────────────────────────────────────────
    @app.get("/api/races/recent")
    async def recent_races(count: int = 20):
        races = await races_repo.get_recent_races(count=count)
        return {"data": [asdict(r) for r in races]}

    # ── Series calendar ───────────────────────────────────────────────────────
    @app.get("/api/series")
    async def get_series():
        from infrastructure.iracing.mock.mock_data import MOCK_SERIES, MOCK_CARS, MOCK_TRACKS
        all_cars = await cars_repo.get_all_cars()
        all_tracks = await tracks_repo.get_all_tracks()
        car_map = {c.car_id: c for c in all_cars}
        track_map = {t.track_id: t for t in all_tracks}

        result = []
        for s in MOCK_SERIES:
            # Cars needed for this series
            series_cars = [
                {
                    "car_id": c.car_id,
                    "name": c.name,
                    "car_type": c.car_class_name,
                    "owned": c.owned,
                    "price": c.price,
                }
                for c in all_cars
                if c.car_class_id in s["car_class_ids"]
            ]
            owned_cars_count = sum(1 for c in series_cars if c["owned"])

            # Tracks this season
            season_tracks = []
            for tid in s["season_tracks"]:
                t = track_map.get(tid)
                if t:
                    season_tracks.append({
                        "track_id": t.track_id,
                        "name": t.name,
                        "country": t.country,
                        "owned": t.owned,
                        "price": t.price,
                    })
            owned_tracks_count = sum(1 for t in season_tracks if t["owned"])

            can_race = owned_cars_count > 0 and owned_tracks_count > 0
            missing_cars = [c for c in series_cars if not c["owned"]]
            missing_tracks = [t for t in season_tracks if not t["owned"]]

            result.append({
                "series_id": s["series_id"],
                "series_name": s["series_name"],
                "car_type": s["car_type"],
                "cars": series_cars,
                "season_tracks": season_tracks,
                "can_race": can_race,
                "owned_cars_count": owned_cars_count,
                "owned_tracks_count": owned_tracks_count,
                "missing_cars": missing_cars,
                "missing_tracks": missing_tracks,
            })
        return {"data": result}

    # ── Recommendations ───────────────────────────────────────────────────────
    @app.get("/api/recommendations")
    async def recommendations(
        bundle_size: int = 3,
        car_types: Optional[List[str]] = Query(default=None),
        include_cars: bool = True,
    ):
        uc = GetPurchaseRecommendationsUseCase(cars_repo, tracks_repo)
        result = await uc.execute(
            bundle_size=bundle_size,
            car_types=car_types if car_types else None,
            include_cars=include_cars,
        )
        return {"data": result}

    return app
