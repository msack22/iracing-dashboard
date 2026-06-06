import random
from datetime import datetime, timedelta
from domain.entities.car import Car
from domain.entities.track import Track, TrackConfig
from domain.entities.member import Member, License
from domain.entities.race import Race


def _rand_lap(base_ms: int) -> int:
    return base_ms + random.randint(-2000, 2000)


MOCK_MEMBER = Member(
    cust_id=1240652,
    username="matiassack",
    display_name="Matias Sack",
    club="Argentina",
    member_since="2022-03-15",
    last_login=datetime.utcnow().isoformat(),
    licenses=[
        License(
            category="road",
            license_level_id=8,
            group_name="Class D",
            safety_rating=3.47,
            irating=1423,
            ttrating=1102,
        ),
        License(
            category="oval",
            license_level_id=1,
            group_name="Rookie",
            safety_rating=2.10,
            irating=1012,
            ttrating=0,
        ),
    ],
)

MOCK_CARS: list[Car] = [
    # Owned
    Car(67,  "Dallara F3",               ["road"], 68,  "Dallara F3",          11.99, owned=True),
    Car(99,  "Dallara F4",               ["road"], 101, "Dallara F4",          11.99, owned=True),
    Car(33,  "Mazda MX-5 Cup",           ["road"], 53,  "MX-5 Cup",            0.00,  owned=True),
    Car(77,  "Skip Barber Formula 2000", ["road"], 63,  "Skip Barber",         0.00,  owned=True),
    Car(120, "Ferrari 488 GT3 Evo 2020", ["road"], 100, "GT3",                 11.99, owned=True),
    Car(75,  "Porsche 911 GT3 Cup (992)",["road"], 131, "GT3 Cup",             11.99, owned=True),
    # Not owned
    Car(139, "Dallara iR-01",            ["road"], 129, "iRacing Formula",     11.99, owned=False),
    Car(137, "Ligier JS P320",           ["road"], 128, "LMP3",                11.99, owned=False),
    Car(105, "Porsche 963 GTP",          ["road"], 140, "GTP",                 14.99, owned=False),
    Car(84,  "McLaren MP4-12C GT3",      ["road"], 92,  "GT3",                 11.99, owned=False),
    Car(152, "BMW M4 GT3",               ["road"], 145, "GT3",                 14.99, owned=False),
    Car(41,  "Lotus 49",                 ["road"], 25,  "Classic Formula",     11.99, owned=False),
    Car(88,  "Mercedes-AMG GT3 2020",    ["road"], 118, "GT3",                 11.99, owned=False),
    Car(117, "Toyota GR86",             ["road"], 148, "GT4",                  11.99, owned=False),
]

MOCK_TRACKS: list[Track] = [
    # Owned
    Track(1, "Brands Hatch", "Swanley", "UK",
          [TrackConfig(1, "Grand Prix", True, 14.99), TrackConfig(11, "Indy", True, 0.0)],
          owned=True, price=14.99),
    Track(2, "Monza", "Monza", "Italy",
          [TrackConfig(2, "Grand Prix", True, 14.99), TrackConfig(22, "Junior", True, 0.0)],
          owned=True, price=14.99),
    Track(4, "Nürburgring", "Nürburg", "Germany",
          [TrackConfig(4, "Grand Prix", True, 0.0)],
          owned=True, price=0.0),
    # Not owned
    Track(5, "Circuit de Barcelona-Catalunya", "Barcelona", "Spain",
          [TrackConfig(5, "Grand Prix", False, 14.99), TrackConfig(51, "National", False, 0.0)],
          owned=False, price=14.99),
    Track(6, "Spa-Francorchamps", "Stavelot", "Belgium",
          [TrackConfig(6, "Grand Prix", False, 14.99)],
          owned=False, price=14.99),
    Track(7, "Silverstone", "Silverstone", "UK",
          [TrackConfig(7, "Grand Prix", False, 14.99), TrackConfig(71, "International", False, 0.0)],
          owned=False, price=14.99),
    Track(8, "Suzuka", "Suzuka", "Japan",
          [TrackConfig(8, "Grand Prix", False, 14.99)],
          owned=False, price=14.99),
    Track(9, "Hungaroring", "Budapest", "Hungary",
          [TrackConfig(9, "Grand Prix", False, 14.99)],
          owned=False, price=14.99),
    Track(10, "Imola", "Imola", "Italy",
          [TrackConfig(10, "Grand Prix", False, 14.99)],
          owned=False, price=14.99),
    Track(12, "Zandvoort", "Zandvoort", "Netherlands",
          [TrackConfig(12, "Grand Prix", False, 14.99)],
          owned=False, price=14.99),
    Track(13, "Mugello", "Mugello", "Italy",
          [TrackConfig(13, "Grand Prix", False, 14.99)],
          owned=False, price=14.99),
]

MOCK_SERIES_COUNT: dict[str, int] = {
    "car_67": 8, "car_99": 12, "car_33": 6, "car_77": 5,
    "car_120": 10, "car_75": 9, "car_139": 14, "car_137": 7,
    "car_105": 11, "car_84": 6, "car_152": 13, "car_41": 4,
    "car_88": 9, "car_117": 7,
    "track_1": 12, "track_2": 15, "track_4": 10, "track_5": 11,
    "track_6": 18, "track_7": 16, "track_8": 14, "track_9": 9,
    "track_10": 13, "track_12": 10, "track_13": 8,
}

_base = datetime.utcnow()

MOCK_RACES: list[Race] = [
    Race(70001, 501, "iRacing Formula 4 Series", "2024 S2", 99, "Dallara F4",
         "Brands Hatch", "Grand Prix", (_base - timedelta(days=5)).isoformat(),
         3, 3, 22, _rand_lap(82000), _rand_lap(84000), 2, 18, 2,
         1423, 1389, 3.47, 3.28, "road"),
    Race(70002, 501, "iRacing Formula 4 Series", "2024 S2", 99, "Dallara F4",
         "Monza", "Grand Prix", (_base - timedelta(days=10)).isoformat(),
         7, 7, 20, _rand_lap(97000), _rand_lap(99000), 0, 22, 4,
         1389, 1401, 3.28, 3.44, "road"),
    Race(70003, 502, "F3 Open Series", "2024 S2", 67, "Dallara F3",
         "Nürburgring", "Grand Prix", (_base - timedelta(days=15)).isoformat(),
         5, 5, 18, _rand_lap(119000), _rand_lap(121000), 1, 15, 1,
         1401, 1385, 3.44, 3.38, "road"),
    Race(70004, 503, "GT3 Endurance Series", "2024 S2", 120, "Ferrari 488 GT3 Evo 2020",
         "Monza", "Grand Prix", (_base - timedelta(days=20)).isoformat(),
         2, 2, 30, _rand_lap(107000), _rand_lap(109000), 5, 40, 0,
         1385, 1360, 3.38, 3.21, "road"),
    Race(70005, 501, "iRacing Formula 4 Series", "2024 S2", 99, "Dallara F4",
         "Brands Hatch", "Indy", (_base - timedelta(days=27)).isoformat(),
         1, 1, 19, _rand_lap(56000), _rand_lap(58000), 12, 20, 0,
         1360, 1310, 3.21, 3.02, "road"),
    Race(70006, 504, "Porsche GT3 Cup Series", "2024 S2", 75, "Porsche 911 GT3 Cup (992)",
         "Nürburgring", "Grand Prix", (_base - timedelta(days=35)).isoformat(),
         9, 9, 24, _rand_lap(122000), _rand_lap(125000), 0, 14, 6,
         1310, 1340, 3.02, 3.25, "road"),
]

# Series del calendario actual — qué pistas y autos usa cada categoría esta temporada
# car_class_ids mapea con car.car_class_id en MOCK_CARS
MOCK_SERIES = [
    {
        "series_id": 501,
        "series_name": "iRacing Formula 4 Series",
        "car_type": "F4",
        "car_class_ids": [101],         # Dallara F4
        "season_tracks": [1, 2, 4, 5, 6, 7, 9],   # track_ids en el calendario
    },
    {
        "series_id": 502,
        "series_name": "F3 Open Series",
        "car_type": "F3",
        "car_class_ids": [68],          # Dallara F3
        "season_tracks": [2, 4, 8, 9, 10, 12],
    },
    {
        "series_id": 505,
        "series_name": "iRacing Formula iR-01 Series",
        "car_type": "Formula iR",
        "car_class_ids": [129],         # Dallara iR-01
        "season_tracks": [5, 6, 7, 8, 10, 13],
    },
    {
        "series_id": 503,
        "series_name": "GT3 Endurance Series",
        "car_type": "GT3",
        "car_class_ids": [100, 92, 118, 145, 131],  # Ferrari, McLaren, Mercedes, BMW, Porsche Cup
        "season_tracks": [1, 2, 5, 6, 7, 8, 10, 12],
    },
    {
        "series_id": 504,
        "series_name": "Porsche GT3 Cup Series",
        "car_type": "GT3 Cup",
        "car_class_ids": [131],         # Porsche GT3 Cup 992
        "season_tracks": [1, 4, 5, 7, 9, 13],
    },
    {
        "series_id": 506,
        "series_name": "GT4 Challenge Series",
        "car_type": "GT4",
        "car_class_ids": [148],         # Toyota GR86
        "season_tracks": [1, 2, 4, 9, 12, 13],
    },
    {
        "series_id": 507,
        "series_name": "LMP3 Series",
        "car_type": "LMP3",
        "car_class_ids": [128],         # Ligier JS P320
        "season_tracks": [5, 6, 7, 8, 10, 13],
    },
    {
        "series_id": 508,
        "series_name": "GTP Series",
        "car_type": "GTP",
        "car_class_ids": [140],         # Porsche 963
        "season_tracks": [6, 7, 8, 10, 12, 13],
    },
]

MOCK_IRATING_HISTORY = [
    {"timestamp": "2024-02-01T00:00:00Z", "irating": 1200},
    {"timestamp": "2024-02-15T00:00:00Z", "irating": 1230},
    {"timestamp": "2024-03-01T00:00:00Z", "irating": 1195},
    {"timestamp": "2024-03-15T00:00:00Z", "irating": 1258},
    {"timestamp": "2024-04-01T00:00:00Z", "irating": 1290},
    {"timestamp": "2024-04-15T00:00:00Z", "irating": 1310},
    {"timestamp": "2024-04-28T00:00:00Z", "irating": 1360},
    {"timestamp": "2024-05-05T00:00:00Z", "irating": 1385},
    {"timestamp": "2024-05-10T00:00:00Z", "irating": 1401},
    {"timestamp": "2024-05-15T00:00:00Z", "irating": 1389},
    {"timestamp": "2024-05-20T00:00:00Z", "irating": 1423},
]
