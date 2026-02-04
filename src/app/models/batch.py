from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class Batch(Base):
    """
    Batch model for managing shipment batches
    """

    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ship_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    label_layout: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    label_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_scheme: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    shipments: Mapped[list["BatchShipment"]] = relationship(
        "BatchShipment", back_populates="batch", cascade="all, delete-orphan"
    )
    rates: Mapped[list["BatchRate"]] = relationship(
        "BatchRate", back_populates="batch", cascade="all, delete-orphan"
    )
    errors: Mapped[list["BatchError"]] = relationship(
        "BatchError", back_populates="batch", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Batch(id={self.id}, batch_id={self.batch_id}, status={self.status})>"


class BatchShipment(Base):
    """
    Model for shipments associated with a batch
    """

    __tablename__ = "batch_shipments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    shipment_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    service_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    label_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    batch: Mapped["Batch"] = relationship("Batch", back_populates="shipments")

    def __repr__(self) -> str:
        return f"<BatchShipment(id={self.id}, shipment_id={self.shipment_id})>"


class BatchRate(Base):
    """
    Model for rates associated with a batch
    """

    __tablename__ = "batch_rates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    rate_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    carrier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    service_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount: Mapped[Optional[float]] = mapped_column(nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    batch: Mapped["Batch"] = relationship("Batch", back_populates="rates")

    def __repr__(self) -> str:
        return f"<BatchRate(id={self.id}, rate_id={self.rate_id})>"


class BatchError(Base):
    """
    Model for errors associated with a batch
    """

    __tablename__ = "batch_errors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    batch: Mapped["Batch"] = relationship("Batch", back_populates="errors")

    def __repr__(self) -> str:
        return f"<BatchError(id={self.id}, error_code={self.error_code})>"
