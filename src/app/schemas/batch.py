from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class BatchShipmentBase(BaseModel):
    """
    Base schema for batch shipment
    """

    shipment_id: str
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    service_code: Optional[str] = None


class BatchShipmentCreate(BatchShipmentBase):
    """
    Schema for creating a new batch shipment
    """

    label_data: Optional[dict[str, Any]] = None


class BatchShipment(BatchShipmentBase):
    """
    Schema for batch shipment returned from API
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    label_data: Optional[dict[str, Any]] = None
    created_at: datetime


class BatchRateBase(BaseModel):
    """
    Base schema for batch rate
    """

    rate_id: str
    carrier: Optional[str] = None
    service_type: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None


class BatchRateCreate(BatchRateBase):
    """
    Schema for creating a new batch rate
    """

    pass


class BatchRate(BatchRateBase):
    """
    Schema for batch rate returned from API
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    created_at: datetime


class BatchErrorBase(BaseModel):
    """
    Base schema for batch error
    """

    error_code: Optional[str] = None
    error_message: str
    error_type: Optional[str] = None
    source: Optional[str] = None


class BatchErrorCreate(BatchErrorBase):
    """
    Schema for creating a new batch error
    """

    pass


class BatchError(BatchErrorBase):
    """
    Schema for batch error returned from API
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    created_at: datetime


class BatchBase(BaseModel):
    """
    Base schema for batch
    """

    batch_id: str
    ship_date: Optional[datetime] = None
    label_layout: Optional[str] = Field(None, description="Layout format like 4x6, letter, A4")
    label_format: Optional[str] = Field(None, description="Label format like pdf, png, zpl")
    display_scheme: Optional[str] = Field(None, description="Display scheme for label")


class BatchCreate(BatchBase):
    """
    Schema for creating a new batch
    """

    pass


class BatchUpdate(BaseModel):
    """
    Schema for updating batch information
    """

    ship_date: Optional[datetime] = None
    label_layout: Optional[str] = None
    label_format: Optional[str] = None
    display_scheme: Optional[str] = None
    status: Optional[str] = None


class Batch(BatchBase):
    """
    Schema for batch returned from API
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    shipments: list[BatchShipment] = []
    rates: list[BatchRate] = []
    errors: list[BatchError] = []


class BatchAddRequest(BaseModel):
    """
    Request schema for adding shipments/rates to a batch
    """

    shipment_ids: list[str] = Field(default_factory=list, description="List of shipment IDs to add")
    rate_ids: list[str] = Field(default_factory=list, description="List of rate IDs to add")


class BatchRemoveRequest(BaseModel):
    """
    Request schema for removing shipments/rates from a batch
    """

    shipment_ids: list[str] = Field(default_factory=list, description="List of shipment IDs to remove")
    rate_ids: list[str] = Field(default_factory=list, description="List of rate IDs to remove")


class BatchProcessLabelsRequest(BaseModel):
    """
    Request schema for processing batch labels
    """

    ship_date: datetime
    label_layout: str = Field(default="4x6", description="Label layout format")
    label_format: str = Field(default="pdf", description="Label file format")
    display_scheme: str = Field(default="label", description="Display scheme")


class BatchErrorsResponse(BaseModel):
    """
    Response schema for batch errors
    """

    errors: list[BatchError]
    links: dict[str, str] = Field(default_factory=dict, description="Pagination links")


class PaginationParams(BaseModel):
    """
    Schema for pagination parameters
    """

    page: int = Field(default=1, ge=1, description="Page number")
    pagesize: int = Field(default=25, ge=1, le=100, description="Items per page")
