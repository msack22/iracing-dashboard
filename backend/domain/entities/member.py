from dataclasses import dataclass
from typing import Literal

LicenseCategory = Literal["road", "oval", "dirt_road", "dirt_oval"]


@dataclass
class License:
    category: LicenseCategory
    license_level_id: int
    group_name: str
    safety_rating: float
    irating: int
    ttrating: int


@dataclass
class Member:
    cust_id: int
    username: str
    display_name: str
    club: str
    licenses: list[License]
    member_since: str
    last_login: str
