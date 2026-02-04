from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .crud_base import CRUDBase
from ..models.batch import Batch, BatchShipment, BatchRate, BatchError
from ..schemas.batch import BatchCreate, BatchUpdate


class CRUDBatch(CRUDBase[Batch, BatchCreate, BatchUpdate]):
    """
    CRUD operations for Batch model
    """

    async def get_by_batch_id(self, db: AsyncSession, *, batch_id: str) -> Optional[Batch]:
        """
        Get batch by batch_id string with all relationships loaded
        """
        result = await db.execute(
            select(Batch)
            .where(Batch.batch_id == batch_id)
            .options(
                selectinload(Batch.shipments),
                selectinload(Batch.rates),
                selectinload(Batch.errors),
            )
        )
        return result.scalar_one_or_none()

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: BatchCreate, user_id: int
    ) -> Batch:
        """
        Create new batch with user ID
        """
        db_obj = Batch(
            batch_id=obj_in.batch_id,
            user_id=user_id,
            ship_date=obj_in.ship_date,
            label_layout=obj_in.label_layout,
            label_format=obj_in.label_format,
            display_scheme=obj_in.display_scheme,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def add_shipments(
        self, db: AsyncSession, *, batch: Batch, shipment_ids: list[str]
    ) -> Batch:
        """
        Add shipments to batch
        """
        for shipment_id in shipment_ids:
            shipment = BatchShipment(
                batch_id=batch.id,
                shipment_id=shipment_id,
            )
            db.add(shipment)

        await db.flush()
        await db.refresh(batch)
        return batch

    async def add_rates(
        self, db: AsyncSession, *, batch: Batch, rate_ids: list[str]
    ) -> Batch:
        """
        Add rates to batch
        """
        for rate_id in rate_ids:
            rate = BatchRate(
                batch_id=batch.id,
                rate_id=rate_id,
            )
            db.add(rate)

        await db.flush()
        await db.refresh(batch)
        return batch

    async def remove_shipments(
        self, db: AsyncSession, *, batch: Batch, shipment_ids: list[str]
    ) -> Batch:
        """
        Remove shipments from batch
        """
        await db.execute(
            delete(BatchShipment).where(
                BatchShipment.batch_id == batch.id,
                BatchShipment.shipment_id.in_(shipment_ids),
            )
        )
        await db.flush()
        await db.refresh(batch)
        return batch

    async def remove_rates(
        self, db: AsyncSession, *, batch: Batch, rate_ids: list[str]
    ) -> Batch:
        """
        Remove rates from batch
        """
        await db.execute(
            delete(BatchRate).where(
                BatchRate.batch_id == batch.id,
                BatchRate.rate_id.in_(rate_ids),
            )
        )
        await db.flush()
        await db.refresh(batch)
        return batch

    async def get_errors(
        self, db: AsyncSession, *, batch: Batch, skip: int = 0, limit: int = 25
    ) -> list[BatchError]:
        """
        Get paginated errors for a batch
        """
        result = await db.execute(
            select(BatchError)
            .where(BatchError.batch_id == batch.id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_error(
        self,
        db: AsyncSession,
        *,
        batch: Batch,
        error_message: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> BatchError:
        """
        Add error to batch
        """
        error = BatchError(
            batch_id=batch.id,
            error_code=error_code,
            error_message=error_message,
            error_type=error_type,
            source=source,
        )
        db.add(error)
        await db.flush()
        await db.refresh(error)
        return error

    async def update_status(
        self, db: AsyncSession, *, batch: Batch, status: str
    ) -> Batch:
        """
        Update batch status
        """
        batch.status = status
        db.add(batch)
        await db.flush()
        await db.refresh(batch)
        return batch


batch = CRUDBatch(Batch)
