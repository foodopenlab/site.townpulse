from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import PrescriptionTypeOrm
from apps.townpulse.adapter.outbound.orm_mappers.prescription_type_orm_mapper import PrescriptionTypeOrmMapper
from apps.townpulse.app.ports.output.prescription_type_port import PrescriptionTypePort
from apps.townpulse.domain.entities.prescription_type_entity import PrescriptionTypeEntity


class PrescriptionTypeRepository(PrescriptionTypePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> PrescriptionTypeEntity | None:
        row = await self._session.get(PrescriptionTypeOrm, entity_id)
        return PrescriptionTypeOrmMapper.to_entity(row) if row else None

    async def find_all_active(self) -> list[PrescriptionTypeEntity]:
        rows = (
            await self._session.execute(
                select(PrescriptionTypeOrm).where(PrescriptionTypeOrm.is_active.is_(True)).order_by(PrescriptionTypeOrm.code)
            )
        ).scalars().all()
        return [PrescriptionTypeOrmMapper.to_entity(r) for r in rows]

    async def find_by_code(self, code: str) -> PrescriptionTypeEntity | None:
        row = (
            await self._session.execute(select(PrescriptionTypeOrm).where(PrescriptionTypeOrm.code == code))
        ).scalar_one_or_none()
        return PrescriptionTypeOrmMapper.to_entity(row) if row else None
