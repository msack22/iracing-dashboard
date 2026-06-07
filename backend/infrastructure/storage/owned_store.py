"""
Manual ownership overrides stored in SQLite.
Lets the user mark cars/tracks as owned or not owned,
independent of the iRacing API (useful when API is unavailable).
"""
import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "credentials.db"


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(_DB_PATH)
    con.execute(
        """CREATE TABLE IF NOT EXISTS owned_items (
               item_type TEXT NOT NULL,  -- 'car' | 'track'
               item_id   INTEGER NOT NULL,
               owned     INTEGER NOT NULL DEFAULT 1,
               PRIMARY KEY (item_type, item_id)
           )"""
    )
    con.commit()
    return con


def get_owned_cars() -> set[int]:
    with _conn() as con:
        rows = con.execute(
            "SELECT item_id FROM owned_items WHERE item_type='car' AND owned=1"
        ).fetchall()
    return {r[0] for r in rows}


def get_owned_tracks() -> set[int]:
    with _conn() as con:
        rows = con.execute(
            "SELECT item_id FROM owned_items WHERE item_type='track' AND owned=1"
        ).fetchall()
    return {r[0] for r in rows}


def get_all_overrides() -> dict:
    with _conn() as con:
        rows = con.execute(
            "SELECT item_type, item_id, owned FROM owned_items"
        ).fetchall()
    cars = [r[1] for r in rows if r[0] == "car" and r[2] == 1]
    tracks = [r[1] for r in rows if r[0] == "track" and r[2] == 1]
    return {"cars": cars, "tracks": tracks}


def set_owned(item_type: str, item_id: int, owned: bool) -> None:
    with _conn() as con:
        con.execute(
            """INSERT INTO owned_items (item_type, item_id, owned)
               VALUES (?, ?, ?)
               ON CONFLICT(item_type, item_id) DO UPDATE SET owned=excluded.owned""",
            (item_type, item_id, 1 if owned else 0),
        )


def remove_override(item_type: str, item_id: int) -> None:
    with _conn() as con:
        con.execute(
            "DELETE FROM owned_items WHERE item_type=? AND item_id=?",
            (item_type, item_id),
        )
