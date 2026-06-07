import random
from datetime import datetime, timedelta
from domain.entities.car import Car
from domain.entities.track import Track, TrackConfig
from domain.entities.member import Member, License
from domain.entities.race import Race


def _rand_lap(base_ms: int) -> int:
    return base_ms + random.randint(-2000, 2000)


# Perfil de ejemplo — el usuario real se configura conectando la API de iRacing
MOCK_MEMBER = Member(
    cust_id=123456,
    username="demo_driver",
    display_name="Demo Driver",
    club="Demo Club",
    member_since="2023-01-01",
    last_login=datetime.utcnow().isoformat(),
    licenses=[
        License(
            category="sport_car",
            license_level_id=12,
            group_name="Class C",
            safety_rating=3.50,
            irating=1200,
            ttrating=0,
        ),
        License(
            category="formula",
            license_level_id=9,
            group_name="Class D",
            safety_rating=3.20,
            irating=1150,
            ttrating=900,
        ),
    ],
)

# ── Autos ─────────────────────────────────────────────────────────────────────
# owned=True solo en contenido incluido gratis con la suscripción de iRacing.
# Configurá los tuyos desde Configuración → Autos en mi Garage.
# Los car_id aproximados se corrigen automáticamente cuando la API real está disponible.
MOCK_CARS: list[Car] = [

    # ═══════════════════════════════════════════════════════
    # ROAD — GRATIS CON SUSCRIPCIÓN
    # ═══════════════════════════════════════════════════════
    Car(39,  "Cadillac CTS-V Racecar",               ["road"],            70,  "Touring Car",   0.00,  owned=True),
    Car(33,  "Global Mazda MX-5 Cup",                ["road"],            53,  "MX-5 Cup",      0.00,  owned=True),
    Car(107, "Kia Optima",                           ["road"],            70,  "Touring Car",   0.00,  owned=True),
    Car(21,  "Pontiac Solstice",                     ["road"],            70,  "Touring Car",   0.00,  owned=True),
    Car(24,  "SCCA Spec Racer Ford",                 ["road"],            35,  "Spec Racer",    0.00,  owned=True),
    Car(32,  "VW Jetta TDI Cup",                     ["road"],            70,  "Touring Car",   0.00,  owned=True),
    Car(5,   "[Legacy] Mazda MX-5 Cup 2010",         ["road"],            53,  "MX-5 Cup",      0.00,  owned=True),
    Car(75,  "[Legacy] Porsche 911 GT3 Cup (992.1)", ["road"],            131, "GT3 Cup",       0.00,  owned=True),
    Car(77,  "Skip Barber Formula 2000",             ["road"],            63,  "Formula",       0.00,  owned=True),
    Car(25,  "Ray FF1600",                           ["road"],            37,  "Formula",       0.00,  owned=True),

    # ═══════════════════════════════════════════════════════
    # ROAD — GT3
    # ═══════════════════════════════════════════════════════
    Car(164, "Ferrari 296 GT3",                      ["road"],            84,  "GT3",           11.99, owned=False),
    Car(120, "Ferrari 488 GT3 Evo 2020",             ["road"],            84,  "GT3",           11.99, owned=False),
    Car(152, "BMW M4 GT3",                           ["road"],            84,  "GT3",           14.99, owned=False),
    Car(88,  "Mercedes-AMG GT3 2020",                ["road"],            84,  "GT3",           11.99, owned=False),
    Car(181, "Audi R8 LMS EVO II GT3",               ["road"],            84,  "GT3",           14.99, owned=False),
    Car(185, "McLaren 720S GT3 EVO",                 ["road"],            84,  "GT3",           14.99, owned=False),
    Car(186, "Ford Mustang GT3",                     ["road"],            84,  "GT3",           14.99, owned=False),
    Car(160, "Lamborghini Huracán GT3 EVO",          ["road"],            84,  "GT3",           14.99, owned=False),
    Car(176, "Porsche 911 GT3 R 992",                ["road"],            84,  "GT3",           14.99, owned=False),
    Car(187, "Aston Martin Vantage GT3",             ["road"],            84,  "GT3",           14.99, owned=False),
    Car(188, "McLaren 650S GT3",                     ["road"],            84,  "GT3",           11.99, owned=False),
    Car(189, "Callaway Corvette Z06 GT3.R",          ["road"],            84,  "GT3",           14.99, owned=False),
    Car(210, "BMW M8 GTE",                           ["road"],            162, "GTE",           14.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # ROAD — GT3 CUP / GT CHALLENGE
    # ═══════════════════════════════════════════════════════
    Car(175, "Porsche 911 GT3 Cup (992.2)",          ["road"],            131, "GT3 Cup",       14.99, owned=False),
    Car(178, "Ferrari 296 Challenge",                ["road"],            140, "GT Challenge",  14.99, owned=False),
    Car(190, "Lamborghini Huracán ST EVO2",          ["road"],            141, "GT Challenge",  14.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # ROAD — GT4
    # ═══════════════════════════════════════════════════════
    Car(156, "BMW M2 CS Racing",                     ["road"],            118, "GT4",           11.99, owned=False),
    Car(170, "Porsche 718 Cayman GT4 Clubsport MR",  ["road"],            118, "GT4",           14.99, owned=False),
    Car(117, "Toyota GR86",                          ["road"],            148, "GT4",           11.99, owned=False),
    Car(191, "BMW M4 GT4",                           ["road"],            118, "GT4",           11.99, owned=False),
    Car(192, "Audi R8 GT4",                          ["road"],            118, "GT4",           11.99, owned=False),
    Car(193, "Mercedes-AMG GT4",                     ["road"],            118, "GT4",           11.99, owned=False),
    Car(194, "Toyota GR Supra GT4 EVO",              ["road"],            118, "GT4",           11.99, owned=False),
    Car(195, "McLaren 570S GT4",                     ["road"],            118, "GT4",           11.99, owned=False),
    Car(196, "Lamborghini Huracán ST",               ["road"],            118, "GT4",           11.99, owned=False),
    Car(211, "Aston Martin Vantage GT4",             ["road"],            118, "GT4",           11.99, owned=False),
    Car(212, "BMW M240i Racing",                     ["road"],            118, "GT4",           11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # ROAD — TCR
    # ═══════════════════════════════════════════════════════
    Car(213, "Honda Civic Type R TCR",               ["road"],            155, "TCR",           11.99, owned=False),
    Car(214, "Hyundai Elantra N TCR",                ["road"],            155, "TCR",           11.99, owned=False),
    Car(215, "Volkswagen Golf GTI TCR",              ["road"],            155, "TCR",           11.99, owned=False),
    Car(216, "CUPRA Leon Competición",               ["road"],            155, "TCR",           11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # ROAD — GTP / LMP
    # ═══════════════════════════════════════════════════════
    Car(197, "Porsche 963 GTP",                      ["road"],            160, "GTP",           14.99, owned=False),
    Car(198, "Cadillac V-Series.R GTP",              ["road"],            160, "GTP",           14.99, owned=False),
    Car(199, "Acura ARX-06 GTP",                     ["road"],            160, "GTP",           14.99, owned=False),
    Car(200, "BMW M Hybrid V8",                      ["road"],            160, "GTP",           14.99, owned=False),
    Car(201, "Toyota GR010 Hybrid",                  ["road"],            161, "LMP1",          14.99, owned=False),
    Car(137, "Ligier JS P320",                       ["road"],            128, "LMP3",          11.99, owned=False),
    Car(202, "Ligier JS P217",                       ["road"],            127, "LMP2",          11.99, owned=False),
    Car(217, "Oreca 07",                             ["road"],            127, "LMP2",          11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # ROAD — FORMULA
    # ═══════════════════════════════════════════════════════
    Car(99,  "Dallara F4",                           ["road"],            101, "Formula",       11.99, owned=False),
    Car(67,  "Dallara F3",                           ["road"],            68,  "Formula",       11.99, owned=False),
    Car(139, "Dallara iR-01",                        ["road"],            130, "Formula",       14.99, owned=False),
    Car(205, "McLaren MP4/30",                       ["road"],            92,  "Formula",       14.99, owned=False),
    Car(218, "Williams FW31",                        ["road"],            91,  "Classic F1",    11.99, owned=False),
    Car(203, "Lotus 49",                             ["road"],            90,  "Classic F1",    11.99, owned=False),
    Car(204, "Lotus 79",                             ["road"],            90,  "Classic F1",    11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # ROAD — MX-5 / SPORTS CAR / MISC
    # ═══════════════════════════════════════════════════════
    Car(206, "Mazda MX-5 Cup 2016",                  ["road"],            53,  "MX-5 Cup",      11.99, owned=False),
    Car(23,  "Radical SR8",                          ["road"],            45,  "Sports Car",    14.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # OVAL — GRATIS CON SUSCRIPCIÓN
    # ═══════════════════════════════════════════════════════
    Car(219, "Legends Car Ford '34 Coupe",           ["oval"],            308, "Legends",       0.00,  owned=True),
    Car(220, "Street Stock",                         ["oval"],            309, "Stock Car",     0.00,  owned=True),

    # ═══════════════════════════════════════════════════════
    # OVAL — NASCAR
    # ═══════════════════════════════════════════════════════
    Car(221, "NASCAR Cup Series Chevrolet Camaro ZL1",      ["oval"],            300, "NASCAR Cup",    14.99, owned=False),
    Car(222, "NASCAR Cup Series Ford Mustang",       ["oval"],            300, "NASCAR Cup",    14.99, owned=False),
    Car(223, "NASCAR Cup Series Toyota Camry",       ["oval"],            300, "NASCAR Cup",    14.99, owned=False),
    Car(224, "NASCAR Xfinity Series Chevrolet Camaro 2018",             ["oval"],            301, "NASCAR Xfinity",11.99, owned=False),
    Car(225, "NASCAR Xfinity Series Ford Mustang 2018",          ["oval"],            301, "NASCAR Xfinity",11.99, owned=False),
    Car(226, "NASCAR Xfinity Toyota Supra",          ["oval"],            301, "NASCAR Xfinity",11.99, owned=False),
    Car(227, "NASCAR Truck Series Chevrolet Silverado",     ["oval"],            302, "NASCAR Trucks", 11.99, owned=False),
    Car(228, "NASCAR Truck Series Ford F-150",              ["oval"],            302, "NASCAR Trucks", 11.99, owned=False),
    Car(229, "NASCAR Truck Series Toyota Tundra TRD",           ["oval"],            302, "NASCAR Trucks", 11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # OVAL — INDYCAR / OPEN WHEEL
    # ═══════════════════════════════════════════════════════
    Car(230, "Dallara IR18 (IndyCar)",               ["oval", "road"],    303, "IndyCar",       14.99, owned=False),
    Car(231, "Indy Pro 2000 PM-18",                  ["oval", "road"],    304, "Indy Pro 2000", 11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # OVAL — STOCK CAR / LATE MODEL
    # ═══════════════════════════════════════════════════════
    Car(232, "ARCA Chevrolet SS",        ["oval"],            305, "ARCA",          11.99, owned=False),
    Car(233, "Late Model Stock",                 ["oval"],            306, "Late Model",    11.99, owned=False),
    Car(234, "Super Late Model",                     ["oval"],            307, "Super Late Model",14.99,owned=False),
    Car(235, "Pro Late Model",                       ["oval"],            307, "Super Late Model",11.99,owned=False),

    # ═══════════════════════════════════════════════════════
    # OVAL — MODIFIED
    # ═══════════════════════════════════════════════════════
    Car(236, "UMP Modified",                         ["oval"],            310, "Modified",      11.99, owned=False),
    Car(237, "NASCAR Whelen Tour Modified",          ["oval"],            310, "Modified",      11.99, owned=False),
    Car(238, "SK Modified Car",                          ["oval"],            310, "Modified",      11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # DIRT OVAL — SPRINT CAR
    # ═══════════════════════════════════════════════════════
    Car(240, "Sprint Car 410ci",                     ["dirt_oval"],       311, "Sprint Car",    11.99, owned=False),
    Car(241, "Sprint Car 360ci",                     ["dirt_oval"],       311, "Sprint Car",    11.99, owned=False),
    Car(242, "World of Outlaws Sprint Car",          ["dirt_oval"],       311, "Sprint Car",    11.99, owned=False),
    Car(243, "High Limit Sprint Car",                ["dirt_oval"],       311, "Sprint Car",    11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # DIRT OVAL — LATE MODEL / MODIFIED
    # ═══════════════════════════════════════════════════════
    Car(244, "DIRTcar UMP Modified",                 ["dirt_oval"],       312, "Dirt Modified", 11.99, owned=False),
    Car(245, "Super DIRTcar Big Block Modified",     ["dirt_oval"],       312, "Dirt Modified", 11.99, owned=False),
    Car(246, "Dirt Late Model",                      ["dirt_oval"],       313, "Dirt Late Model",11.99,owned=False),
    Car(247, "World of Outlaws Late Model",          ["dirt_oval"],       313, "Dirt Late Model",11.99,owned=False),
    Car(248, "DIRTcar Street Stock",                 ["dirt_oval"],       309, "Stock Car",     11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # DIRT OVAL — MIDGET
    # ═══════════════════════════════════════════════════════
    Car(249, "Dirt Midget",                          ["dirt_oval"],       314, "Dirt Midget",   11.99, owned=False),
    Car(250, "Micro Sprint Car",                     ["dirt_oval"],       314, "Dirt Midget",   11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # DIRT ROAD — RALLYCROSS
    # ═══════════════════════════════════════════════════════
    Car(251, "Subaru WRX STi",                       ["dirt_road"],       315, "Rallycross",    11.99, owned=False),
    Car(252, "Volkswagen Beetle Rallycross",         ["dirt_road"],       315, "Rallycross",    11.99, owned=False),

    # ═══════════════════════════════════════════════════════
    # CATÁLOGO COMPLETO — agregados desde el catálogo oficial de iRacing
    # (se irán actualizando con precios/IDs reales vía /api/catalog/sync)
    # ═══════════════════════════════════════════════════════

    # ── NASCAR ──
    Car(253, "NASCAR Truck RAM", ["oval"], 302, "NASCAR Trucks", 11.99, owned=False),
    Car(254, "Next Gen NASCAR Cup Series Chevrolet Camaro ZL1", ["oval"], 300, "NASCAR Cup", 11.99, owned=False),
    Car(255, "Next Gen NASCAR Cup Series Ford Mustang", ["oval"], 300, "NASCAR Cup", 11.99, owned=False),
    Car(256, "Next Gen NASCAR Cup Series Toyota Camry", ["oval"], 300, "NASCAR Cup", 11.99, owned=False),
    Car(257, "NASCAR O'Reilly Chevrolet Camaro", ["oval"], 300, "NASCAR Cup", 11.99, owned=False),
    Car(258, "NASCAR O'Reilly Ford Mustang", ["oval"], 300, "NASCAR Cup", 11.99, owned=False),
    Car(259, "NASCAR O'Reilly Toyota Supra", ["oval"], 300, "NASCAR Cup", 11.99, owned=False),
    Car(260, "ARCA Ford Mustang", ["oval"], 305, "ARCA", 11.99, owned=False),
    Car(261, "ARCA Toyota Camry", ["oval"], 305, "ARCA", 11.99, owned=False),
    Car(262, "Gen 4 Chevrolet Monte Carlo - 2003", ["oval"], 326, "NASCAR Cup Legacy", 9.99, owned=False),
    Car(263, "Gen 4 Ford Taurus - 2003", ["oval"], 326, "NASCAR Cup Legacy", 9.99, owned=False),
    Car(264, "NASCAR Legends Buick LeSabre - 1987", ["oval"], 308, "Legends", 9.99, owned=False),
    Car(265, "NASCAR Legends Ford Thunderbird - 1987", ["oval"], 308, "Legends", 9.99, owned=False),
    Car(266, "NASCAR Legends Pontiac Grand Prix - 1987", ["oval"], 308, "Legends", 9.99, owned=False),
    Car(267, "NASCAR Legends Chevrolet Monte Carlo - 1987", ["oval"], 308, "Legends", 9.99, owned=False),
    Car(268, "SRX", ["oval"], 330, "SRX", 11.99, owned=False),
    Car(269, "Street Stock - Panther", ["oval"], 332, "Street Stock", 0.0, owned=True),
    Car(270, "Street Stock - Eagle", ["oval"], 332, "Street Stock", 0.0, owned=True),
    Car(271, "Street Stock - Casino", ["oval"], 332, "Street Stock", 0.0, owned=True),
    Car(272, "Mini Stock", ["oval"], 325, "Mini Stock", 0.0, owned=True),
    Car(273, "Legends Ford '34 Coupe", ["oval"], 308, "Legends", 9.99, owned=False),
    Car(274, "NASCAR Cup Series Ford Fusion", ["oval"], 326, "NASCAR Cup Legacy", 9.99, owned=False),
    Car(275, "NASCAR Chevrolet SS Cup Car", ["oval"], 326, "NASCAR Cup Legacy", 9.99, owned=False),
    Car(276, "NASCAR Gen 4 Cup", ["oval"], 326, "NASCAR Cup Legacy", 9.99, owned=False),
    Car(277, "NASCAR Xfinity Series Toyota Camry 2018", ["oval"], 301, "NASCAR Xfinity", 11.99, owned=False),
    Car(278, "NASCAR Chevrolet Impala SS COT circa 2013", ["oval"], 326, "NASCAR Cup Legacy", 9.99, owned=False),
    Car(279, "NASCAR Xfinity Series Chevrolet Impala SS - Circa 2011", ["oval"], 301, "NASCAR Xfinity", 11.99, owned=False),
    Car(280, "NASCAR Truck Chevrolet Silverado - 2008", ["oval"], 302, "NASCAR Trucks", 11.99, owned=False),

    # ── Sports Car ──
    Car(281, "Audi RS3 LMS Gen2 TCR", ["road"], 155, "TCR", 11.99, owned=False),
    Car(282, "Aston Martin Vantage GT3 EVO", ["road"], 84, "GT3", 14.99, owned=False),
    Car(283, "Ford Mustang GT4", ["road"], 118, "GT4", 11.99, owned=False),
    Car(284, "Acura NSX GT3 EVO 22", ["road"], 84, "GT3", 14.99, owned=False),
    Car(285, "BMW M4 GT3 EVO", ["road"], 84, "GT3", 14.99, owned=False),
    Car(286, "Chevrolet Corvette Z06 GT3.R", ["road"], 84, "GT3", 14.99, owned=False),
    Car(287, "Porsche 911 GT3 R (992)", ["road"], 84, "GT3", 14.99, owned=False),
    Car(288, "Porsche 911 Cup (992.2)", ["road"], 131, "GT3 Cup", 14.99, owned=False),
    Car(289, "Supercars Chevrolet Camaro Gen 3", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(290, "Supercars Ford Mustang Gen 3", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(291, "BMW M4 G82 GT4 Evo", ["road"], 118, "GT4", 11.99, owned=False),
    Car(292, "Porsche 718 Cayman GT4 Clubsport", ["road"], 118, "GT4", 11.99, owned=False),
    Car(293, "Audi RS 3 LMS TCR", ["road"], 155, "TCR", 11.99, owned=False),
    Car(294, "Hyundai Veloster N TCR", ["road"], 155, "TCR", 11.99, owned=False),
    Car(295, "Renault Clio R.S. V", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(296, "Stockcar Brasil Chevrolet Cruze", ["road"], 331, "Stock Car Brasil", 11.99, owned=False),
    Car(297, "Stockcar Brasil Toyota Corolla", ["road"], 331, "Stock Car Brasil", 11.99, owned=False),
    Car(298, "Chevrolet Corvette C8.R", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(299, "Ferrari 488 GTE", ["road"], 162, "GTE", 14.99, owned=False),
    Car(300, "Ford GT GTE", ["road"], 162, "GTE", 14.99, owned=False),
    Car(301, "Porsche 911 RSR", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(302, "Porsche Mission R", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(303, "Chevrolet Corvette C6.R", ["road"], 162, "GTE", 14.99, owned=False),
    Car(304, "Aston Martin DBR9 GT1", ["road"], 162, "GTE", 14.99, owned=False),
    Car(305, "Ford Mustang FR500S", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(306, "Audi 90 GTO", ["road"], 70, "Touring Car", 0.0, owned=True),
    Car(307, "Ferrari 488 GT3", ["road"], 84, "GT3", 14.99, owned=False),
    Car(308, "McLaren MP4-12C GT3", ["road"], 84, "GT3", 14.99, owned=False),
    Car(309, "BMW Z4 GT3", ["road"], 84, "GT3", 14.99, owned=False),
    Car(310, "Ford GT-R", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(311, "Audi R8 LMS GT3", ["road"], 84, "GT3", 14.99, owned=False),
    Car(312, "Mercedes-AMG GT3", ["road"], 84, "GT3", 14.99, owned=False),
    Car(313, "Supercars Ford Mustang GT", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(314, "Supercars Holden ZB Commodore", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(315, "V8 Supercar Holden VF Commodore - 2014", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(316, "V8 Supercar Ford FG Falcon - 2014", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(317, "V8 Supercar Ford Falcon - 2009", ["road"], 334, "Supercars", 11.99, owned=False),
    Car(318, "BMW M4 F82 GT4 - 2018", ["road"], 118, "GT4", 11.99, owned=False),
    Car(319, "Ruf Rt 12 R", ["road"], 140, "GT Challenge", 14.99, owned=False),
    Car(320, "Volkswagen Jetta TDi", ["road"], 70, "Touring Car", 0.0, owned=True),
    Car(321, "Mazda MX-5 Roadster - 2010", ["road"], 53, "MX-5 Cup", 11.99, owned=False),

    # ── Prototype ──
    Car(322, "Ferrari 499P", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(323, "Dallara P217 LMP2", ["road"], 127, "LMP2", 11.99, owned=False),
    Car(324, "Radical SR10", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(325, "Porsche 919 LMP1", ["road"], 160, "GTP", 14.99, owned=False),
    Car(326, "Audi R18 LMP1", ["road"], 160, "GTP", 14.99, owned=False),
    Car(327, "Chevrolet Corvette C7 Daytona Prototype", ["road"], 160, "GTP", 14.99, owned=False),
    Car(328, "HPD ARX 01c", ["road"], 45, "Sports Car", 11.99, owned=False),
    Car(329, "Riley Mk XX Daytona Prototype", ["road"], 160, "GTP", 14.99, owned=False),
    Car(330, "Nissan GTP ZX-T", ["road"], 160, "GTP", 14.99, owned=False),
    Car(331, "Radical SR8 V8", ["road"], 128, "LMP3", 11.99, owned=False),

    # ── Formula ──
    Car(332, "Dallara IL-15", ["road"], 63, "Formula", 11.99, owned=False),
    Car(333, "Super Formula Lights", ["road"], 333, "Super Formula", 11.99, owned=False),
    Car(334, "Super Formula SF23 - Honda", ["road"], 333, "Super Formula", 11.99, owned=False),
    Car(335, "Super Formula SF23 - Toyota", ["road"], 333, "Super Formula", 11.99, owned=False),
    Car(336, "Mercedes-AMG F1 W13 E Performance", ["road"], 320, "Formula 1", 14.99, owned=False),
    Car(337, "Mercedes-AMG F1 W12 E Performance", ["road"], 320, "Formula 1", 14.99, owned=False),
    Car(338, "Indy Pro 2000", ["road"], 303, "IndyCar", 14.99, owned=False),
    Car(339, "FIA F4", ["road"], 321, "Formula 4", 11.99, owned=False),
    Car(340, "Formula Vee", ["road"], 323, "Formula Vee", 9.99, owned=False),
    Car(341, "USF2000", ["road"], 329, "Road to Indy", 11.99, owned=False),
    Car(342, "McLaren Honda MP4-30", ["road"], 63, "Formula", 11.99, owned=False),
    Car(343, "Williams-Toyota FW31", ["road"], 63, "Formula", 11.99, owned=False),
    Car(344, "Dallara IR18 INDYCAR", ["road"], 303, "IndyCar", 14.99, owned=False),
    Car(345, "Formula Renault 3.5", ["road"], 322, "Formula Renault", 11.99, owned=False),
    Car(346, "Formula Renault 2.0", ["road"], 322, "Formula Renault", 11.99, owned=False),
    Car(347, "Pro Mazda", ["road"], 329, "Road to Indy", 11.99, owned=False),
    Car(348, "C&R Racing Silver Crown Car", ["road"], 63, "Formula", 11.99, owned=False),
    Car(349, "Sprint Car", ["road"], 63, "Formula", 11.99, owned=False),
    Car(350, "Dallara DW12", ["road"], 303, "IndyCar", 14.99, owned=False),
    Car(351, "Dallara IR05 - Circa 2009", ["road"], 63, "Formula", 11.99, owned=False),

    # ── Dirt Oval ──
    Car(352, "Mini Stock - Dirt", ["dirt_oval"], 325, "Mini Stock", 0.0, owned=True),
    Car(353, "DIRTcar 358 Small Block Modified", ["dirt_oval"], 312, "Dirt Modified", 11.99, owned=False),
    Car(354, "World of Outlaws 410 Sprint Car", ["dirt_oval"], 311, "Sprint Car", 11.99, owned=False),
    Car(355, "DIRTcar 360 Sprint Car", ["dirt_oval"], 311, "Sprint Car", 11.99, owned=False),
    Car(356, "DIRTcar 305 Sprint Car", ["dirt_oval"], 311, "Sprint Car", 11.99, owned=False),
    Car(357, "Dirt Micro Sprint", ["dirt_oval"], 324, "Micro Sprint", 9.99, owned=False),
    Car(358, "Dirt Outlaw Micro Sprint - Winged", ["dirt_oval"], 324, "Micro Sprint", 9.99, owned=False),
    Car(359, "Dirt Micro Sprint - Non Winged", ["dirt_oval"], 324, "Micro Sprint", 9.99, owned=False),
    Car(360, "Dirt Outlaw Micro Sprint - Non Winged", ["dirt_oval"], 324, "Micro Sprint", 9.99, owned=False),
    Car(361, "World of Outlaws Super Late Model", ["dirt_oval"], 313, "Dirt Late Model", 11.99, owned=False),
    Car(362, "DIRTcar Pro Late Model", ["dirt_oval"], 313, "Dirt Late Model", 11.99, owned=False),
    Car(363, "DIRTcar Limited Late Model", ["dirt_oval"], 313, "Dirt Late Model", 11.99, owned=False),
    Car(364, "USAC 410 Sprint Car", ["dirt_oval"], 311, "Sprint Car", 11.99, owned=False),
    Car(365, "USAC 360 Sprint Car", ["dirt_oval"], 311, "Sprint Car", 11.99, owned=False),
    Car(366, "NASCAR Truck Series Dirt Chevrolet Silverado", ["dirt_oval"], 327, "NASCAR Trucks Dirt", 11.99, owned=False),
    Car(367, "NASCAR Truck Series Dirt Toyota Tundra TRD", ["dirt_oval"], 327, "NASCAR Trucks Dirt", 11.99, owned=False),
    Car(368, "Dirt Legends Ford '34 Coupe", ["dirt_oval"], 308, "Legends", 9.99, owned=False),
    Car(369, "NASCAR Truck Series Dirt Ford F-150", ["dirt_oval"], 327, "NASCAR Trucks Dirt", 11.99, owned=False),
    Car(370, "Dirt Street Stock", ["dirt_oval"], 332, "Street Stock", 9.99, owned=False),

    # ── Rallycross ──
    Car(371, "FIA Cross Car", ["dirt_road"], 315, "Rallycross", 11.99, owned=False),
    Car(372, "Ford Fiesta RS WRC", ["dirt_road"], 315, "Rallycross", 11.99, owned=False),
    Car(373, "VW Beetle", ["dirt_road"], 315, "Rallycross", 11.99, owned=False),
    Car(374, "VW Beetle Lite", ["dirt_road"], 315, "Rallycross", 11.99, owned=False),

    # ── Off-Road ──
    Car(375, "Lucas Oil Off Road Pro 2 Truck", ["dirt_road"], 328, "Off-Road Truck", 11.99, owned=False),
    Car(376, "Lucas Oil Off Road Pro 4 Truck", ["dirt_road"], 328, "Off-Road Truck", 11.99, owned=False),
    Car(377, "Lucas Oil Off-Road Pro 2 Lite Truck", ["dirt_road"], 328, "Off-Road Truck", 11.99, owned=False),
]

# ── Pistas ─────────────────────────────────────────────────────────────────────
# owned=True solo en pistas incluidas gratis con la suscripción de iRacing.
# Configurá las tuyas desde Configuración → Pistas que tengo.
MOCK_TRACKS: list[Track] = [
    # ── Incluidas con iRacing (gratis) ────────────────────────────────────────
    Track(5,  "Lime Rock Park",                       "Lakeville",      "USA",
          [TrackConfig(5,   "Grand Prix",          True,  0.0),
           TrackConfig(501, "Chicanes",            True,  0.0),
           TrackConfig(502, "West Bend Chicane",   True,  0.0)],
          owned=True,  price=0.0),

    Track(6,  "Mid-Ohio Sports Car Course",           "Lexington",      "USA",
          [TrackConfig(6,   "Full Course",         True,  0.0),
           TrackConfig(601, "Short",               True,  0.0)],
          owned=True,  price=0.0),

    Track(15, "Summit Point Raceway",                 "Summit Point",   "USA",
          [TrackConfig(15,  "Summit Point",        True,  0.0),
           TrackConfig(151, "Jefferson",           True,  0.0)],
          owned=True,  price=0.0),

    Track(17, "Virginia International Raceway",       "Alton",          "USA",
          [TrackConfig(17,  "Full Course",         True,  0.0),
           TrackConfig(171, "Grand East",          True,  0.0),
           TrackConfig(172, "North Course",        True,  0.0),
           TrackConfig(173, "Patriot",             True,  0.0)],
          owned=True,  price=0.0),

    Track(18, "Watkins Glen International",           "Watkins Glen",   "USA",
          [TrackConfig(18,  "Boot",                True,  0.0),
           TrackConfig(181, "Short",               True,  0.0),
           TrackConfig(182, "Classic Boot",        True,  0.0)],
          owned=True,  price=0.0),

    Track(37, "Nürburgring GP",                      "Nürburg",        "Germany",
          [TrackConfig(37,  "Grand Prix",          True,  0.0),
           TrackConfig(371, "Sprint",              True,  0.0)],
          owned=True,  price=0.0),

    Track(43, "Daytona International Speedway",       "Daytona",        "USA",
          [TrackConfig(43,  "Road Course",         True,  0.0)],
          owned=True,  price=0.0),

    Track(46, "Road Atlanta",                         "Braselton",      "USA",
          [TrackConfig(46,  "Full Course",         True,  0.0)],
          owned=True,  price=0.0),

    # ── De pago — marcalas como propias en Configuración ─────────────────────
    Track(1,  "Autódromo José Carlos Pace",           "São Paulo",      "Brazil",
          [TrackConfig(1,   "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(2,  "Autodromo Nazionale Monza",             "Monza",          "Italy",
          [TrackConfig(2,   "Grand Prix",          False, 14.99),
           TrackConfig(21,  "Junior",              False, 0.0)],
          owned=False, price=14.99),

    Track(3,  "Circuit de Spa-Francorchamps",         "Stavelot",       "Belgium",
          [TrackConfig(3,   "Spa",                 False, 14.99)],
          owned=False, price=14.99),

    Track(4,  "Circuit Zolder",                       "Zolder",         "Belgium",
          [TrackConfig(4,   "Zolder",              False, 14.99)],
          owned=False, price=14.99),

    Track(7,  "Misano World Circuit",                 "Misano",         "Italy",
          [TrackConfig(7,   "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(8,  "Motorsport Arena Oschersleben",        "Oschersleben",   "Germany",
          [TrackConfig(8,   "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(9,  "Mount Panorama Circuit",               "Bathurst",       "Australia",
          [TrackConfig(9,   "Mount Panorama",      False, 14.99)],
          owned=False, price=14.99),

    Track(10, "Okayama International Circuit",        "Okayama",        "Japan",
          [TrackConfig(10,  "Full Course",         False, 14.99),
           TrackConfig(100, "Short",               False, 0.0)],
          owned=False, price=14.99),

    Track(11, "Oran Park Raceway",                    "Narellan",       "Australia",
          [TrackConfig(11,  "Full",                False, 14.99)],
          owned=False, price=14.99),

    Track(12, "Oulton Park Circuit",                  "Oulton Park",    "UK",
          [TrackConfig(12,  "International",       False, 14.99),
           TrackConfig(121, "Fosters",             False, 0.0),
           TrackConfig(122, "Island",              False, 0.0)],
          owned=False, price=14.99),

    Track(13, "Road America",                         "Elkhart Lake",   "USA",
          [TrackConfig(13,  "Full Course",         False, 11.99)],
          owned=False, price=11.99),

    Track(14, "Snetterton Circuit",                   "Norfolk",        "UK",
          [TrackConfig(14,  "300",                 False, 14.99),
           TrackConfig(141, "200",                 False, 0.0),
           TrackConfig(142, "100",                 False, 0.0)],
          owned=False, price=14.99),

    Track(16, "Tsukuba Circuit",                      "Tsukuba",        "Japan",
          [TrackConfig(16,  "2000 Full",           False, 14.99)],
          owned=False, price=14.99),

    Track(19, "WeatherTech Raceway Laguna Seca",      "Salinas",        "USA",
          [TrackConfig(19,  "Full Course",         False, 11.99)],
          owned=False, price=11.99),

    Track(20, "Winton Motor Raceway",                 "Winton",         "Australia",
          [TrackConfig(20,  "National Circuit",    False, 14.99)],
          owned=False, price=14.99),

    Track(21, "Circuit de Lédenon",                  "Lédenon",        "France",
          [TrackConfig(210, "Lédenon",             False, 14.99)],
          owned=False, price=14.99),

    Track(22, "Circuito de Navarra",                  "Navarra",        "Spain",
          [TrackConfig(22,  "Speed Circuit",       False, 14.99),
           TrackConfig(221, "Speed Circuit Medium",False, 0.0)],
          owned=False, price=14.99),

    Track(23, "Rudskogen Motorsenter",                "Rudskogen",      "Norway",
          [TrackConfig(23,  "Full",                False, 14.99)],
          owned=False, price=14.99),

    Track(24, "Charlotte Motor Speedway",             "Concord",        "USA",
          [TrackConfig(24,  "Oval",                False, 14.99),
           TrackConfig(241, "Roval 2025",          False, 0.0)],
          owned=False, price=14.99),

    Track(30, "Silverstone Circuit",                  "Silverstone",    "UK",
          [TrackConfig(30,  "Grand Prix",          False, 14.99),
           TrackConfig(301, "National",            False, 0.0)],
          owned=False, price=14.99),

    Track(31, "Brands Hatch Circuit",                 "Swanley",        "UK",
          [TrackConfig(31,  "Grand Prix",          False, 14.99),
           TrackConfig(311, "Indy",                False, 0.0)],
          owned=False, price=14.99),

    Track(32, "Circuit de Barcelona-Catalunya",       "Barcelona",      "Spain",
          [TrackConfig(32,  "Grand Prix",          False, 14.99),
           TrackConfig(321, "National",            False, 0.0)],
          owned=False, price=14.99),

    Track(33, "Autodromo Enzo e Dino Ferrari (Imola)","Imola",          "Italy",
          [TrackConfig(33,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(34, "Hungaroring",                          "Budapest",       "Hungary",
          [TrackConfig(34,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(35, "Circuit Zandvoort",                    "Zandvoort",      "Netherlands",
          [TrackConfig(35,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(36, "Hockenheimring",                       "Hockenheim",     "Germany",
          [TrackConfig(36,  "Grand Prix",          False, 14.99),
           TrackConfig(361, "Short",               False, 0.0)],
          owned=False, price=14.99),

    Track(38, "Suzuka International Racing Course",   "Suzuka",         "Japan",
          [TrackConfig(38,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(39, "Autodromo Internacional do Algarve",   "Portimão",       "Portugal",
          [TrackConfig(39,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(40, "Autodromo Internazionale del Mugello", "Mugello",        "Italy",
          [TrackConfig(40,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(41, "Circuit des 24 Heures du Mans",        "Le Mans",        "France",
          [TrackConfig(41,  "24 Heures du Mans",   False, 14.99)],
          owned=False, price=14.99),

    Track(42, "Sebring International Raceway",        "Sebring",        "USA",
          [TrackConfig(42,  "International",       False, 11.99),
           TrackConfig(421, "Short",               False, 0.0)],
          owned=False, price=11.99),

    Track(44, "Canadian Tire Motorsport Park",        "Bowmanville",    "Canada",
          [TrackConfig(44,  "Grand Prix",          False, 11.99)],
          owned=False, price=11.99),

    Track(45, "Nürburgring Combined",                "Nürburg",        "Germany",
          [TrackConfig(45,  "Gesamtstrecke 24h",   False, 14.99)],
          owned=False, price=14.99),

    Track(47, "St. Petersburg Grand Prix",            "St. Petersburg", "USA",
          [TrackConfig(47,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(48, "Adelaide Street Circuit",              "Adelaide",       "Australia",
          [TrackConfig(48,  "Adelaide",            False, 14.99)],
          owned=False, price=14.99),

    Track(49, "Barber Motorsports Park",              "Leeds",          "USA",
          [TrackConfig(49,  "Full",                False, 14.99)],
          owned=False, price=14.99),

    Track(50, "Long Beach Street Circuit",            "Long Beach",     "USA",
          [TrackConfig(50,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(51, "Donington Park Racing Circuit",        "Donington",      "UK",
          [TrackConfig(51,  "Grand Prix",          False, 14.99),
           TrackConfig(511, "National",            False, 0.0)],
          owned=False, price=14.99),

    Track(52, "Circuit of the Americas",              "Austin",         "USA",
          [TrackConfig(52,  "Grand Prix",          False, 14.99),
           TrackConfig(521, "NASCAR West",         False, 0.0)],
          owned=False, price=14.99),

    Track(53, "Fuji International Speedway",          "Oyama",          "Japan",
          [TrackConfig(53,  "Grand Prix",          False, 14.99),
           TrackConfig(531, "No Chicane",          False, 0.0)],
          owned=False, price=14.99),

    Track(54, "Willow Springs International Raceway", "Rosamond",       "USA",
          [TrackConfig(54,  "Big Willow",          False, 14.99)],
          owned=False, price=14.99),

    Track(55, "Circuit de Nevers Magny-Cours",        "Magny-Cours",    "France",
          [TrackConfig(55,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(56, "Thruxton Circuit",                     "Thruxton",       "UK",
          [TrackConfig(56,  "Thruxton",            False, 14.99)],
          owned=False, price=14.99),

    Track(57, "Miami International Autodrome",        "Miami",          "USA",
          [TrackConfig(57,  "Grand Prix",          False, 14.99),
           TrackConfig(571, "Extended Marina Loop",False, 0.0)],
          owned=False, price=14.99),

    Track(58, "Red Bull Ring",                        "Spielberg",      "Austria",
          [TrackConfig(58,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(59, "Phillip Island Circuit",               "Phillip Island", "Australia",
          [TrackConfig(59,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(60, "Mobility Resort Motegi",               "Motegi",         "Japan",
          [TrackConfig(60,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(61, "Indianapolis Motor Speedway",          "Indianapolis",   "USA",
          [TrackConfig(61,  "Road Course",         False, 14.99)],
          owned=False, price=14.99),

    Track(62, "MotorLand Aragón",                    "Aragón",          "Spain",
          [TrackConfig(62,  "Motorcycle Grand Prix", False, 14.99)],
          owned=False, price=14.99),

    Track(63, "Nürburgring Nordschleife",            "Nürburg",         "Germany",
          [TrackConfig(63,  "Industriefahrten",    False, 14.99)],
          owned=False, price=14.99),

    Track(64, "Sonoma Raceway",                       "Sonoma",          "USA",
          [TrackConfig(64,  "Sportscar",           False, 11.99),
           TrackConfig(641, "Sportscar Alt",       False, 0.0)],
          owned=False, price=11.99),

    Track(65, "Autódromo Hermanos Rodríguez",        "Mexico City",     "Mexico",
          [TrackConfig(65,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(67, "Sachsenring",                          "Hohenstein-Ernstthal", "Germany",
          [TrackConfig(67,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(68, "Circuit Gilles Villeneuve",            "Montreal",        "Canada",
          [TrackConfig(68,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    # ── Más pistas del catálogo iRacing ──────────────────────────────────────
    Track(70, "Autodromo di Monza (Historic)",        "Monza",           "Italy",
          [TrackConfig(70,  "1966",                False, 14.99)],
          owned=False, price=14.99),

    Track(71, "Circuit de la Sarthe (Test Drive)",   "Le Mans",          "France",
          [TrackConfig(71,  "2022 Test Drive",     False, 14.99)],
          owned=False, price=14.99),

    Track(72, "Kyalami Grand Prix Circuit",          "Midrand",          "South Africa",
          [TrackConfig(72,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(73, "Interlagos Historic",                 "São Paulo",        "Brazil",
          [TrackConfig(73,  "Historic",            False, 14.99)],
          owned=False, price=14.99),

    Track(74, "Circuit de Monaco",                   "Monte Carlo",      "Monaco",
          [TrackConfig(74,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(75, "Silverstone (Historic)",              "Silverstone",       "UK",
          [TrackConfig(75,  "Classic",             False, 14.99)],
          owned=False, price=14.99),

    Track(76, "Knockhill Racing Circuit",            "Dunfermline",       "UK",
          [TrackConfig(76,  "National",            False, 14.99),
           TrackConfig(761, "National Reverse",    False, 0.0)],
          owned=False, price=14.99),

    Track(77, "Spa 1966",                            "Stavelot",          "Belgium",
          [TrackConfig(77,  "Historic",            False, 14.99)],
          owned=False, price=14.99),

    Track(78, "Tsukuba Circuit (Wet)",               "Tsukuba",           "Japan",
          [TrackConfig(78,  "2000 Full Wet",       False, 14.99)],
          owned=False, price=14.99),

    Track(79, "Circuit Park Zandvoort (Historic)",  "Zandvoort",          "Netherlands",
          [TrackConfig(79,  "1987",                False, 14.99)],
          owned=False, price=14.99),

    Track(80, "WeatherTech Raceway Laguna Seca (Wet)","Salinas",          "USA",
          [TrackConfig(80,  "Full Course Wet",     False, 11.99)],
          owned=False, price=11.99),

    Track(81, "Lime Rock Park (Night)",              "Lakeville",          "USA",
          [TrackConfig(81,  "Grand Prix Night",    False, 0.0)],
          owned=False, price=0.0),

    Track(82, "Autodromo Internazionale del Mugello (Wet)","Mugello",      "Italy",
          [TrackConfig(82,  "Grand Prix Wet",      False, 14.99)],
          owned=False, price=14.99),

    Track(83, "Circuito de Jerez",                   "Jerez de la Frontera","Spain",
          [TrackConfig(83,  "Angel Nieto",         False, 14.99)],
          owned=False, price=14.99),

    Track(84, "Hungaroring (Historic)",              "Budapest",           "Hungary",
          [TrackConfig(84,  "1986",                False, 14.99)],
          owned=False, price=14.99),

    Track(85, "Autodromo de Interlagos (Wet)",       "São Paulo",          "Brazil",
          [TrackConfig(85,  "Grand Prix Wet",      False, 14.99)],
          owned=False, price=14.99),

    Track(86, "Phoenix Raceway",                     "Avondale",           "USA",
          [TrackConfig(86,  "Road Course",         False, 14.99)],
          owned=False, price=14.99),

    Track(87, "Autodromo Nazionale Monza (Wet)",     "Monza",              "Italy",
          [TrackConfig(87,  "Grand Prix Wet",      False, 14.99)],
          owned=False, price=14.99),

    Track(88, "Okayama International Circuit (Wet)","Okayama",             "Japan",
          [TrackConfig(88,  "Full Course Wet",     False, 14.99)],
          owned=False, price=14.99),

    Track(89, "Twin Ring Motegi",                    "Motegi",             "Japan",
          [TrackConfig(89,  "Road Course",         False, 14.99),
           TrackConfig(891, "East Short Course",   False, 0.0)],
          owned=False, price=14.99),

    Track(90, "Baskerville Raceway",                 "Baskerville",        "Australia",
          [TrackConfig(90,  "Grand Prix",          False, 14.99)],
          owned=False, price=14.99),

    Track(91, "Sebring International Raceway (Wet)", "Sebring",            "USA",
          [TrackConfig(91,  "International Wet",   False, 11.99)],
          owned=False, price=11.99),

    Track(92, "Watkins Glen International (Wet)",    "Watkins Glen",       "USA",
          [TrackConfig(92,  "Boot Wet",            False, 0.0)],
          owned=False, price=0.0),

    Track(93, "Circuit of the Americas (Wet)",       "Austin",             "USA",
          [TrackConfig(93,  "Grand Prix Wet",      False, 14.99)],
          owned=False, price=14.99),

    Track(94, "Autodromo International do Algarve (Wet)","Portimão",       "Portugal",
          [TrackConfig(94,  "Grand Prix Wet",      False, 14.99)],
          owned=False, price=14.99),

    Track(95, "Brands Hatch (Wet)",                  "Swanley",            "UK",
          [TrackConfig(95,  "Grand Prix Wet",      False, 14.99)],
          owned=False, price=14.99),

    Track(96, "Road America (Wet)",                  "Elkhart Lake",       "USA",
          [TrackConfig(96,  "Full Course Wet",     False, 11.99)],
          owned=False, price=11.99),

    Track(97, "Mount Panorama Circuit (Wet)",        "Bathurst",           "Australia",
          [TrackConfig(97,  "Mount Panorama Wet",  False, 14.99)],
          owned=False, price=14.99),

    Track(98, "Spa-Francorchamps (Wet)",             "Stavelot",           "Belgium",
          [TrackConfig(98,  "Spa Wet",             False, 14.99)],
          owned=False, price=14.99),

    Track(99, "Nürburgring Nordschleife (24h)",     "Nürburg",             "Germany",
          [TrackConfig(99,  "24h",                 False, 14.99)],
          owned=False, price=14.99),

    # ── Catálogo completo — agregadas desde el catálogo oficial de iRacing ──
    Track(100, "Portland International Raceway", "", "USA", [], owned=False, price=9.99),
    Track(101, "Sandown International Motor Raceway", "", "Australia", [], owned=False, price=9.99),
    Track(102, "LA Coliseum", "", "USA", [], owned=False, price=9.99),
    Track(103, "Bark River International Raceway", "", "USA", [], owned=False, price=9.99),
    Track(104, "Cedar Lake Speedway", "", "USA", [], owned=False, price=9.99),
    Track(105, "Chicago Street Course", "", "USA", [], owned=False, price=9.99),
    Track(106, "Crandon International Raceway", "", "USA", [], owned=False, price=9.99),
    Track(107, "Mount Washington Auto Road", "", "USA", [], owned=False, price=9.99),
    Track(108, "Nashville Fairgrounds Speedway", "", "USA", [], owned=False, price=9.99),
    Track(109, "Firebird Motorsports Park", "", "USA", [], owned=False, price=9.99),
    Track(110, "Wild West Motorsports Park", "", "USA", [], owned=False, price=9.99),
    Track(111, "Kokomo Speedway", "", "USA", [], owned=False, price=9.99),
    Track(112, "Detroit Grand Prix at Belle Isle", "", "USA", [], owned=False, price=9.99),
    Track(113, "Myrtle Beach Speedway", "", "USA", [], owned=False, price=9.99),
    Track(114, "Talladega Superspeedway", "", "USA", [], owned=False, price=9.99),
    Track(115, "Volusia Speedway Park", "", "USA", [], owned=False, price=9.99),
    Track(116, "Limaland Motorsports Park", "", "USA", [], owned=False, price=9.99),
    Track(117, "Silverstone Circuit - 2008", "", "UK", [], owned=False, price=9.99),
    Track(118, "Lanier National Speedway - Dirt", "", "USA", [], owned=False, price=9.99),
    Track(119, "Thompson Speedway Motorsports Park", "", "USA", [], owned=False, price=9.99),
    Track(120, "The Milwaukee Mile", "", "USA", [], owned=False, price=9.99),
    Track(121, "Las Vegas Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(122, "New Hampshire Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(123, "Chicagoland Speedway", "", "USA", [], owned=False, price=9.99),
    Track(124, "Stafford Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(125, "Homestead Miami Speedway", "", "USA", [], owned=False, price=9.99),
    Track(126, "Irwindale Speedway", "", "USA", [], owned=False, price=9.99),
    Track(127, "Langley Speedway", "", "USA", [], owned=False, price=9.99),
    Track(128, "New Jersey Motorsports Park", "", "USA", [], owned=False, price=9.99),
    Track(129, "Shell V-Power Motorsports Park at The Bend", "", "Australia", [], owned=False, price=9.99),
    Track(130, "Huset's Speedway", "", "USA", [], owned=False, price=9.99),
    Track(131, "Cadwell Park Circuit", "", "UK", [], owned=False, price=9.99),
    Track(132, "Oswego Speedway", "", "USA", [], owned=False, price=9.99),
    Track(133, "Millbridge Speedway", "", "USA", [], owned=False, price=9.99),
    Track(134, "Slinger Speedway", "", "USA", [], owned=False, price=9.99),
    Track(135, "Kevin Harvick's Kern Raceway", "", "USA", [], owned=False, price=9.99),
    Track(136, "Port Royal Speedway", "", "USA", [], owned=False, price=9.99),
    Track(137, "Federated Auto Parts Raceway at I-55", "", "USA", [], owned=False, price=9.99),
    Track(138, "Lincoln Speedway", "", "USA", [], owned=False, price=9.99),
    Track(139, "Lucas Oil Speedway", "", "USA", [], owned=False, price=9.99),
    Track(140, "Hickory Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(141, "Lånkebanen (HellRX)", "", "Norway", [], owned=False, price=9.99),
    Track(142, "iRacing Superspeedway", "", "—", [], owned=True, price=0.0),
    Track(143, "Nashville Superspeedway", "", "USA", [], owned=False, price=9.99),
    Track(144, "North Wilkesboro Speedway", "", "USA", [], owned=False, price=9.99),
    Track(145, "Texas Motor Speedway - 2009", "", "USA", [], owned=False, price=9.99),
    Track(146, "Weedsport Speedway", "", "USA", [], owned=False, price=9.99),
    Track(147, "World Wide Technology Raceway", "", "USA", [], owned=False, price=9.99),
    Track(148, "Lernerville Speedway", "", "USA", [], owned=False, price=9.99),
    Track(149, "Chili Bowl", "", "USA", [], owned=False, price=9.99),
    Track(150, "Bristol Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(151, "Pocono Raceway", "", "USA", [], owned=False, price=9.99),
    Track(152, "Southern National Motorsports Park", "", "USA", [], owned=False, price=9.99),
    Track(153, "Williams Grove Speedway", "", "USA", [], owned=False, price=9.99),
    Track(154, "The Bullring at LVMS", "", "USA", [], owned=False, price=9.99),
    Track(155, "Eldora Speedway", "", "USA", [], owned=False, price=9.99),
    Track(156, "Knoxville Raceway", "", "USA", [], owned=False, price=9.99),
    Track(157, "Kansas Speedway", "", "USA", [], owned=False, price=9.99),
    Track(158, "Dover Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(159, "Lucas Oil Indianapolis Raceway Park", "", "USA", [], owned=False, price=9.99),
    Track(160, "Darlington Raceway", "", "USA", [], owned=False, price=9.99),
    Track(161, "Iowa Speedway", "", "USA", [], owned=False, price=9.99),
    Track(162, "Auto Club Speedway", "", "USA", [], owned=False, price=9.99),
    Track(163, "Kentucky Speedway", "", "USA", [], owned=False, price=9.99),
    Track(164, "New Smyrna Speedway", "", "USA", [], owned=False, price=9.99),
    Track(165, "Richmond Raceway", "", "USA", [], owned=False, price=9.99),
    Track(166, "Martinsville Speedway", "", "USA", [], owned=False, price=9.99),
    Track(167, "EchoPark Speedway/Atlanta", "", "USA", [], owned=False, price=9.99),
    Track(168, "Concord Speedway", "", "USA", [], owned=False, price=9.99),
    Track(169, "Oxford Plains Speedway", "", "USA", [], owned=False, price=9.99),
    Track(170, "Lanier National Speedway", "", "USA", [], owned=False, price=9.99),
    Track(171, "USA International Speedway", "", "USA", [], owned=False, price=9.99),
    Track(172, "Dirt Track at Charlotte", "", "USA", [], owned=False, price=9.99),
    Track(173, "USA International Speedway - Dirt", "", "USA", [], owned=False, price=9.99),
    Track(174, "Phoenix Raceway - 2008", "", "USA", [], owned=False, price=9.99),
    Track(175, "Daytona International Speedway - Rallycross", "", "USA", [], owned=False, price=9.99),
    Track(176, "Centripetal Circuit", "", "USA", [], owned=True, price=0.0),
    Track(177, "Pocono Raceway - 2009", "", "USA", [], owned=False, price=9.99),
    Track(178, "Michigan International Speedway - 2009", "", "USA", [], owned=False, price=9.99),
    Track(179, "Texas Motor Speedway", "", "USA", [], owned=False, price=9.99),
    Track(180, "Fairbury Speedway", "", "USA", [], owned=False, price=9.99),
]

# ── Calendarios 2026 S2 ───────────────────────────────────────────────────────
# Fuente: SeasonSchedule.pdf de iRacing (Road series, licencia C/D)
MOCK_SERIES = [
    {
        "series_id": 601,
        "series_name": "BMW M2 Cup by Nitro Concepts",
        "car_type": "GT4",
        "car_class_ids": [118],
        "license_class": "Rookie",
        "season_tracks": [8, 24, 15, 5, 10, 17, 12, 21, 22, 16, 20],
    },
    {
        "series_id": 602,
        "series_name": "Global Mazda MX-5 Cup by Fanatec",
        "car_type": "MX-5 Cup",
        "car_class_ids": [53],
        "license_class": "Rookie",
        "season_tracks": [8, 24, 15, 5, 10, 17, 12, 21, 22, 16, 20],
    },
    {
        "series_id": 603,
        "series_name": "Advanced Mazda MX-5 Cup by Heusinkveld",
        "car_type": "MX-5 Cup",
        "car_class_ids": [53],
        "license_class": "Class D",
        "season_tracks": [47, 22, 5, 38, 13, 18, 54, 52, 8, 2, 35, 41],
    },
    {
        "series_id": 604,
        "series_name": "Toyota GR86 Cup by SIMAGIC",
        "car_type": "GT4",
        "car_class_ids": [148],
        "license_class": "Rookie 4.0",
        "season_tracks": [5, 47, 31, 16, 1, 18, 22, 44, 57, 12, 9, 48],
    },
    {
        "series_id": 605,
        "series_name": "GT4 Falken Tyre Challenge",
        "car_type": "GT4",
        "car_class_ids": [118, 148],
        "license_class": "Class D",
        "season_tracks": [48, 42, 64, 51, 49, 45, 8, 19, 52, 14, 53, 6],
    },
    {
        "series_id": 606,
        "series_name": "iRacing Porsche Cup Fixed by CONSPIT",
        "car_type": "GT3 Cup",
        "car_class_ids": [131],
        "license_class": "Class D",
        "season_tracks": [42, 33, 38, 65, 50, 58, 45, 51, 3, 35, 48, 47],
    },
    {
        "series_id": 607,
        "series_name": "GT3 Challenge Fixed by Fanatec",
        "car_type": "GT3",
        "car_class_ids": [84],
        "license_class": "Class C",
        "season_tracks": [47, 42, 15, 3, 40, 53, 31, 48, 38, 55, 56, 57],
    },
    {
        "series_id": 608,
        "series_name": "Spec Racer Ford Challenge",
        "car_type": "Spec Racer",
        "car_class_ids": [35],
        "license_class": "Rookie 4.0",
        "season_tracks": [14, 32, 10, 52, 63, 40, 15, 61, 49, 24, 62, 2],
    },
    {
        "series_id": 609,
        "series_name": "Sports Car Challenge by Falken Tyre",
        "car_type": "GT4 + LMP3",
        "car_class_ids": [118, 148, 128],
        "license_class": "Class D",
        "season_tracks": [48, 42, 64, 51, 49, 45, 8, 19, 52, 14, 53, 6],
    },
    {
        "series_id": 610,
        "series_name": "IMSA Michelin Pilot Challenge",
        "car_type": "GT4 + TCR",
        "car_class_ids": [118, 148],
        "license_class": "Class D",
        "season_tracks": [42, 51, 45, 19, 14, 6],
    },
    {
        "series_id": 701,
        "series_name": "FIA F4 Challenge Fixed",
        "car_type": "Formula",
        "car_class_ids": [101],
        "license_class": "Rookie 4.0",
        "season_tracks": [17, 38, 67, 14, 55, 4, 47, 21, 62, 68, 10, 36],
    },
    {
        "series_id": 702,
        "series_name": "Skip Barber Race Series",
        "car_type": "Formula",
        "car_class_ids": [63],
        "license_class": "Rookie 4.0",
        "season_tracks": [10, 51, 12, 2, 17, 13, 15, 59, 24, 68, 5, 58],
    },
    {
        "series_id": 703,
        "series_name": "Dallara Formula iR",
        "car_type": "Formula",
        "car_class_ids": [130],
        "license_class": "Class D",
        "season_tracks": [17, 48, 47, 6, 61, 13, 2, 24, 38],
    },
    {
        "series_id": 800,
        "series_name": "NASCAR Cup Series",
        "car_type": "NASCAR Cup",
        "car_class_ids": [300],
        "license_class": "Class A",
        "season_tracks": [24, 43, 61, 114, 121, 150, 160, 165, 166, 179, 158, 157],
    },
    {
        "series_id": 801,
        "series_name": "NASCAR Xfinity Series",
        "car_type": "NASCAR Xfinity",
        "car_class_ids": [301],
        "license_class": "Class B",
        "season_tracks": [113, 119, 124, 127, 134, 140, 144, 168, 169, 132, 120, 167],
    },
    {
        "series_id": 802,
        "series_name": "NASCAR Craftsman Truck Series",
        "car_type": "NASCAR Trucks",
        "car_class_ids": [302],
        "license_class": "Class C",
        "season_tracks": [86, 108, 122, 123, 125, 143, 147, 151, 154, 161, 163, 164],
    },
    {
        "series_id": 803,
        "series_name": "ARCA Menards Series",
        "car_type": "ARCA",
        "car_class_ids": [305],
        "license_class": "Class D",
        "season_tracks": [113, 119, 124, 127, 134, 140, 144, 168, 169, 132],
    },
    {
        "series_id": 804,
        "series_name": "INDYCAR Series Fixed",
        "car_type": "IndyCar",
        "car_class_ids": [303],
        "license_class": "Class A",
        "season_tracks": [61, 121, 86, 47, 50, 64, 13, 19, 52],
    },
    {
        "series_id": 805,
        "series_name": "NASCAR Cup Legacy Series",
        "car_type": "NASCAR Cup Legacy",
        "car_class_ids": [326],
        "license_class": "Class C",
        "season_tracks": [144, 108, 169, 134, 140, 132],
    },
    {
        "series_id": 806,
        "series_name": "SRX Series",
        "car_type": "SRX",
        "car_class_ids": [330],
        "license_class": "Class C",
        "season_tracks": [124, 134, 140, 168, 119, 127],
    },
    {
        "series_id": 900,
        "series_name": "World of Outlaws Late Models",
        "car_type": "Dirt Late Model",
        "car_class_ids": [313],
        "license_class": "Class C",
        "season_tracks": [104, 115, 130, 133, 138, 139, 146, 153, 155, 180],
    },
    {
        "series_id": 901,
        "series_name": "World of Outlaws Sprint Cars",
        "car_type": "Sprint Car",
        "car_class_ids": [311],
        "license_class": "Class C",
        "season_tracks": [111, 116, 130, 136, 148, 149, 156, 170, 172, 173],
    },
    {
        "series_id": 902,
        "series_name": "USAC Dirt Midgets Series",
        "car_type": "Dirt Midget",
        "car_class_ids": [314],
        "license_class": "Class D",
        "season_tracks": [104, 111, 116, 118, 133, 146, 149, 156, 170],
    },
    {
        "series_id": 903,
        "series_name": "Dirt Modified Series",
        "car_type": "Dirt Modified",
        "car_class_ids": [312],
        "license_class": "Class D",
        "season_tracks": [104, 115, 118, 130, 133, 146, 153, 172],
    },
    {
        "series_id": 904,
        "series_name": "NASCAR Trucks Dirt Series",
        "car_type": "NASCAR Trucks Dirt",
        "car_class_ids": [327],
        "license_class": "Class C",
        "season_tracks": [104, 115, 136, 138, 139, 155],
    },
    {
        "series_id": 905,
        "series_name": "Micro Sprint Series",
        "car_type": "Micro Sprint",
        "car_class_ids": [324],
        "license_class": "Rookie",
        "season_tracks": [111, 116, 133, 146, 170],
    },
    {
        "series_id": 906,
        "series_name": "Dirt Street Stock Series",
        "car_type": "Street Stock",
        "car_class_ids": [332],
        "license_class": "Rookie",
        "season_tracks": [104, 115, 130, 138, 146, 180],
    },
    {
        "series_id": 1000,
        "series_name": "Rallycross Series",
        "car_type": "Rallycross",
        "car_class_ids": [315],
        "license_class": "Class C",
        "season_tracks": [141, 175, 176],
    },
    {
        "series_id": 1001,
        "series_name": "Lucas Oil Off Road Series",
        "car_type": "Off-Road Truck",
        "car_class_ids": [328],
        "license_class": "Class C",
        "season_tracks": [102, 103, 106, 109, 110],
    },
    {
        "series_id": 750,
        "series_name": "F1 Sprint Series",
        "car_type": "Formula 1",
        "car_class_ids": [320],
        "license_class": "Class A",
        "season_tracks": [30, 33, 36, 52, 58, 32, 3, 41, 65, 38, 74, 39],
    },
    {
        "series_id": 751,
        "series_name": "FIA Formula 4 Championship",
        "car_type": "Formula 4",
        "car_class_ids": [321],
        "license_class": "Rookie 4.0",
        "season_tracks": [17, 14, 56, 76, 31, 51],
    },
    {
        "series_id": 752,
        "series_name": "Formula Renault Challenge",
        "car_type": "Formula Renault",
        "car_class_ids": [322],
        "license_class": "Class D",
        "season_tracks": [21, 22, 32, 55, 4, 62],
    },
    {
        "series_id": 753,
        "series_name": "Formula Vee Sprint Series",
        "car_type": "Formula Vee",
        "car_class_ids": [323],
        "license_class": "Rookie",
        "season_tracks": [15, 5, 49, 54, 64],
    },
    {
        "series_id": 754,
        "series_name": "Super Formula Championship",
        "car_type": "Super Formula",
        "car_class_ids": [333],
        "license_class": "Class A",
        "season_tracks": [60, 89, 38, 16, 53, 10],
    },
    {
        "series_id": 654,
        "series_name": "Stock Car Brasil Series",
        "car_type": "Stock Car Brasil",
        "car_class_ids": [331],
        "license_class": "Class C",
        "season_tracks": [1, 73, 85, 39, 65],
    },
    {
        "series_id": 655,
        "series_name": "Supercars Championship",
        "car_type": "Supercars",
        "car_class_ids": [334],
        "license_class": "Class B",
        "season_tracks": [9, 48, 11, 20, 59, 90, 129, 101],
    },
    {
        "series_id": 611,
        "series_name": "GTE Endurance Series",
        "car_type": "GTE",
        "car_class_ids": [162],
        "license_class": "Class B",
        "season_tracks": [41, 42, 17, 13, 19, 6, 33],
    },
    {
        "series_id": 612,
        "series_name": "LMP2 Prototype Challenge",
        "car_type": "LMP2",
        "car_class_ids": [127],
        "license_class": "Class A",
        "season_tracks": [41, 42, 17, 13, 19, 6],
    },
    {
        "series_id": 613,
        "series_name": "GTP Hypercar Series",
        "car_type": "GTP",
        "car_class_ids": [160],
        "license_class": "Class A",
        "season_tracks": [41, 42, 19, 33, 17, 6, 13, 52],
    },
    {
        "series_id": 614,
        "series_name": "TCR Touring Car Series",
        "car_type": "TCR",
        "car_class_ids": [155],
        "license_class": "Class C",
        "season_tracks": [12, 30, 31, 32, 35, 51, 56, 76],
    },
    {
        "series_id": 615,
        "series_name": "Touring Car Challenge",
        "car_type": "Touring Car",
        "car_class_ids": [70],
        "license_class": "Class C",
        "season_tracks": [12, 30, 31, 51, 56, 76],
    },
    {
        "series_id": 616,
        "series_name": "Production Car Challenge",
        "car_type": "Sports Car",
        "car_class_ids": [45],
        "license_class": "Class C",
        "season_tracks": [42, 19, 13, 64, 6],
    },
    {
        "series_id": 617,
        "series_name": "Road to Indy Series",
        "car_type": "Road to Indy",
        "car_class_ids": [329, 304],
        "license_class": "Class D",
        "season_tracks": [47, 50, 49, 64, 13, 19],
    },
    {
        "series_id": 704,
        "series_name": "Classic Lotus Formula Series",
        "car_type": "Classic F1",
        "car_class_ids": [90, 91],
        "license_class": "Class C",
        "season_tracks": [74, 51, 12, 56, 31],
    },
    {
        "series_id": 807,
        "series_name": "NASCAR Whelen Modified Tour",
        "car_type": "Modified",
        "car_class_ids": [310],
        "license_class": "Class C",
        "season_tracks": [108, 119, 124, 127, 134, 169],
    },
    {
        "series_id": 808,
        "series_name": "Legends Car Series",
        "car_type": "Legends",
        "car_class_ids": [308],
        "license_class": "Rookie",
        "season_tracks": [113, 119, 124, 127, 134, 169],
    },
]

# ── Carreras de ejemplo ───────────────────────────────────────────────────────
_base = datetime.utcnow()

MOCK_RACES: list[Race] = [
    Race(70001, 608, "Spec Racer Ford Challenge",    "2026 S2", 24,  "SCCA Spec Racer Ford",
         "Snetterton Circuit", "300",
         (_base - timedelta(days=5)).isoformat(),
         3, 3, 18, _rand_lap(110000), _rand_lap(112000), 2, 18, 2,
         1200, 1215, 3.50, 3.55, "road"),
    Race(70002, 602, "Global MX-5 Cup",             "2026 S2", 33,  "Global Mazda MX-5 Cup",
         "Motorsport Arena Oschersleben", "Grand Prix",
         (_base - timedelta(days=12)).isoformat(),
         7, 7, 20, _rand_lap(90000),  _rand_lap(92000),  0, 22, 4,
         1215, 1198, 3.55, 3.42, "road"),
    Race(70003, 601, "BMW M2 Cup",                  "2026 S2", 156, "BMW M2 CS Racing",
         "Winton Motor Raceway", "National Circuit",
         (_base - timedelta(days=19)).isoformat(),
         5, 5, 18, _rand_lap(98000),  _rand_lap(100000), 1, 15, 1,
         1198, 1210, 3.42, 3.48, "road"),
    Race(70004, 702, "Skip Barber Race Series",     "2026 S2", 77,  "Skip Barber Formula 2000",
         "Okayama International Circuit", "Full Course",
         (_base - timedelta(days=26)).isoformat(),
         2, 2, 22, _rand_lap(95000),  _rand_lap(97000),  3, 30, 0,
         1210, 1185, 3.48, 3.30, "road"),
    Race(70005, 608, "Spec Racer Ford Challenge",   "2026 S2", 24,  "SCCA Spec Racer Ford",
         "Summit Point Raceway", "Summit Point",
         (_base - timedelta(days=33)).isoformat(),
         1, 1, 20, _rand_lap(105000), _rand_lap(107000), 4, 20, 0,
         1185, 1155, 3.30, 3.12, "road"),
    Race(70006, 602, "Global MX-5 Cup",             "2026 S2", 33,  "Global Mazda MX-5 Cup",
         "Virginia International Raceway", "Full Course",
         (_base - timedelta(days=40)).isoformat(),
         9, 9, 24, _rand_lap(88000),  _rand_lap(90000),  0, 14, 6,
         1155, 1175, 3.12, 3.25, "road"),
]

MOCK_SERIES_COUNT: dict[str, int] = {}
for _c in MOCK_CARS:
    MOCK_SERIES_COUNT[f"car_{_c.car_id}"] = random.randint(2, 12)
for _t in MOCK_TRACKS:
    MOCK_SERIES_COUNT[f"track_{_t.track_id}"] = random.randint(1, 8)

MOCK_IRATING_HISTORY = [
    {"timestamp": "2025-10-01T00:00:00Z", "irating": 900},
    {"timestamp": "2025-11-01T00:00:00Z", "irating": 950},
    {"timestamp": "2025-12-01T00:00:00Z", "irating": 980},
    {"timestamp": "2026-01-01T00:00:00Z", "irating": 1050},
    {"timestamp": "2026-02-01T00:00:00Z", "irating": 1100},
    {"timestamp": "2026-03-01T00:00:00Z", "irating": 1130},
    {"timestamp": "2026-04-01T00:00:00Z", "irating": 1155},
    {"timestamp": "2026-05-01T00:00:00Z", "irating": 1185},
    {"timestamp": "2026-05-15T00:00:00Z", "irating": 1198},
    {"timestamp": "2026-06-01T00:00:00Z", "irating": 1210},
    {"timestamp": "2026-06-05T00:00:00Z", "irating": 1200},
]
