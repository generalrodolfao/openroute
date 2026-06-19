"""
Rastreamento de custo por query, modelo e período.

Armazena custos em memória com limite diário configurável.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

from src.config import COST_LIMIT_DAILY


@dataclass
class CostEntry:
    provider: str
    model: str
    cost: float
    input_tokens: int
    output_tokens: int
    timestamp: float = field(default_factory=time.time)


class CostTracker:
    def __init__(self, daily_limit: float = COST_LIMIT_DAILY):
        self._entries: list[CostEntry] = []
        self._daily_limit = daily_limit

    def add(self, entry: CostEntry):
        self._entries.append(entry)

    def today(self) -> float:
        today_start = time.time() - (time.time() % 86400)
        return sum(e.cost for e in self._entries if e.timestamp >= today_start)

    def by_model(self) -> dict[str, float]:
        result: dict[str, float] = defaultdict(float)
        for e in self._entries:
            result[f"{e.provider}/{e.model}"] += e.cost
        return dict(result)

    def by_provider(self) -> dict[str, float]:
        result: defaultdict[str, float] = defaultdict(float)
        for e in self._entries:
            result[e.provider] += e.cost
        return dict(result)

    def total(self) -> float:
        return sum(e.cost for e in self._entries)

    def exceeded(self) -> bool:
        return self.today() >= self._daily_limit

    def summary(self) -> dict:
        return {
            "total_cost": round(self.total(), 6),
            "today_cost": round(self.today(), 6),
            "daily_limit": self._daily_limit,
            "exceeded": self.exceeded(),
            "by_model": self.by_model(),
            "by_provider": self.by_provider(),
            "total_queries": len(self._entries),
        }


_tracker: Optional[CostTracker] = None


def get_tracker() -> CostTracker:
    global _tracker
    if _tracker is None:
        _tracker = CostTracker()
    return _tracker
