from __future__ import annotations
from typing import Dict, List, Optional
from domain.entities.member import Member, License, LicenseCategory
from domain.repositories.i_member_repository import IMemberRepository
from infrastructure.iracing.mock.mock_data import MOCK_MEMBER, MOCK_IRATING_HISTORY


class MockMemberRepository(IMemberRepository):
    async def get_member_profile(self, cust_id: Optional[int] = None) -> Member:
        return MOCK_MEMBER

    async def get_irating_history(self, cust_id: Optional[int] = None, category: str = "road") -> List[Dict]:
        return MOCK_IRATING_HISTORY


class IracingMemberRepository(IMemberRepository):
    def __init__(self, client, default_cust_id: int) -> None:
        self._client = client
        self._cust_id = default_cust_id

    async def get_member_profile(self, cust_id: Optional[int] = None) -> Member:
        cid = cust_id or self._cust_id
        info = self._client.get_member_info()
        licenses_raw = info.get("licenses", [])
        licenses = []
        for lic in licenses_raw:
            cat_name = lic.get("category", "road").lower().replace(" ", "_")
            if cat_name not in ("road", "oval", "dirt_road", "dirt_oval"):
                cat_name = "road"
            licenses.append(
                License(
                    category=cat_name,  # type: ignore[arg-type]
                    license_level_id=lic.get("license_level", 0),
                    group_name=lic.get("group_name", ""),
                    safety_rating=lic.get("safety_rating", 0.0),
                    irating=lic.get("irating", 1350),
                    ttrating=lic.get("tt_rating", 0),
                )
            )
        return Member(
            cust_id=info.get("cust_id", cid),
            username=info.get("username", ""),
            display_name=info.get("display_name", ""),
            club=info.get("club_name", ""),
            licenses=licenses,
            member_since=info.get("member_since", ""),
            last_login=info.get("last_login", ""),
        )

    async def get_irating_history(self, cust_id: Optional[int] = None, category: str = "road") -> List[Dict]:
        cid = cust_id or self._cust_id
        try:
            data = self._client.stats_member_chart_data(cust_id=cid, category_id=2, chart_type=1)
            return [{"timestamp": p["when"], "irating": p["value"]} for p in data.get("data", {}).get("chunk_info", [])]
        except Exception:
            return []
