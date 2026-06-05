from dataclasses import dataclass
from domain.repositories.i_cars_repository import ICarsRepository
from domain.repositories.i_tracks_repository import ITracksRepository

DISCOUNT_TIERS = [(6, 0.15), (3, 0.10)]


def _get_discount(count: int) -> float:
    for min_items, discount in DISCOUNT_TIERS:
        if count >= min_items:
            return discount
    return 0.0


@dataclass
class ContentItem:
    type: str        # 'car' | 'track'
    id: int
    name: str
    price: float
    series_count: int
    score: float


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

    async def execute(self, bundle_size: int = 3) -> dict:
        all_cars, all_tracks = await self._cars.get_all_cars(), await self._tracks.get_all_tracks()

        owned_cars = [c for c in all_cars if c.owned]
        owned_tracks = [t for t in all_tracks if t.owned]
        total_spent = sum(c.price for c in owned_cars) + sum(t.price for t in owned_tracks)

        car_items = []
        for c in all_cars:
            if not c.owned and not c.retired:
                sc = await self._cars.get_series_count_by_car_id(c.car_id)
                car_items.append(ContentItem("car", c.car_id, c.name, c.price, sc, sc * 10 - c.price * 0.5))

        track_items = []
        for t in all_tracks:
            if not t.owned:
                sc = await self._tracks.get_series_count_by_track_id(t.track_id)
                track_items.append(ContentItem("track", t.track_id, t.name, t.price, sc, sc * 10 - t.price * 0.5))

        all_items = sorted(car_items + track_items, key=lambda x: x.score, reverse=True)
        top_items = all_items[:20]

        bundles = []
        pool = list(top_items)
        while len(pool) >= bundle_size:
            chunk = pool[:bundle_size]
            pool = pool[bundle_size:]
            total = sum(i.price for i in chunk)
            disc = _get_discount(bundle_size)
            savings = round(total * disc, 2)
            bundles.append(Bundle(chunk, round(total, 2), disc, savings, round(total - savings, 2)))
        bundles = bundles[:3]

        return {
            "top_items": [vars(i) for i in top_items],
            "bundles": [
                {
                    "items": [vars(i) for i in b.items],
                    "total_price": b.total_price,
                    "discount_pct": b.discount_pct,
                    "savings": b.savings,
                    "final_price": b.final_price,
                }
                for b in bundles
            ],
            "investment_summary": {
                "owned_cars": len(owned_cars),
                "owned_tracks": len(owned_tracks),
                "total_spent": round(total_spent, 2),
            },
        }
