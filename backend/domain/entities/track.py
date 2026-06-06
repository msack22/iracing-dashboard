from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TrackConfig:
    track_id: int
    config_name: str
    owned: bool
    price: float
    package_id: Optional[int] = None


@dataclass
class Track:
    track_id: int
    name: str
    city: str
    country: str
    configs: List[TrackConfig]
    owned: bool
    price: float
    package_id: Optional[int] = None
