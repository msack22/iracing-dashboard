from abc import ABC, abstractmethod
from domain.entities.member import Member


class IMemberRepository(ABC):
    @abstractmethod
    async def get_member_profile(self, cust_id: int | None = None) -> Member: ...

    @abstractmethod
    async def get_irating_history(
        self, cust_id: int | None = None, category: str = "road"
    ) -> list[dict]: ...
