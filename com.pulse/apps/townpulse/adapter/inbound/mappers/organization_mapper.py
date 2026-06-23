from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.organization_schema import OrganizationResponse
from apps.townpulse.app.dtos.organization_dto import OrganizationDto


class OrganizationMapper:
    @staticmethod
    def to_response(dto: OrganizationDto) -> OrganizationResponse:
        return OrganizationResponse(id=str(dto.id))
