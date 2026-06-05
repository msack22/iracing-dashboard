from dataclasses import dataclass


@dataclass
class Race:
    subsession_id: int
    series_id: int
    series_name: str
    season_name: str
    car_id: int
    car_name: str
    track_name: str
    track_config: str
    start_time: str
    finish_position: int
    finish_position_in_class: int
    num_drivers: int
    best_lap_time: int    # milliseconds
    avg_lap_time: int     # milliseconds
    laps_led: int
    laps_complete: int
    incidents: int
    new_irating: int
    old_irating: int
    new_safety_rating: float
    old_safety_rating: float
    category: str
