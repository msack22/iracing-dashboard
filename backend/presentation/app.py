from fastapi import FastAPI, Query, UploadFile, File, Form
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
    get_current_week, set_current_week,
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
    async def import_pdf(file: UploadFile = File(...), skip_weekly: bool = Form(False)):
        """
        Acepta el PDF "Current iRacing Race Schedule" (todas las categorías),
        extrae el texto con pdftotext -layout (preserva columnas) y parsea
        series + pistas de cada temporada. Devuelve ParsedSeries[] para que
        el usuario revise y confirme.

        skip_weekly: si es True, omite las series "Nth Week ..." (sesiones
        sueltas de la temporada anterior que todavía aparecen en el PDF pero
        no representan un calendario de temporada completo).
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
                ["pdftotext", "-layout", tmp_path, "-"],
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

        def derive_car_info(raw_names: list[str]) -> tuple[str, list[int]]:
            """Determina la clase de auto representativa y los car_class_id involucrados
            en una serie a partir de los nombres crudos parseados del PDF."""
            labels = []
            class_ids: list[int] = []
            for raw in raw_names:
                matched = match_car(raw)
                if matched:
                    labels.append(matched.car_class_name or matched.name)
                    if matched.car_class_id not in class_ids:
                        class_ids.append(matched.car_class_id)
            if not labels:
                return (raw_names[0] if raw_names else ""), class_ids
            return Counter(labels).most_common(1)[0][0], class_ids

        # ── Parsing ──────────────────────────────────────────────────────────
        # El PDF "Current iRacing Race Schedule" lista, por categoría
        # (OVAL / SPORTS CAR / FORMULA CAR / DIRT ... ) y clase de licencia
        # (R/D/C/B/A), cada serie con su temporada ("Series Name - 2026 Season N"),
        # los autos habilitados, y 12 líneas "Week N (YYYY-MM-DD)  Track  clima  formato".
        # Algunas entradas son sobrantes de la temporada anterior ("Nth Week ...")
        # con muy pocas rondas: se marcan como likely_weekly_guide y, si
        # skip_weekly=True, se descartan directamente.

        SECTION_RE = re.compile(r'^([RDCBA])\s+Class\s+Series\s*\(', re.IGNORECASE)
        # Las cabeceras de serie son "Nombre - YYYY Season N[ Fixed/Open]", pero el PDF
        # tiene variantes irregulares (sin número, "YYYY - Season N", años truncados a
        # 3 cifras). Como "Season" no aparece en ninguna otra línea del documento,
        # cualquier número (2-4 cifras) seguido de "Season" marca el final del nombre.
        HEADER_RE = re.compile(r'(.*?)\s*[-–]?\s*\d{2,4}\s*[-–]?\s*Season(?:\s+(\d+|Fixed|Open))?', re.IGNORECASE)
        # Formato invertido (sobrantes "Nth Week"): "2026 Season 2 - 13th Week - Nombre"
        REVERSED_HEADER_RE = re.compile(r'^\d{2,4}\s*[-–]?\s*Season\s+(\d+)\s*[-–]\s*(.+)$', re.IGNORECASE)
        TRACK_RE = re.compile(r'^Week\s+\d+\s*\(\d{4}-\d{2}-\d{2}\)\s+(.+)$')
        week_guide_re = re.compile(r'^\d+(?:st|nd|rd|th)\s+Week\b', re.IGNORECASE)

        def match_header(l: str):
            return HEADER_RE.search(l)

        def is_new_series(l: str) -> bool:
            # Una nueva sección de licencia, una cabecera "Nombre - YYYY Season N",
            # o una cabecera "Nth Week ..." sin sufijo de temporada (caso borde del PDF)
            # marcan siempre el inicio de una nueva serie.
            return bool(SECTION_RE.match(l) or match_header(l) or week_guide_re.match(l))

        # Filtrar líneas de la tabla de contenido (con "leader dots" tipo ". . . . 12")
        # y números de página sueltos.
        lines = []
        for raw_l in text.splitlines():
            if re.search(r'\.\s?\.\s?\.', raw_l):
                continue
            if re.match(r'^\s*\d+\s*$', raw_l):
                continue
            lines.append(raw_l.rstrip())

        parsed_series = []
        current_license = ""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            sec_m = SECTION_RE.match(line)
            if sec_m:
                current_license = sec_m.group(1).upper()
                i += 1
                continue

            header_match = match_header(line)
            week_only = None if header_match else week_guide_re.match(line)
            if header_match or week_only:
                if header_match:
                    series_name = header_match.group(1).strip(" -–")
                    season_num = header_match.group(2)
                    if not series_name:
                        # Formato invertido: "2026 Season 2 - 13th Week - Nombre"
                        rev_m = REVERSED_HEADER_RE.match(line)
                        if rev_m:
                            season_num = rev_m.group(1)
                            series_name = rev_m.group(2).strip(" -–")
                    if season_num and season_num.isdigit():
                        season = f"2026 Season {season_num}"
                    else:
                        season = "2026 Season 3"
                        if season_num:
                            # "Fixed"/"Open" venían después de "Season" sin número
                            # (ej. "NASCAR iRacing Series - 2026 Season Fixed") -
                            # se agregan al nombre para distinguir ambas variantes.
                            series_name = f"{series_name} - {season_num}"
                    # Sufijo "- Fixed"/"- Open" después del número de temporada
                    # (ej. "X - 2026 Season 3 - Fixed"), que si no se distingue
                    # produce dos series con el mismo nombre+temporada.
                    trailing = line[header_match.end():].strip(" -–")
                    if trailing.lower() in ("fixed", "open") and not series_name.lower().endswith(trailing.lower()):
                        series_name = f"{series_name} - {trailing}"
                else:
                    # Caso borde: cabecera "Nth Week ..." sin sufijo "- YYYY Season N"
                    series_name = line
                    season = "2026 Season 2"
                i += 1

                # Líneas de autos: vienen justo después del header, hasta la
                # línea de rango de licencia ("Rookie X.X --> Pro/WC X.X" o
                # "Class X X.X --> Pro/WC X.X")
                car_lines = []
                while i < len(lines):
                    l = lines[i].strip()
                    if not l:
                        i += 1
                        continue
                    if '-->' in l or TRACK_RE.match(l) or is_new_series(l):
                        break
                    car_lines.append(l)
                    i += 1
                cars_found = [c.strip() for c in " ".join(car_lines).split(",") if c.strip()]

                # La línea que rompió el loop contiene la clase de licencia mínima requerida
                # para entrar a la serie: "Class D 4.0 --> Pro/WC 4.0" o "Rookie X.X --> ...".
                # Eso es más útil que la sección del PDF para filtrar por licencia propia.
                series_license = current_license
                if i < len(lines) and '-->' in lines[i]:
                    lic_m = re.match(r'^(?:Class\s+([RDCBA])|Rookie)\s*[\d.]*\s*-->', lines[i].strip(), re.IGNORECASE)
                    if lic_m:
                        series_license = lic_m.group(1).upper() if lic_m.group(1) else 'R'

                # Líneas de pistas ("Week N (YYYY-MM-DD)   Track Name   clima...   formato")
                tracks_parsed = []
                while i < len(lines):
                    l = lines[i].strip()
                    if is_new_series(l):
                        break
                    track_m = TRACK_RE.match(l)
                    if track_m:
                        rest = track_m.group(1)
                        parts = re.split(r'\s{2,}', rest.strip())
                        raw_name = parts[0] if parts else ""
                        # Si el nombre de la pista pisa la columna de clima por falta de espacio
                        raw_name = re.split(r'\d+°[FC]', raw_name)[0].strip()
                        if raw_name:
                            matched_track = match_track(raw_name)
                            owned = False
                            if matched_track:
                                owned = matched_track.owned or matched_track.track_id in owned_tracks_manual
                            tracks_parsed.append({
                                "raw": raw_name,
                                "track_id": matched_track.track_id if matched_track else None,
                                "name": matched_track.name if matched_track else None,
                                "owned": owned,
                            })
                    i += 1

                is_weekly = bool(week_guide_re.match(series_name))
                if tracks_parsed and not (skip_weekly and is_weekly):
                    matched_count = sum(1 for t in tracks_parsed if t["track_id"] is not None)
                    car_type, car_class_ids = derive_car_info(cars_found)
                    parsed_series.append({
                        "series_name": series_name,
                        "season": season,
                        "car_names": cars_found,
                        "car_type": car_type,
                        "car_class_ids": car_class_ids,
                        "license_class": series_license,
                        "tracks": tracks_parsed,
                        "matched_count": matched_count,
                        "total_tracks": len(tracks_parsed),
                        "likely_weekly_guide": is_weekly,
                    })
                continue
            i += 1

        # Si la mayoría de las series detectadas son "guías semanales", avisar
        # antes de importar (los datos no representan un calendario de temporada).
        weekly_guide_count = sum(1 for s in parsed_series if s["likely_weekly_guide"])
        warning_type = None
        if parsed_series and weekly_guide_count >= len(parsed_series) / 2:
            warning_type = "likely_weekly_guide"

        return {"data": parsed_series, "warning_type": warning_type}

    class ImportConfirmPayload(BaseModel):
        series: list[dict]
        replace_existing: bool = False

    @app.post("/api/series/import-confirm")
    async def import_confirm(payload: ImportConfirmPayload):
        """
        Recibe las series seleccionadas (ya parseadas y revisadas por el usuario)
        e importa / sobreescribe en schedule_store.
        Si replace_existing=True, borra el calendario anterior por completo antes de importar.
        """
        import json as _json
        from infrastructure.storage.schedule_store import _conn

        imported = 0
        with _conn() as con:
            if payload.replace_existing:
                con.execute("DELETE FROM series_schedule_tracks")
                con.execute("DELETE FROM series_schedule")

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

                # dedupe preservando el orden: una pista puede repetirse en el calendario
                # de la serie (varias rondas en el mismo circuito), pero la tabla solo
                # admite una fila por (series_id, track_id)
                seen: set[int] = set()
                track_ids = []
                for t in s.get("tracks", []):
                    tid = t.get("track_id")
                    if tid and tid not in seen:
                        seen.add(tid)
                        track_ids.append(tid)
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
        Sólo cuenta rondas de la semana actual en adelante: si una pista ya
        corrió su ronda esta temporada, comprarla ahora no suma valor.
        Útil para decidir qué pistas comprar para correr más series.
        """
        all_tracks = await tracks_repo.get_all_tracks()
        manual = get_all_overrides()
        owned_tracks_manual = set(manual["tracks"])
        track_map = {t.track_id: t for t in all_tracks}
        current_week = get_current_week()

        series_list = schedule_get_all_series()
        if series_ids:
            series_list = [s for s in series_list if s["series_id"] in series_ids]

        # track_id → lista de series que la usan (sólo rondas que todavía no corrieron)
        track_series: dict[int, list[dict]] = {}
        for s in series_list:
            for t in s.get("tracks", []):
                if t.get("round_num", 0) and t["round_num"] < current_week:
                    continue
                track_series.setdefault(t["track_id"], []).append({
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
        return {"data": result, "current_week": current_week}

    # ── App settings ──────────────────────────────────────────────────────────
    @app.get("/api/settings/current-week")
    async def get_current_week_endpoint():
        return {"data": {"current_week": get_current_week()}}

    class CurrentWeekBody(BaseModel):
        week: int

    @app.post("/api/settings/current-week")
    async def set_current_week_endpoint(body: CurrentWeekBody):
        set_current_week(body.week)
        return {"ok": True, "current_week": get_current_week()}

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
                           owned=excluded.owned,
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
