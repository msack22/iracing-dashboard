from dataclasses import dataclass
from domain.repositories.i_cars_repository import ICarsRepository
from domain.repositories.i_tracks_repository import ITracksRepository
from infrastructure.iracing.mock.mock_data import MOCK_SERIES
from infrastructure.storage.owned_store import get_all_overrides

DISCOUNT_TIERS = [(6, 0.15), (3, 0.10)]


def _get_discount(count: int) -> float:
    for min_items, discount in DISCOUNT_TIERS:
        if count >= min_items:
            return discount
    return 0.0


@dataclass
class ContentItem:
    type: str
    id: int
    name: str
    price: float
    series_count: int
    score: float
    car_type: str | None = None


@dataclass
class Bundle:
    items: list[ContentItem]
    total_price: float
    discount_pct: float
    savings: float
    final_price: float


class GetPurchaseRecommendationsUseCase:
    def __init__(self, cars_repo: ICarsRepository, tracks_repo: ITracksRepository) -> None:
        self._cars = cars_repo
        self._tracks = tracks_repo

    async def execute(
        self,
        bundle_size: int = 3,
        car_types: list[str] | None = None,
        include_cars: bool = True,
    ) -> dict:
        all_cars, all_tracks = await self._cars.get_all_cars(), await self._tracks.get_all_tracks()

        manual = get_all_overrides()
        owned_car_ids = set(manual["cars"])
        owned_track_ids = set(manual["tracks"])
        for c in all_cars:
            if c.car_id in owned_car_ids:
                c.owned = True
        for t in all_tracks:
            if t.track_id in owned_track_ids:
                t.owned = True

        owned_cars = [c for c in all_cars if c.owned]
        owned_tracks = [t for t in all_tracks if t.owned]
        total_spent = sum(c.price for c in owned_cars) + sum(t.price for t in owned_tracks)

        selected_series = MOCK_SERIES
        if car_types:
            selected_series = [s for s in MOCK_SERIES if s["car_type"] in car_types]

        relevant_class_ids: set[int] = set()
        relevant_track_ids: set[int] = set()
        for s in selected_series:
            relevant_class_ids.update(s["car_class_ids"])
            relevant_track_ids.update(s["season_tracks"])

        car_items: list[ContentItem] = []
        if include_cars:
            for c in all_cars:
                if c.owned or c.retired:
                    continue
                if car_types and c.car_class_id not in relevant_class_ids:
                    continue
                sc = await self._cars.get_series_count_by_car_id(c.car_id)
                car_type_label = _resolve_car_type(c.car_class_name, c.name)
                car_items.append(ContentItem(
                    type="car", id=c.car_id, name=c.name, price=c.price,
                    series_count=sc, score=sc * 10 - c.price * 0.5,
                    car_type=car_type_label,
                ))

        track_items: list[ContentItem] = []
        for t in all_tracks:
            if t.owned:
                continue
            if car_types and t.track_id not in relevant_track_ids:
                continue
            sc = await self._tracks.get_series_count_by_track_id(t.track_id)
            track_items.append(ContentItem(
                type="track", id=t.track_id, name=t.name, price=t.price,
                series_count=sc, score=sc * 10 - t.price * 0.5,
            ))

        all_items = sorted(car_items + track_items, key=lambda x: x.score, reverse=True)
        top_items = all_items[:20]
        bundles = _build_bundles(top_items, bundle_size)

        available_car_types = sorted({s["car_type"] for s in MOCK_SERIES})

        return {
            "top_items": [_item_to_dict(i) for i in top_items],
            "bundles": [_bundle_to_dict(b) for b in bundles],
            "investment_summary": {
                "owned_cars": len(owned_cars),
                "owned_tracks": len(owned_tracks),
                "total_spent": round(total_spent, 2),
            },
            "available_car_types": available_car_types,
            "selected_series": [
                {"series_name": s["series_name"], "car_type": s["car_type"]}
                for s in selected_series
            ],
        }


def _resolve_car_type(class_name: str, car_name: str) -> str:
    name = (class_name or car_name).lower()
    if "f4" in name or "formula 4" in name: return "F4"
    if "f3" in name or "formula 3" in name: return "F3"
    if "ir-01" in name or "ir01" in name: return "Formula iR"
    if "formula 2000" in name or "skip barber" in name: return "Formula 2000"
    if "lmp3" in name: return "LMP3"
    if "lmp2" in name: return "LMP2"
    if "gtp" in name: return "GTP"
    if "gt3 cup" in name or "cup" in name: return "GT3 Cup"
    if "gt3" in name: return "GT3"
    if "gt4" in name: return "GT4"
    if "mx-5" in name or "mx5" in name: return "MX-5"
    if "classic formula" in name or "lotus" in name: return "Classic F1"
    return class_name or "—"


def _build_bundles(items: list[ContentItem], size: int) -> list[Bundle]:
    bundles = []
    pool = list(items)
    while len(pool) >= size:
        chunk, pool = pool[:size], pool[size:]
        total = sum(i.price for i in chunk)
        disc = _get_discount(size)
        savings = round(total * disc, 2)
        bundles.append(Bundle(chunk, round(total, 2), disc, savings, round(total - savings, 2)))
    return bundles[:3]


def _item_to_dict(i: ContentItem) -> dict:
    d = {"type": i.type, "id": i.id, "name": i.name, "price": i.price,
         "series_count": i.series_count, "score": i.score}
    if i.car_type:
        d["car_type"] = i.car_type
    return d


def _bundle_to_dict(b: Bundle) -> dict:
    return {
        "items": [_item_to_dict(i) for i in b.items],
        "total_price": b.total_price,
        "discount_pct": b.discount_pct,
        "savings": b.savings,
        "final_price": b.final_price,
    }
