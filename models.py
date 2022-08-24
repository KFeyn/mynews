from __future__ import annotations

import dataclasses
import datetime


@dataclasses.dataclass
class Article:
    link: str
    rating: str
    date: datetime.datetime

    @classmethod
    async def from_page(cls, el: tuple) -> Article:
        return cls(
            link=el[0],
            rating=el[1],
            date=el[2]
        )
