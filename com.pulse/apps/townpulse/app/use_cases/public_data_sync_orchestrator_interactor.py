from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.public_data_sync_orchestrator_dto import SyncJobLatestDto, SyncTriggerResultDto
from apps.townpulse.app.ports.input.public_data_sync_orchestrator_use_case import PublicDataSyncOrchestratorUseCase
from apps.townpulse.app.ports.output.public_data_sync_orchestrator_port import PublicDataSyncOrchestratorPort
from apps.townpulse.app.ports.output.region_port import RegionPort
from apps.townpulse.app.ports.output.snap_building_port import SnapBuildingPort
from apps.townpulse.app.ports.output.snap_population_port import SnapPopulationPort
from apps.townpulse.app.ports.output.snap_statistics_port import SnapStatisticsPort
from apps.townpulse.app.ports.output.snap_transport_port import SnapTransportPort
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.app.ports.output.village_port import VillagePort
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_morpheus_base_orchestrator import MorpheusOrchestratorBase

MIGRATION_CHUNKS = 10


class PublicDataSyncOrchestratorInteractor(PublicDataSyncOrchestratorUseCase, MorpheusOrchestratorBase):
    def __init__(
        self,
        sync_port: PublicDataSyncOrchestratorPort,
        region_port: RegionPort,
        village_port: VillagePort,
        snap_population_port: SnapPopulationPort,
        snap_building_port: SnapBuildingPort,
        snap_transport_port: SnapTransportPort,
        snap_statistics_port: SnapStatisticsPort,
        tvi_score_port: TviScorePort,
    ) -> None:
        self._sync_port = sync_port
        self._region_port = region_port
        self._village_port = village_port
        self._snap_population_port = snap_population_port
        self._snap_building_port = snap_building_port
        self._snap_transport_port = snap_transport_port
        self._snap_statistics_port = snap_statistics_port
        self._tvi_score_port = tvi_score_port

    async def collect_core(self, *, limit: int | None = None) -> SyncTriggerResultDto:
        """Phase A — vworld·pop#2#3·building·statistics·transport (API#4 제외)."""
        return await self.collect_all_core(limit=limit)

    async def collect_all_core(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        sync_dong_code: bool = True,
        sync_core: bool = True,
        sync_transport: bool = True,
        sigungu_code: str | None = None,
        sync_tvi: bool = True,
    ) -> SyncTriggerResultDto:
        job_id = await self._sync_port.save_job_started("MONTHLY_SNAP")
        try:
            processed = await self._run_phase_a(
                offset=offset,
                limit=limit,
                sync_dong_code=sync_dong_code,
                sync_core=sync_core,
                sync_transport=sync_transport,
                sigungu_code=sigungu_code,
            )
            tvi_updated = 0
            if sync_tvi:
                tvi_updated = await self._tvi_score_port.recalculate_all()
            km = get_keymaker()
            has_keys = bool(
                km.get_secret("POPULATION_HOUSEHOLD_API_KEY")
                or km.get_secret("BUILDING_HUB_API_KEY")
                or km.get_secret("VWORLD_API_KEY")
                or km.get_secret("BUS_ROUTE_API_KEY")
            )
            await self._sync_port.save_job_completed(job_id, processed)
            return SyncTriggerResultDto(
                job_id=str(job_id),
                status="COMPLETED",
                processed=processed,
                tvi_recalculated=tvi_updated,
                mock=not has_keys,
            )
        except Exception as exc:
            await self._sync_port.save_job_failed(job_id, str(exc))
            raise

    async def collect_migration_chunk(self, chunk_index: int) -> SyncTriggerResultDto:
        if chunk_index not in range(MIGRATION_CHUNKS):
            raise ValueError(f"chunk_index must be in range {MIGRATION_CHUNKS}")
        job_id = await self._sync_port.save_job_started("MIGRATION_CHUNK")
        try:
            villages = await self._village_port.find_all_for_geocode_sync()
            codes = [v.emd_code for v in villages if v.emd_code and len(v.emd_code) == 10]
            chunk = self._split_chunk(codes, MIGRATION_CHUNKS, chunk_index)
            processed = 0
            if get_keymaker().get_secret("POPULATION_MIGRATION_API_KEY"):
                for code in chunk:
                    await self._snap_population_port.ingest_migration_from_public_api(code)
                    processed += 1
            await self._sync_port.save_job_completed(job_id, processed)
            return SyncTriggerResultDto(
                job_id=str(job_id),
                status="COMPLETED",
                processed=processed,
                tvi_recalculated=0,
                mock=processed == 0,
            )
        except Exception as exc:
            await self._sync_port.save_job_failed(job_id, str(exc))
            raise

    async def finalize_monthly_snap(self) -> SyncTriggerResultDto:
        job_id = await self._sync_port.save_job_started("MONTHLY_SNAP")
        try:
            tvi_updated = await self._tvi_score_port.recalculate_all()
            await self._sync_port.save_job_completed(job_id, tvi_updated)
            return SyncTriggerResultDto(
                job_id=str(job_id),
                status="COMPLETED",
                processed=tvi_updated,
                tvi_recalculated=tvi_updated,
                mock=False,
            )
        except Exception as exc:
            await self._sync_port.save_job_failed(job_id, str(exc))
            raise

    async def collect_all(self) -> SyncTriggerResultDto:
        return await self.collect_all_core()

    async def ingest_fiscal_all(self) -> SyncTriggerResultDto:
        job_id = await self._sync_port.save_job_started("FISCAL_YEARLY")
        try:
            await self._region_port.ingest_fiscal_self_reliance()
            has_key = bool(get_keymaker().get_secret("FISCAL_RELIANCE_API_KEY"))
            await self._sync_port.save_job_completed(job_id, 1)
            return SyncTriggerResultDto(
                job_id=str(job_id),
                status="COMPLETED",
                processed=1,
                tvi_recalculated=0,
                mock=not has_key,
            )
        except Exception as exc:
            await self._sync_port.save_job_failed(job_id, str(exc))
            raise

    async def trigger_sync(self) -> SyncTriggerResultDto:
        return await self.collect_all_core()

    async def get_latest_job(self) -> SyncJobLatestDto | None:
        return await self._sync_port.get_latest_job()

    async def get_job_by_id(self, job_id: UUID) -> SyncJobLatestDto | None:
        return await self._sync_port.get_job_by_id(job_id)

    async def _run_phase_a(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        sync_dong_code: bool = True,
        sync_core: bool = True,
        sync_transport: bool = True,
        sigungu_code: str | None = None,
    ) -> int:
        km = get_keymaker()
        household_key = km.get_secret("POPULATION_HOUSEHOLD_API_KEY")
        age_key = km.get_secret("POPULATION_AGE_API_KEY")
        building_key = km.get_secret("BUILDING_HUB_API_KEY")
        vworld_key = km.get_secret("VWORLD_API_KEY")
        bus_key = km.get_secret("BUS_ROUTE_API_KEY")

        if household_key and sync_dong_code:
            await self._village_port.resolve_legal_dong_codes(household_key)

        villages = await self._village_port.find_all_for_geocode_sync()
        
        # Sort villages deterministically for chunking
        villages.sort(key=lambda v: (v.emd_code or "", str(v.id)))

        # Filter by sigungu_code if provided
        if sigungu_code is not None:
            villages = [v for v in villages if v.sigungu_code == sigungu_code]

        # Apply offset and limit
        if offset is not None or limit is not None:
            start = offset or 0
            end = start + limit if limit is not None else len(villages)
            villages = villages[start:end]

        processed = 0
        if sync_core:
            for village in villages:
                if vworld_key:
                    await self._village_port.update_geocode_from_vworld(village.id)
                if not village.emd_code or len(village.emd_code) != 10:
                    continue

                did_ingest = False
                if household_key and age_key:
                    await self._snap_population_port.ingest_core_from_public_api(village.emd_code)
                    did_ingest = True
                if building_key:
                    await self._snap_building_port.ingest_from_public_api(village.emd_code)
                    did_ingest = True
                if household_key and age_key:
                    await self._snap_statistics_port.ingest_from_public_api(village.emd_code)
                if did_ingest:
                    processed += 1

        if sync_transport:
            for village in villages:
                if bus_key or vworld_key:
                    await self._snap_transport_port.ingest_for_village(
                        village.id, apply_mock=not bus_key
                    )
                    if not sync_core:
                        processed += 1

        return processed

    @staticmethod
    def _split_chunk(codes: list[str], n: int, i: int) -> list[str]:
        size = (len(codes) + n - 1) // n
        return codes[i * size : (i + 1) * size]
