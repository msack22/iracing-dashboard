from dataclasses import dataclass


@dataclass
class TrackConfig:
    track_id: int
    config_name: str
    owned: bool
    price: float
    package_id: int | None = None


@dataclass
class Track:
    track_id: int
    name: str
    city: str
    country: str
    configs: list[TrackConfig]
    owned: bool
    price: float
    package_id: int | None = None
