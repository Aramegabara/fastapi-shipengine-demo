from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_active_user
from ...core.database import get_db
from ...crud.crud_batch import batch as crud_batch
from ...models.user import User
from ...schemas.batch import (
    Batch as BatchSchema,
    BatchCreate,
    BatchUpdate,
    BatchAddRequest,
    BatchRemoveRequest,
    BatchProcessLabelsRequest,
    BatchErrorsResponse,
    BatchError as BatchErrorSchema,
)
from ...utils.cache import cache

router = APIRouter()


@router.post("/{batch_id}/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_to_batch(
    batch_id: str,
    request: BatchAddRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Add shipments or rates to a batch
    """
    batch = await crud_batch.get_by_batch_id(db, batch_id=batch_id)

    if not batch:
        # Create new batch if it doesn't exist
        batch_create = BatchCreate(batch_id=batch_id)
        batch = await crud_batch.create_with_user(db, obj_in=batch_create, user_id=current_user.id)

    # Add shipments if provided
    if request.shipment_ids:
        batch = await crud_batch.add_shipments(db, batch=batch, shipment_ids=request.shipment_ids)

    # Add rates if provided
    if request.rate_ids:
        batch = await crud_batch.add_rates(db, batch=batch, rate_ids=request.rate_ids)

    # Invalidate cache for this batch
    await cache.delete(f"batch:{batch_id}")

    return None


@router.get("/{batch_id}/errors", response_model=BatchErrorsResponse)
async def get_batch_errors(
    batch_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    pagesize: int = Query(25, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get errors for a batch with pagination
    """
    batch = await crud_batch.get_by_batch_id(db, batch_id=batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    # Check if user owns this batch
    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    skip = (page - 1) * pagesize
    errors = await crud_batch.get_errors(db, batch=batch, skip=skip, limit=pagesize)

    # Build pagination links
    links = {
        "first": f"/api/v1/batches/{batch_id}/errors?page=1&pagesize={pagesize}",
        "last": f"/api/v1/batches/{batch_id}/errors?page={page}&pagesize={pagesize}",
    }

    if page > 1:
        links["prev"] = f"/api/v1/batches/{batch_id}/errors?page={page-1}&pagesize={pagesize}"

    if len(errors) == pagesize:
        links["next"] = f"/api/v1/batches/{batch_id}/errors?page={page+1}&pagesize={pagesize}"

    return {"errors": errors, "links": links}


@router.post("/{batch_id}/process/labels", status_code=status.HTTP_204_NO_CONTENT)
async def process_batch_labels(
    batch_id: str,
    request: BatchProcessLabelsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Process batch ID labels
    """
    batch = await crud_batch.get_by_batch_id(db, batch_id=batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    # Check if user owns this batch
    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Update batch with processing information
    update_data = BatchUpdate(
        ship_date=request.ship_date,
        label_layout=request.label_layout,
        label_format=request.label_format,
        display_scheme=request.display_scheme,
        status="processing",
    )

    await crud_batch.update(db, db_obj=batch, obj_in=update_data)

    # Invalidate cache
    await cache.delete(f"batch:{batch_id}")

    # In production, this would trigger background job to process labels
    # For now, we just update the status

    return None


@router.post("/{batch_id}/remove", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_batch(
    batch_id: str,
    request: BatchRemoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Remove shipments or rates from a batch
    """
    batch = await crud_batch.get_by_batch_id(db, batch_id=batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    # Check if user owns this batch
    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Remove shipments if provided
    if request.shipment_ids:
        batch = await crud_batch.remove_shipments(
            db, batch=batch, shipment_ids=request.shipment_ids
        )

    # Remove rates if provided
    if request.rate_ids:
        batch = await crud_batch.remove_rates(db, batch=batch, rate_ids=request.rate_ids)

    # Invalidate cache
    await cache.delete(f"batch:{batch_id}")

    return None


@router.get("/{batch_id}", response_model=BatchSchema)
async def get_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get batch by ID with caching
    """
    # Try to get from cache first
    cached_batch = await cache.get(f"batch:{batch_id}")
    if cached_batch:
        return cached_batch

    batch = await crud_batch.get_by_batch_id(db, batch_id=batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    # Check if user owns this batch
    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Cache the result for 5 minutes
    batch_dict = {
        "id": batch.id,
        "batch_id": batch.batch_id,
        "user_id": batch.user_id,
        "status": batch.status,
        "ship_date": batch.ship_date.isoformat() if batch.ship_date else None,
        "label_layout": batch.label_layout,
        "label_format": batch.label_format,
        "display_scheme": batch.display_scheme,
        "created_at": batch.created_at.isoformat(),
        "updated_at": batch.updated_at.isoformat(),
        "shipments": [
            {
                "id": s.id,
                "batch_id": s.batch_id,
                "shipment_id": s.shipment_id,
                "tracking_number": s.tracking_number,
                "carrier": s.carrier,
                "service_code": s.service_code,
                "label_data": s.label_data,
                "created_at": s.created_at.isoformat(),
            }
            for s in batch.shipments
        ],
        "rates": [
            {
                "id": r.id,
                "batch_id": r.batch_id,
                "rate_id": r.rate_id,
                "carrier": r.carrier,
                "service_type": r.service_type,
                "amount": r.amount,
                "currency": r.currency,
                "created_at": r.created_at.isoformat(),
            }
            for r in batch.rates
        ],
        "errors": [
            {
                "id": e.id,
                "batch_id": e.batch_id,
                "error_code": e.error_code,
                "error_message": e.error_message,
                "error_type": e.error_type,
                "source": e.source,
                "created_at": e.created_at.isoformat(),
            }
            for e in batch.errors
        ],
    }

    await cache.set(f"batch:{batch_id}", batch_dict, expire=300)

    return batch


@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a batch completely
    """
    batch = await crud_batch.get_by_batch_id(db, batch_id=batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    if batch.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    await crud_batch.remove(db, id=batch.id)
    await cache.delete(f"batch:{batch_id}")

    return None
