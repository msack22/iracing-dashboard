from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.car import Car, CarCategory


class ICarsRepository(ABC):
    @abstractmethod
    async def get_all_cars(self) -> List[Car]: ...

    @abstractmethod
    async def get_owned_cars(self) -> List[Car]: ...

    @abstractmethod
    async def get_cars_by_category(self, category: CarCategory) -> List[Car]: ...

    @abstractmethod
    async def get_car_by_id(self, car_id: int) -> Optional[Car]: ...

    @abstractmethod
    async def get_series_count_by_car_id(self, car_id: int) -> int: ...
