from __future__ import annotations
from dataclasses import dataclass
from typing import List, Literal

LicenseCategory = Literal["road", "oval", "dirt_road", "dirt_oval"]


@dataclass
class License:
    category: LicenseCategory
    license_level_id: int
    group_name: str       # 'Rookie', 'Class D', 'Class C', 'Class B', 'Class A', 'Pro'
    safety_rating: float  # 0.00 – 4.99
    irating: int
    ttrating: int


@dataclass
class Member:
    cust_id: int
    username: str
    display_name: str
    club: str
    licenses: List[License]
    member_since: str
    last_login: str
