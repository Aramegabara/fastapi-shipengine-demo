import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_create_batch(client: AsyncClient, user_token_headers):
    """
    Test creating a new batch by adding items
    """
    batch_id = "test-batch-001"
    data = {
        "shipment_ids": ["ship-001", "ship-002"],
        "rate_ids": ["rate-001"],
    }

    response = await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/add",
        json=data,
        headers=user_token_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_batch(client: AsyncClient, user_token_headers):
    """
    Test getting batch information
    """
    # First create a batch
    batch_id = "test-batch-002"
    data = {
        "shipment_ids": ["ship-003"],
        "rate_ids": [],
    }

    await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/add",
        json=data,
        headers=user_token_headers,
    )

    # Get the batch
    response = await client.get(
        f"{settings.API_V1_STR}/batches/{batch_id}",
        headers=user_token_headers,
    )

    assert response.status_code == 200
    batch_data = response.json()
    assert batch_data["batch_id"] == batch_id
    assert len(batch_data["shipments"]) == 1


@pytest.mark.asyncio
async def test_get_batch_errors(client: AsyncClient, user_token_headers):
    """
    Test getting batch errors with pagination
    """
    batch_id = "test-batch-003"

    # Create batch
    data = {"shipment_ids": ["ship-004"], "rate_ids": []}
    await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/add",
        json=data,
        headers=user_token_headers,
    )

    # Get errors
    response = await client.get(
        f"{settings.API_V1_STR}/batches/{batch_id}/errors?page=1&pagesize=25",
        headers=user_token_headers,
    )

    assert response.status_code == 200
    errors_data = response.json()
    assert "errors" in errors_data
    assert "links" in errors_data


@pytest.mark.asyncio
async def test_process_batch_labels(client: AsyncClient, user_token_headers):
    """
    Test processing batch labels
    """
    batch_id = "test-batch-004"

    # Create batch
    data = {"shipment_ids": ["ship-005"], "rate_ids": []}
    await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/add",
        json=data,
        headers=user_token_headers,
    )

    # Process labels
    process_data = {
        "ship_date": "2026-02-10T10:00:00",
        "label_layout": "4x6",
        "label_format": "pdf",
        "display_scheme": "label",
    }

    response = await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/process/labels",
        json=process_data,
        headers=user_token_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remove_from_batch(client: AsyncClient, user_token_headers):
    """
    Test removing items from batch
    """
    batch_id = "test-batch-005"

    # Create batch
    data = {
        "shipment_ids": ["ship-006", "ship-007"],
        "rate_ids": ["rate-002"],
    }
    await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/add",
        json=data,
        headers=user_token_headers,
    )

    # Remove items
    remove_data = {
        "shipment_ids": ["ship-006"],
        "rate_ids": ["rate-002"],
    }

    response = await client.post(
        f"{settings.API_V1_STR}/batches/{batch_id}/remove",
        json=remove_data,
        headers=user_token_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_nonexistent_batch(client: AsyncClient, user_token_headers):
    """
    Test getting nonexistent batch returns 404
    """
    response = await client.get(
        f"{settings.API_V1_STR}/batches/nonexistent-batch",
        headers=user_token_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """
    Test accessing batch endpoints without authentication
    """
    response = await client.get(f"{settings.API_V1_STR}/batches/some-batch")

    assert response.status_code == 401
