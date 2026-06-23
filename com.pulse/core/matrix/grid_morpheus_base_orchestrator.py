from __future__ import annotations

import asyncio
from typing import Any


class MorpheusOrchestratorBase:
    async def gather_use_cases(self, *awaitables: Any) -> list[Any]:
        return list(await asyncio.gather(*awaitables))
