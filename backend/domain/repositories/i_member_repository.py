from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from domain.entities.member import Member


class IMemberRepository(ABC):
    @abstractmethod
    async def get_member_profile(self, cust_id: Optional[int] = None) -> Member: ...

    @abstractmethod
    async def get_irating_history(
        self, cust_id: Optional[int] = None, category: str = "road"
    ) -> List[Dict]: ...
