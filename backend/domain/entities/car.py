from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal, Optional

CarCategory = Literal["road", "oval", "dirt_road", "dirt_oval"]


@dataclass
class Car:
    car_id: int
    name: str
    categories: List[CarCategory]
    car_class_id: int
    car_class_name: str
    price: float
    owned: bool
    retired: bool = False
    package_id: Optional[int] = None
