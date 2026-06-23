"""One-time scaffold: v9.5 22×12 fractal structure."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "townpulse"

DOMAINS = [
    "region",
    "village",
    "snap_population",
    "snap_building",
    "snap_transport",
    "snap_statistics",
    "tvi_score",
    "prescription_type",
    "prescription_indicator",
    "prescription_fund_source",
    "dispatch_rule",
    "budget_unit_price",
    "prescription_result",
    "budget_estimate",
    "organization",
    "subscription",
    "user",
    "report",
    "dashboard_orchestrator",
    "village_detail_orchestrator",
    "report_orchestrator",
    "public_data_sync_orchestrator",
]


def pascal(s: str) -> str:
    return "".join(p.capitalize() for p in s.split("_"))


def ensure(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main() -> None:
    for d in [
        "domain/entities",
        "domain/value_objects",
        "app/ports/input",
        "app/ports/output",
        "app/use_cases",
        "app/dtos",
        "adapter/inbound/api/v1",
        "adapter/inbound/api/schemas",
        "adapter/inbound/mappers",
        "adapter/outbound/orm",
        "adapter/outbound/orm_mappers",
        "adapter/outbound/repositories",
        "dependencies",
    ]:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    for domain in DOMAINS:
        P = pascal(domain)
        ensure(
            ROOT / f"domain/entities/{domain}_entity.py",
            f'''from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class {P}Entity:
    id: UUID
    created_at: datetime | None = None
''',
        )
        ensure(
            ROOT / f"app/dtos/{domain}_dto.py",
            f'''from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class {P}Dto:
    id: UUID
''',
        )
        ensure(
            ROOT / f"app/ports/input/{domain}_use_case.py",
            f'''from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.{domain}_dto import {P}Dto


class {P}UseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> {P}Dto | None:
        ...
''',
        )
        ensure(
            ROOT / f"app/ports/output/{domain}_port.py",
            f'''from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.{domain}_entity import {P}Entity


class {P}Port(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> {P}Entity | None:
        ...
''',
        )
        ensure(
            ROOT / f"app/use_cases/{domain}_interactor.py",
            f'''from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.{domain}_dto import {P}Dto
from apps.townpulse.app.ports.input.{domain}_use_case import {P}UseCase
from apps.townpulse.app.ports.output.{domain}_port import {P}Port


class {P}Interactor({P}UseCase):
    def __init__(self, port: {P}Port) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> {P}Dto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return {P}Dto(id=entity.id)
''',
        )
        ensure(
            ROOT / f"adapter/inbound/api/schemas/{domain}_schema.py",
            f'''from __future__ import annotations

from pydantic import BaseModel


class {P}Response(BaseModel):
    id: str
''',
        )
        ensure(
            ROOT / f"adapter/inbound/mappers/{domain}_mapper.py",
            f'''from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.{domain}_schema import {P}Response
from apps.townpulse.app.dtos.{domain}_dto import {P}Dto


class {P}Mapper:
    @staticmethod
    def to_response(dto: {P}Dto) -> {P}Response:
        return {P}Response(id=str(dto.id))
''',
        )
        ensure(
            ROOT / f"adapter/outbound/orm_mappers/{domain}_orm_mapper.py",
            f'''from __future__ import annotations

from apps.townpulse.domain.entities.{domain}_entity import {P}Entity


class {P}OrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> {P}Entity:
        return {P}Entity(id=orm_obj.id)
''',
        )
        ensure(
            ROOT / f"adapter/outbound/repositories/{domain}_repository.py",
            f'''from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.{domain}_port import {P}Port
from apps.townpulse.domain.entities.{domain}_entity import {P}Entity


class {P}Repository({P}Port):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> {P}Entity | None:
        return None
''',
        )
        ensure(
            ROOT / f"dependencies/{domain}_provider.py",
            f'''from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.{domain}_repository import {P}Repository
from apps.townpulse.app.ports.input.{domain}_use_case import {P}UseCase
from apps.townpulse.app.use_cases.{domain}_interactor import {P}Interactor
from core.matrix.grid_oracle_database_manager import get_db


def get_{domain}_repository(session: AsyncSession = Depends(get_db)) -> {P}Repository:
    return {P}Repository(session)


def get_{domain}_use_case(repo: {P}Repository = Depends(get_{domain}_repository)) -> {P}UseCase:
    return {P}Interactor(repo)
''',
        )
        ensure(
            ROOT / f"adapter/inbound/api/v1/{domain}_router.py",
            f'''from __future__ import annotations

from fastapi import APIRouter

{domain}_router = APIRouter(tags=["{domain}"])
''',
        )

    for pkg in [
        "domain",
        "domain/entities",
        "domain/value_objects",
        "app",
        "app/ports",
        "app/ports/input",
        "app/ports/output",
        "app/use_cases",
        "app/dtos",
        "adapter/inbound/api",
        "adapter/inbound/mappers",
        "adapter/outbound/orm",
        "adapter/outbound/orm_mappers",
    ]:
        ensure(ROOT / pkg / "__init__.py", "")

    print(f"scaffolded {len(DOMAINS)} domains under {ROOT}")


if __name__ == "__main__":
    main()
