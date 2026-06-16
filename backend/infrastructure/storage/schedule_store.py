"""
Persists series schedules (which tracks are on each series calendar for the season).
Allows the user to manage schedules manually when the iRacing API is unavailable.
Seeds from MOCK_SERIES on first run.
"""
import json
import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "credentials.db"


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(_DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS series_schedule (
            series_id     INTEGER PRIMARY KEY,
            series_name   TEXT NOT NULL,
            car_type      TEXT,
            car_class_ids TEXT DEFAULT '[]',
            license_class TEXT DEFAULT ''
        )
    """)
    try:
        con.execute("ALTER TABLE series_schedule ADD COLUMN license_class TEXT DEFAULT ''")
        con.commit()
    except Exception:
        pass
    con.execute("""
        CREATE TABLE IF NOT EXISTS series_schedule_tracks (
            series_id  INTEGER NOT NULL,
            track_id   INTEGER NOT NULL,
            round_num  INTEGER DEFAULT 0,
            PRIMARY KEY (series_id, track_id),
            FOREIGN KEY (series_id) REFERENCES series_schedule(series_id)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            item_type TEXT NOT NULL,
            item_id   INTEGER NOT NULL,
            PRIMARY KEY (item_type, item_id)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog_cars (
            car_id        INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            categories    TEXT DEFAULT '[]',
            car_class_id  INTEGER DEFAULT 0,
            car_class_name TEXT DEFAULT '',
            price         REAL DEFAULT 0.0,
            owned         INTEGER DEFAULT 0
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS catalog_tracks (
            track_id  INTEGER PRIMARY KEY,
            name      TEXT NOT NULL,
            city      TEXT DEFAULT '',
            country   TEXT DEFAULT '',
            price     REAL DEFAULT 0.0,
            owned     INTEGER DEFAULT 0,
            configs   TEXT DEFAULT '[]'
        )
    """)
    con.commit()
    return con


def seed_catalog() -> None:
    """Upsert full car/track catalog from mock data on startup."""
    from infrastructure.iracing.mock.mock_data import MOCK_CARS, MOCK_TRACKS
    from dataclasses import asdict
    with _conn() as con:
        for c in MOCK_CARS:
            con.execute(
                """INSERT INTO catalog_cars (car_id, name, categories, car_class_id, car_class_name, price, owned)
                   VALUES (?,?,?,?,?,?,?)
                   ON CONFLICT(car_id) DO UPDATE SET
                       name=excluded.name,
                       categories=excluded.categories,
                       car_class_id=excluded.car_class_id,
                       car_class_name=excluded.car_class_name,
                       price=excluded.price,
                       owned=excluded.owned""",
                (c.car_id, c.name, json.dumps(c.categories), c.car_class_id,
                 c.car_class_name, c.price, int(c.owned))
            )
        for t in MOCK_TRACKS:
            configs = [
                {"track_id": cfg.track_id, "config_name": cfg.config_name,
                 "owned": cfg.owned, "price": cfg.price}
                for cfg in t.configs
            ]
            con.execute(
                """INSERT INTO catalog_tracks (track_id, name, city, country, price, owned, configs)
                   VALUES (?,?,?,?,?,?,?)
                   ON CONFLICT(track_id) DO UPDATE SET
                       name=excluded.name,
                       city=excluded.city,
                       country=excluded.country,
                       price=excluded.price,
                       configs=excluded.configs""",
                (t.track_id, t.name, t.city, t.country, t.price, int(t.owned),
                 json.dumps(configs))
            )


def _seed_if_empty() -> None:
    from infrastructure.iracing.mock.mock_data import MOCK_SERIES
    with _conn() as con:
        count = con.execute("SELECT COUNT(*) FROM series_schedule").fetchone()[0]
        if count > 0:
            return
        for s in MOCK_SERIES:
            con.execute(
                "INSERT OR IGNORE INTO series_schedule (series_id, series_name, car_type, car_class_ids, license_class) VALUES (?,?,?,?,?)",
                (s["series_id"], s["series_name"], s["car_type"], json.dumps(s["car_class_ids"]), s.get("license_class", ""))
            )
            for i, tid in enumerate(s["season_tracks"]):
                con.execute(
                    "INSERT OR IGNORE INTO series_schedule_tracks (series_id, track_id, round_num) VALUES (?,?,?)",
                    (s["series_id"], tid, i + 1)
                )


# ── Series ────────────────────────────────────────────────────────────────────

def get_all_series() -> list[dict]:
    _seed_if_empty()
    with _conn() as con:
        rows = con.execute(
            "SELECT series_id, series_name, car_type, car_class_ids, license_class FROM series_schedule ORDER BY series_id"
        ).fetchall()
        track_rows = con.execute(
            "SELECT series_id, track_id, round_num FROM series_schedule_tracks ORDER BY series_id, round_num"
        ).fetchall()

    tracks_by_series: dict[int, list[dict]] = {}
    for sid, tid, rn in track_rows:
        tracks_by_series.setdefault(sid, []).append({"track_id": tid, "round_num": rn})

    return [
        {
            "series_id": r[0],
            "series_name": r[1],
            "car_type": r[2],
            "car_class_ids": json.loads(r[3]),
            "license_class": r[4] if len(r) > 4 else "",
            "tracks": tracks_by_series.get(r[0], []),
        }
        for r in rows
    ]


def upsert_series(series_id: int, series_name: str, car_type: str, car_class_ids: list[int]) -> None:
    with _conn() as con:
        con.execute(
            """INSERT INTO series_schedule (series_id, series_name, car_type, car_class_ids)
               VALUES (?,?,?,?)
               ON CONFLICT(series_id) DO UPDATE SET
                   series_name=excluded.series_name,
                   car_type=excluded.car_type,
                   car_class_ids=excluded.car_class_ids""",
            (series_id, series_name, car_type, json.dumps(car_class_ids))
        )


def set_series_tracks(series_id: int, track_ids: list[int]) -> None:
    with _conn() as con:
        con.execute("DELETE FROM series_schedule_tracks WHERE series_id=?", (series_id,))
        for i, tid in enumerate(track_ids):
            con.execute(
                "INSERT INTO series_schedule_tracks (series_id, track_id, round_num) VALUES (?,?,?)",
                (series_id, tid, i + 1)
            )


def delete_series(series_id: int) -> None:
    with _conn() as con:
        con.execute("DELETE FROM series_schedule_tracks WHERE series_id=?", (series_id,))
        con.execute("DELETE FROM series_schedule WHERE series_id=?", (series_id,))


# ── Wishlist ──────────────────────────────────────────────────────────────────

def get_wishlist() -> dict:
    with _conn() as con:
        rows = con.execute("SELECT item_type, item_id FROM wishlist").fetchall()
    return {
        "cars": [r[1] for r in rows if r[0] == "car"],
        "tracks": [r[1] for r in rows if r[0] == "track"],
    }


def wishlist_add(item_type: str, item_id: int) -> None:
    with _conn() as con:
        con.execute(
            "INSERT OR IGNORE INTO wishlist (item_type, item_id) VALUES (?,?)",
            (item_type, item_id)
        )


def wishlist_remove(item_type: str, item_id: int) -> None:
    with _conn() as con:
        con.execute(
            "DELETE FROM wishlist WHERE item_type=? AND item_id=?",
            (item_type, item_id)
        )


def wishlist_clear() -> None:
    with _conn() as con:
        con.execute("DELETE FROM wishlist")


# ── App settings ──────────────────────────────────────────────────────────────

def get_setting(key: str, default: str | None = None) -> str | None:
    with _conn() as con:
        row = con.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def set_setting(key: str, value: str) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO app_settings (key, value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value)
        )


def get_current_week() -> int:
    return int(get_setting("current_week", "1"))


def set_current_week(week: int) -> None:
    set_setting("current_week", str(max(1, week)))
