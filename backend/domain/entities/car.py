from dataclasses import dataclass, field
from typing import Literal

CarCategory = Literal["road", "oval", "dirt_road", "dirt_oval"]


@dataclass
class Car:
    car_id: int
    name: str
    categories: list[CarCategory]
    car_class_id: int
    car_class_name: str
    price: float
    owned: bool
    retired: bool = False
    package_id: int | None = None
