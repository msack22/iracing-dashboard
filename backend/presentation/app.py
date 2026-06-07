from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import asdict
from domain.repositories.i_cars_repository import ICarsRepository
from domain.repositories.i_tracks_repository import ITracksRepository
from domain.repositories.i_member_repository import IMemberRepository
from domain.repositories.i_races_repository import IRacesRepository
from application.use_cases.recommendations.get_purchase_recommendations import GetPurchaseRecommendationsUseCase
from infrastructure.auth.credentials_store import (
    save_credentials, credentials_exist, delete_credentials
)
from infrastructure.storage.owned_store import (
    get_all_overrides, set_owned, remove_override
)
from infrastructure.storage.schedule_store import (
    get_all_series as schedule_get_all_series,
    upsert_series, set_series_tracks, delete_series,
    get_wishlist, wishlist_add, wishlist_remove, wishlist_clear,
)
from pydantic import BaseModel


class CredentialsPayload(BaseModel):
    username: str
    password: str


class OwnedPayload(BaseModel):
    owned: bool


class SeriesUpsertPayload(BaseModel):
    series_name: str
    car_type: str
    car_class_ids: list[int]
    track_ids: list[int]


def _apply_ownership(items: list, owned_ids: set[int], id_field: str) -> list:
    """Merge API/mock ownership with manual overrides."""
    for item in items:
        if item[id_field] in owned_ids:
            item["owned"] = True
    return items


def create_app(
    cars_repo: ICarsRepository,
    tracks_repo: ITracksRepository,
    member_repo: IMemberRepository,
    races_repo: IRacesRepository,
) -> FastAPI:
    app = FastAPI(title="iRacing Dashboard API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Auth ─────────────────────────────────────────────────────────────────
    @app.get("/api/auth/status")
    def auth_status():
        return {"configured": credentials_exist()}

    @app.post("/api/auth/credentials")
    def set_credentials(payload: CredentialsPayload):
        save_credentials(payload.username, payload.password)
        return {"ok": True}

    @app.delete("/api/auth/credentials")
    def clear_credentials():
        delete_credentials()
        return {"ok": True}

    # ── Health ────────────────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # ── Member ────────────────────────────────────────────────────────────────
    @app.get("/api/member/profile")
    async def member_profile():
        profile = await member_repo.get_member_profile()
        return {"data": asdict(profile)}

    @app.get("/api/member/irating-history")
    async def irating_history(category: str = "road"):
        history = await member_repo.get_irating_history(category=category)
        return {"data": history}

    # ── Cars ──────────────────────────────────────────────────────────────────
    @app.get("/api/cars")
    async def get_cars(owned_only: bool = False):
        cars = await (cars_repo.get_owned_cars() if owned_only else cars_repo.get_all_cars())
        manual = get_all_overrides()
        owned_set = set(manual["cars"])
        result = []
        for c in cars:
            d = asdict(c)
            if d["car_id"] in owned_set:
                d["owned"] = True
            if owned_only and not d["owned"]:
                continue
            result.append(d)
        return {"data": result}

    @app.get("/api/cars/category/{category}")
    async def cars_by_category(category: str):
        if category not in ("road", "oval", "dirt_road", "dirt_oval"):
            return {"error": "Invalid category"}, 400
        cars = await cars_repo.get_cars_by_category(category)  # type: ignore[arg-type]
        return {"data": [asdict(c) for c in cars]}

    # ── Tracks ────────────────────────────────────────────────────────────────
    @app.get("/api/tracks")
    async def get_tracks(owned_only: bool = False):
        tracks = await (tracks_repo.get_owned_tracks() if owned_only else tracks_repo.get_all_tracks())
        manual = get_all_overrides()
        owned_set = set(manual["tracks"])
        result = []
        for t in tracks:
            d = asdict(t)
            if d["track_id"] in owned_set:
                d["owned"] = True
                for cfg in d.get("configs", []):
                    cfg["owned"] = True
            if owned_only and not d["owned"]:
                continue
            result.append(d)
        return {"data": result}

    # ── Races ─────────────────────────────────────────────────────────────────
    @app.get("/api/races/recent")
    async def recent_races(count: int = 20):
        races = await races_repo.get_recent_races(count=count)
        return {"data": [asdict(r) for r in races]}

    @app.get("/api/races/by-series")
    async def races_by_series(count: int = 50):
        races = await races_repo.get_recent_races(count=count)
        grouped: dict[str, dict] = {}
        for r in races:
            d = asdict(r)
            key = str(d["series_id"])
            if key not in grouped:
                grouped[key] = {
                    "series_id": d["series_id"],
                    "series_name": d["series_name"],
                    "races": [],
                    "best_position": None,
                    "total_races": 0,
                    "total_incidents": 0,
                }
            g = grouped[key]
            g["races"].append(d)
            g["total_races"] += 1
            g["total_incidents"] += d.get("incidents", 0)
            pos = d.get("finish_position", 99)
            if g["best_position"] is None or pos < g["best_position"]:
                g["best_position"] = pos
        return {"data": list(grouped.values())}

    # ── Manual Ownership ─────────────────────────────────────────────────────
    @app.get("/api/owned")
    def owned_items():
        return {"data": get_all_overrides()}

    @app.put("/api/owned/car/{car_id}")
    def set_car_owned(car_id: int, payload: OwnedPayload):
        if payload.owned:
            set_owned("car", car_id, True)
        else:
            remove_override("car", car_id)
        return {"ok": True}

    @app.put("/api/owned/track/{track_id}")
    def set_track_owned(track_id: int, payload: OwnedPayload):
        if payload.owned:
            set_owned("track", track_id, True)
        else:
            remove_override("track", track_id)
        return {"ok": True}

    # ── Series calendar ───────────────────────────────────────────────────────
    def _build_series_detail(series_list, all_cars, all_tracks, manual):
        owned_cars_manual = set(manual["cars"])
        owned_tracks_manual = set(manual["tracks"])
        track_map = {t.track_id: t for t in all_tracks}
        result = []
        for s in series_list:
            series_cars = []
            for c in all_cars:
                if c.car_class_id not in s["car_class_ids"]:
                    continue
                owned = c.owned or c.car_id in owned_cars_manual
                series_cars.append({
                    "car_id": c.car_id,
                    "name": c.name,
                    "car_type": c.car_class_name,
                    "owned": owned,
                    "price": c.price,
                })

            track_ids = s.get("season_tracks") or [t["track_id"] for t in s.get("tracks", [])]
            season_tracks = []
            for tid in track_ids:
                t = track_map.get(tid)
                if not t:
                    continue
                owned = t.owned or t.track_id in owned_tracks_manual
                season_tracks.append({
                    "track_id": t.track_id,
                    "name": t.name,
                    "country": t.country,
                    "owned": owned,
                    "price": t.price,
                })

            owned_cars_count = sum(1 for c in series_cars if c["owned"])
            owned_tracks_count = sum(1 for t in season_tracks if t["owned"])
            can_race = owned_cars_count > 0 and owned_tracks_count > 0

            result.append({
                "series_id": s["series_id"],
                "series_name": s["series_name"],
                "car_type": s["car_type"],
                "license_class": s.get("license_class", ""),
                "cars": series_cars,
                "season_tracks": season_tracks,
                "can_race": can_race,
                "owned_cars_count": owned_cars_count,
                "owned_tracks_count": owned_tracks_count,
                "total_tracks": len(season_tracks),
                "missing_cars": [c for c in series_cars if not c["owned"]],
                "missing_tracks": [t for t in season_tracks if not t["owned"]],
            })
        return result

    @app.get("/api/series")
    async def get_series():
        series_list = schedule_get_all_series()
        # enrich with car_class_ids and season_tracks from db
        all_cars = await cars_repo.get_all_cars()
        all_tracks = await tracks_repo.get_all_tracks()
        manual = get_all_overrides()
        return {"data": _build_series_detail(series_list, all_cars, all_tracks, manual)}

    @app.post("/api/series/seed")
    async def seed_series():
        """Force re-seed de schedules desde MOCK_SERIES (borra y recrea)."""
        from infrastructure.iracing.mock.mock_data import MOCK_SERIES
        import sqlite3
        from pathlib import Path
        from infrastructure.storage.schedule_store import _conn
        with _conn() as con:
            con.execute("DELETE FROM series_schedule_tracks")
            con.execute("DELETE FROM series_schedule")
            import json
            for s in MOCK_SERIES:
                con.execute(
                    "INSERT INTO series_schedule (series_id, series_name, car_type, car_class_ids, license_class) VALUES (?,?,?,?,?)",
                    (s["series_id"], s["series_name"], s["car_type"], json.dumps(s["car_class_ids"]), s.get("license_class", ""))
                )
                for i, tid in enumerate(s.get("season_tracks", [])):
                    con.execute(
                        "INSERT INTO series_schedule_tracks (series_id, track_id, round_num) VALUES (?,?,?)",
                        (s["series_id"], tid, i + 1)
                    )
        return {"ok": True, "seeded": len(MOCK_SERIES)}

    @app.post("/api/series/import-pdf")
    async def import_pdf(file: UploadFile = File(...)):
        """
        Acepta un PDF con el calendario de temporada de iRacing,
        extrae el texto con pdftotext y parsea series + tracks.
        Devuelve ParsedSeries[] para que el usuario revise y confirme.
        """
        import tempfile, subprocess, re, json as _json
        from collections import Counter
        from infrastructure.iracing.mock.mock_data import MOCK_TRACKS, MOCK_CARS
        from infrastructure.storage.owned_store import get_all_overrides

        if not file.filename or not file.filename.endswith(".pdf"):
            return {"error": "Solo se aceptan archivos PDF"}, 400

        content = await file.read()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                ["pdftotext", tmp_path, "-"],
                capture_output=True, text=True, timeout=30
            )
            text = result.stdout
        finally:
            import os
            os.unlink(tmp_path)

        if not text.strip():
            return {"error": "No se pudo extraer texto del PDF. ¿Está instalado poppler (pdftotext)?"}

        # Build track lookup: name keywords → track
        manual = get_all_overrides()
        owned_tracks_manual = set(manual["tracks"])

        def name_tokens(name: str) -> list[str]:
            return [w.lower() for w in re.split(r'[\s\-_/,]+', name) if len(w) > 2]

        track_lookup = []
        for t in MOCK_TRACKS:
            tokens = name_tokens(t.name)
            track_lookup.append((t, tokens))

        def match_track(raw: str):
            raw_lower = raw.lower()
            raw_tokens = name_tokens(raw)
            best_score = 0
            best_track = None
            for t, tokens in track_lookup:
                score = sum(1 for tok in tokens if tok in raw_lower)
                if score > best_score:
                    best_score = score
                    best_track = t
            if best_score == 0:
                return None
            return best_track

        # Build car lookup: name keywords → car (used to derive car_type/class for the series)
        car_lookup = []
        for c in MOCK_CARS:
            tokens = name_tokens(c.name)
            car_lookup.append((c, tokens))

        def match_car(raw: str):
            raw_lower = raw.lower()
            best_score = 0
            best_car = None
            for c, tokens in car_lookup:
                score = sum(1 for tok in tokens if tok in raw_lower)
                if score > best_score:
                    best_score = score
                    best_car = c
            if best_score == 0:
                return None
            return best_car

        def derive_car_type(raw_names: list[str]) -> str:
            """Determina la clase de auto representativa de una serie a partir de los nombres crudos parseados del PDF."""
            labels = []
            for raw in raw_names:
                matched = match_car(raw)
                if matched:
                    labels.append(matched.car_class_name or matched.name)
            if not labels:
                return raw_names[0] if raw_names else ""
            return Counter(labels).most_common(1)[0][0]

        # Parse text into series blocks
        # Series header pattern: "Series Name - YYYY Season N"
        # Track lines: lines NOT starting with "(2026-" that come before date lines
        lines = text.splitlines()
        parsed_series = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Detect series header: "Something - 2026 Season N" or "Something 2026 Season N"
            header_match = re.search(r'(.+?)\s*[-–]\s*20\d\d\s+Season\s+\d+', line, re.IGNORECASE)
            if not header_match:
                # Also check for plain "2026 Season N" without dash
                header_match = re.search(r'(.+?)\s+20\d\d\s+Season\s+\d+', line, re.IGNORECASE)
            if header_match:
                series_name = header_match.group(1).strip()
                season_str = line[header_match.start():]
                season_m = re.search(r'(20\d\d\s+Season\s+\d+)', season_str, re.IGNORECASE)
                season = season_m.group(1) if season_m else "2026 Season 2"

                # Gather track+date pairs until next header
                tracks_parsed = []
                cars_found = []
                license_class = ""
                i += 1
                while i < len(lines):
                    l = lines[i].strip()
                    # Stop at next series header
                    if re.search(r'(.+?)\s*[-–]\s*20\d\d\s+Season\s+\d+', l, re.IGNORECASE) or \
                       re.search(r'(.+?)\s+20\d\d\s+Season\s+\d+', l, re.IGNORECASE):
                        break
                    # License line
                    lic_m = re.search(r'Class\s+([A-F])\b', l, re.IGNORECASE)
                    if lic_m:
                        license_class = lic_m.group(1).upper()
                    # Car line (lines with "car:" or "Fixed" markers)
                    if re.match(r'Car\s*:', l, re.IGNORECASE):
                        cars_found.append(re.sub(r'^Car\s*:\s*', '', l, flags=re.IGNORECASE).strip())
                    # Track entry: non-empty line that isn't a date line and has reasonable length
                    # A track line is followed by a date line "(2026-..."
                    if l and not l.startswith('(') and not l.startswith('Week') and \
                       len(l) > 4 and not re.match(r'^[\d\s/]+$', l):
                        # Peek ahead for date line
                        if i + 1 < len(lines):
                            next_l = lines[i + 1].strip()
                            if next_l.startswith('(2026-') or re.match(r'\(20\d\d-\d\d-\d\d', next_l):
                                matched_track = match_track(l)
                                owned = False
                                if matched_track:
                                    owned = matched_track.owned or matched_track.track_id in owned_tracks_manual
                                tracks_parsed.append({
                                    "raw": l,
                                    "track_id": matched_track.track_id if matched_track else None,
                                    "name": matched_track.name if matched_track else None,
                                    "owned": owned,
                                })
                    i += 1

                if tracks_parsed:
                    matched_count = sum(1 for t in tracks_parsed if t["track_id"] is not None)
                    parsed_series.append({
                        "series_name": series_name,
                        "season": season,
                        "car_names": cars_found,
                        "car_type": derive_car_type(cars_found),
                        "license_class": license_class,
                        "tracks": tracks_parsed,
                        "matched_count": matched_count,
                        "total_tracks": len(tracks_parsed),
                    })
                continue
            i += 1

        return {"data": parsed_series}

    class ImportConfirmPayload(BaseModel):
        series: list[dict]

    @app.post("/api/series/import-confirm")
    async def import_confirm(payload: ImportConfirmPayload):
        """
        Recibe las series seleccionadas (ya parseadas y revisadas por el usuario)
        e importa / sobreescribe en schedule_store.
        """
        import json as _json
        from infrastructure.storage.schedule_store import _conn

        imported = 0
        with _conn() as con:
            for idx, s in enumerate(payload.series):
                series_id = 9000 + idx  # IDs temporales empezando en 9000
                # Intentar detectar ID existente por nombre
                row = con.execute(
                    "SELECT series_id FROM series_schedule WHERE series_name=?",
                    (s["series_name"],)
                ).fetchone()
                if row:
                    series_id = row[0]
                else:
                    # Asignar nuevo ID
                    max_row = con.execute("SELECT MAX(series_id) FROM series_schedule").fetchone()
                    existing_max = max_row[0] if max_row and max_row[0] else 8999
                    series_id = max(9000, existing_max + 1)

                track_ids = [t["track_id"] for t in s.get("tracks", []) if t.get("track_id")]
                car_class_ids = s.get("car_class_ids", [])

                con.execute(
                    "INSERT OR REPLACE INTO series_schedule (series_id, series_name, car_type, car_class_ids, license_class) VALUES (?,?,?,?,?)",
                    (series_id, s["series_name"], s.get("car_type", ""), _json.dumps(car_class_ids), s.get("license_class", ""))
                )
                con.execute("DELETE FROM series_schedule_tracks WHERE series_id=?", (series_id,))
                for round_num, tid in enumerate(track_ids, 1):
                    con.execute(
                        "INSERT INTO series_schedule_tracks (series_id, track_id, round_num) VALUES (?,?,?)",
                        (series_id, tid, round_num)
                    )
                imported += 1

        return {"ok": True, "imported": imported}

    @app.put("/api/series/{series_id}")
    async def update_series(series_id: int, payload: SeriesUpsertPayload):
        upsert_series(series_id, payload.series_name, payload.car_type, payload.car_class_ids)
        set_series_tracks(series_id, payload.track_ids)
        return {"ok": True}

    @app.delete("/api/series/{series_id}")
    async def remove_series(series_id: int):
        delete_series(series_id)
        return {"ok": True}

    # ── Track overlap analysis ────────────────────────────────────────────────
    @app.get("/api/overlap")
    async def track_overlap(series_ids: list[int] | None = Query(default=None)):
        """
        Devuelve tracks ordenadas por cuántas series las usan.
        Si series_ids está vacío, usa todas las series.
        Útil para decidir qué pistas comprar para correr más series.
        """
        all_tracks = await tracks_repo.get_all_tracks()
        manual = get_all_overrides()
        owned_tracks_manual = set(manual["tracks"])
        track_map = {t.track_id: t for t in all_tracks}

        series_list = schedule_get_all_series()
        if series_ids:
            series_list = [s for s in series_list if s["series_id"] in series_ids]

        # track_id → lista de series que la usan
        track_series: dict[int, list[dict]] = {}
        for s in series_list:
            track_ids = [t["track_id"] for t in s.get("tracks", [])]
            for tid in track_ids:
                track_series.setdefault(tid, []).append({
                    "series_id": s["series_id"],
                    "series_name": s["series_name"],
                    "car_type": s["car_type"],
                })

        result = []
        for tid, used_by in track_series.items():
            t = track_map.get(tid)
            if not t:
                continue
            owned = t.owned or tid in owned_tracks_manual
            result.append({
                "track_id": tid,
                "name": t.name,
                "country": t.country,
                "price": t.price,
                "owned": owned,
                "series_count": len(used_by),
                "used_by": used_by,
            })

        result.sort(key=lambda x: (-x["series_count"], x["owned"], x["name"]))
        return {"data": result}

    # ── Wishlist ──────────────────────────────────────────────────────────────
    @app.get("/api/wishlist")
    def get_wishlist_endpoint():
        wl = get_wishlist()
        all_tracks_sync = None
        return {"data": wl}

    @app.post("/api/wishlist/{item_type}/{item_id}")
    def wishlist_add_endpoint(item_type: str, item_id: int):
        if item_type not in ("car", "track"):
            return {"error": "item_type must be car or track"}
        wishlist_add(item_type, item_id)
        return {"ok": True}

    @app.delete("/api/wishlist/{item_type}/{item_id}")
    def wishlist_remove_endpoint(item_type: str, item_id: int):
        wishlist_remove(item_type, item_id)
        return {"ok": True}

    @app.delete("/api/wishlist")
    def wishlist_clear_endpoint():
        wishlist_clear()
        return {"ok": True}

    @app.get("/api/wishlist/summary")
    async def wishlist_summary():
        """Devuelve el wishlist con precios y series cubiertas."""
        wl = get_wishlist()
        all_tracks = await tracks_repo.get_all_tracks()
        all_cars_list = await cars_repo.get_all_cars()
        track_map = {t.track_id: t for t in all_tracks}
        car_map = {c.car_id: c for c in all_cars_list}

        total_cost = 0.0
        tracks_detail = []
        for tid in wl["tracks"]:
            t = track_map.get(tid)
            if t:
                total_cost += t.price
                tracks_detail.append({"track_id": tid, "name": t.name, "price": t.price, "country": t.country})

        cars_detail = []
        for cid in wl["cars"]:
            c = car_map.get(cid)
            if c:
                total_cost += c.price
                cars_detail.append({"car_id": cid, "name": c.name, "price": c.price})

        return {
            "data": {
                "tracks": tracks_detail,
                "cars": cars_detail,
                "total_cost": round(total_cost, 2),
                "total_items": len(wl["tracks"]) + len(wl["cars"]),
            }
        }

    # ── Catalog sync (from iRacing API when live) ────────────────────────────
    @app.post("/api/catalog/sync")
    async def catalog_sync():
        """
        Sincroniza el catálogo completo de autos y pistas desde la API de iRacing.
        Cuando USE_MOCK=false y hay credenciales válidas, trae el catálogo real y
        actualiza precios, nombres e IDs. Agrega contenido nuevo si aparece.
        """
        from infrastructure.storage.schedule_store import _conn
        import json as _json
        from dataclasses import asdict

        try:
            all_cars  = await cars_repo.get_all_cars()
            all_tracks = await tracks_repo.get_all_tracks()
        except Exception as e:
            return {"ok": False, "error": str(e)}

        with _conn() as con:
            for c in all_cars:
                con.execute(
                    """INSERT INTO catalog_cars (car_id, name, categories, car_class_id, car_class_name, price, owned)
                       VALUES (?,?,?,?,?,?,?)
                       ON CONFLICT(car_id) DO UPDATE SET
                           name=excluded.name,
                           categories=excluded.categories,
                           car_class_id=excluded.car_class_id,
                           car_class_name=excluded.car_class_name,
                           price=excluded.price""",
                    (c.car_id, c.name, _json.dumps(c.categories), c.car_class_id,
                     c.car_class_name, c.price, int(c.owned))
                )
            for t in all_tracks:
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
                     _json.dumps(configs))
                )

        return {"ok": True, "cars": len(all_cars), "tracks": len(all_tracks)}

    # ── Recommendations ───────────────────────────────────────────────────────
    @app.get("/api/recommendations")
    async def recommendations(
        bundle_size: int = 3,
        car_types: list[str] | None = Query(default=None),
        include_cars: bool = True,
    ):
        uc = GetPurchaseRecommendationsUseCase(cars_repo, tracks_repo)
        result = await uc.execute(
            bundle_size=bundle_size,
            car_types=car_types if car_types else None,
            include_cars=include_cars,
        )
        return {"data": result}

    return app
