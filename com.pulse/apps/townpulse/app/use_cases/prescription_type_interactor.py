from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.prescription_type_dto import PrescriptionTypeDto, PrescriptionTypeListResult
from apps.townpulse.app.ports.input.prescription_type_use_case import PrescriptionTypeUseCase
from apps.townpulse.app.ports.output.prescription_type_port import PrescriptionTypePort
from apps.townpulse.domain.entities.prescription_type_entity import PrescriptionTypeEntity


class PrescriptionTypeInteractor(PrescriptionTypeUseCase):
    def __init__(self, port: PrescriptionTypePort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> PrescriptionTypeDto | None:
        entity = await self._port.find_by_id(entity_id)
        return self._to_dto(entity) if entity else None

    async def find_all_active(self) -> PrescriptionTypeListResult:
        entities = await self._port.find_all_active()
        items = [self._to_dto(e) for e in entities]
        return PrescriptionTypeListResult(items=items, total=len(items))

    async def find_by_code(self, code: str) -> PrescriptionTypeDto | None:
        entity = await self._port.find_by_code(code)
        return self._to_dto(entity) if entity else None

    @staticmethod
    def _to_dto(entity: PrescriptionTypeEntity) -> PrescriptionTypeDto:
        return PrescriptionTypeDto(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            category=entity.category,
            rollout_timeline=entity.rollout_timeline,
            is_active=entity.is_active,
        )
