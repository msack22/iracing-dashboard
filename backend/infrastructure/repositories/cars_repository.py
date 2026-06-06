from __future__ import annotations
from typing import Dict, List, Optional
from domain.entities.car import Car, CarCategory
from domain.repositories.i_cars_repository import ICarsRepository
from infrastructure.iracing.mock.mock_data import MOCK_CARS, MOCK_SERIES_COUNT


class MockCarsRepository(ICarsRepository):
    async def get_all_cars(self) -> List[Car]:
        return MOCK_CARS

    async def get_owned_cars(self) -> List[Car]:
        return [c for c in MOCK_CARS if c.owned]

    async def get_cars_by_category(self, category: CarCategory) -> List[Car]:
        return [c for c in MOCK_CARS if category in c.categories]

    async def get_car_by_id(self, car_id: int) -> Optional[Car]:
        return next((c for c in MOCK_CARS if c.car_id == car_id), None)

    async def get_series_count_by_car_id(self, car_id: int) -> int:
        return MOCK_SERIES_COUNT.get(f"car_{car_id}", 0)


class IracingCarsRepository(ICarsRepository):
    def __init__(self, client) -> None:
        self._client = client
        self._series_cache: Dict[str, int] = {}

    async def get_all_cars(self) -> List[Car]:
        raw = self._client.get_cars()
        return [self._map(c) for c in raw]

    async def get_owned_cars(self) -> List[Car]:
        all_cars = await self.get_all_cars()
        return [c for c in all_cars if c.owned]

    async def get_cars_by_category(self, category: CarCategory) -> List[Car]:
        all_cars = await self.get_all_cars()
        return [c for c in all_cars if category in c.categories]

    async def get_car_by_id(self, car_id: int) -> Optional[Car]:
        all_cars = await self.get_all_cars()
        return next((c for c in all_cars if c.car_id == car_id), None)

    async def get_series_count_by_car_id(self, car_id: int) -> int:
        return self._series_cache.get(f"car_{car_id}", 0)

    def _map(self, raw: dict) -> Car:
        categories: list[CarCategory] = []
        for cat in raw.get("car_types", []):
            name = cat.get("car_type", "").lower()
            if name in ("road", "oval", "dirt_road", "dirt_oval"):
                categories.append(name)  # type: ignore[arg-type]
        if not categories:
            categories = ["road"]
        return Car(
            car_id=raw["car_id"],
            name=raw["car_name"],
            categories=categories,
            car_class_id=raw.get("car_class_id", 0),
            car_class_name=raw.get("car_class_name", ""),
            price=raw.get("price", 0.0),
            owned=raw.get("owned", False),
            retired=raw.get("retired", False),
            package_id=raw.get("package_id"),
        )
