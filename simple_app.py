import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
import random

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.future import select

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./batches.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    batches = relationship("Batch", back_populates="user")

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    batch_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ship_date = Column(DateTime)
    label_layout = Column(String(50))
    label_format = Column(String(50))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="batches")
    shipments = relationship("BatchShipment", back_populates="batch", cascade="all, delete-orphan")
    rates = relationship("BatchRate", back_populates="batch", cascade="all, delete-orphan")
    errors = relationship("BatchError", back_populates="batch", cascade="all, delete-orphan")

class BatchShipment(Base):
    __tablename__ = "batch_shipments"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    shipment_id = Column(String(255), nullable=False)
    tracking_number = Column(String(255))
    carrier = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("Batch", back_populates="shipments")

class BatchRate(Base):
    __tablename__ = "batch_rates"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    rate_id = Column(String(255), nullable=False)
    carrier = Column(String(100))
    amount = Column(Float)
    currency = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("Batch", back_populates="rates")

class BatchError(Base):
    __tablename__ = "batch_errors"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    error_code = Column(String(100))
    error_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("Batch", back_populates="errors")

# Pydantic schemas
class ShipmentCreate(BaseModel):
    shipment_id: str

class RateCreate(BaseModel):
    rate_id: str

class BatchAddRequest(BaseModel):
    shipment_ids: List[str] = []
    rate_ids: List[str] = []

class BatchRemoveRequest(BaseModel):
    shipment_ids: List[str] = []
    rate_ids: List[str] = []

class BatchProcessRequest(BaseModel):
    ship_date: datetime
    label_layout: str = "4x6"
    label_format: str = "pdf"

class BatchResponse(BaseModel):
    id: int
    batch_id: str
    status: str
    ship_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    id: int
    error_code: Optional[str]
    error_message: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="FastAPI Batches Simple", version="1.0.0")

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Startup event
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create test user
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(email="test@example.com", full_name="Test User")
            session.add(user)
            await session.commit()

# Get test user
async def get_current_user(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == "test@example.com"))
    return result.scalar_one()

# Endpoints
@app.get("/")
async def root():
    return {
        "message": "FastAPI Batches Simple API",
        "docs": "/docs",
        "endpoints": [
            "POST /batches/{batch_id}/add",
            "GET /batches/{batch_id}",
            "GET /batches/{batch_id}/errors",
            "POST /batches/{batch_id}/process",
            "POST /batches/{batch_id}/remove",
        ]
    }

@app.post("/batches/{batch_id}/add", status_code=204)
async def add_to_batch(
    batch_id: str,
    request: BatchAddRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(select(Batch).where(Batch.batch_id == batch_id))
    batch = result.scalar_one_or_none()
    
    if not batch:
        batch = Batch(batch_id=batch_id, user_id=user.id)
        db.add(batch)
        await db.flush()
    
    for ship_id in request.shipment_ids:
        shipment = BatchShipment(
            batch_id=batch.id,
            shipment_id=ship_id,
            tracking_number=f"1Z{random.randint(100000, 999999):08d}",
            carrier=random.choice(["fedex", "ups", "usps"])
        )
        db.add(shipment)
    
    for rate_id in request.rate_ids:
        rate = BatchRate(
            batch_id=batch.id,
            rate_id=rate_id,
            carrier=random.choice(["fedex", "ups"]),
            amount=round(random.uniform(15, 100), 2),
            currency="USD"
        )
        db.add(rate)
    
    await db.commit()
    return None

@app.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Batch).where(Batch.batch_id == batch_id, Batch.user_id == user.id)
    )
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return batch

@app.get("/batches/{batch_id}/errors", response_model=List[ErrorResponse])
async def get_batch_errors(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Batch).where(Batch.batch_id == batch_id, Batch.user_id == user.id)
    )
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    result = await db.execute(
        select(BatchError).where(BatchError.batch_id == batch.id)
    )
    return result.scalars().all()

@app.post("/batches/{batch_id}/process", status_code=204)
async def process_batch(
    batch_id: str,
    request: BatchProcessRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Batch).where(Batch.batch_id == batch_id, Batch.user_id == user.id)
    )
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    batch.ship_date = request.ship_date
    batch.label_layout = request.label_layout
    batch.label_format = request.label_format
    batch.status = "processing"
    
    await db.commit()
    return None

@app.post("/batches/{batch_id}/remove", status_code=204)
async def remove_from_batch(
    batch_id: str,
    request: BatchRemoveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Batch).where(Batch.batch_id == batch_id, Batch.user_id == user.id)
    )
    batch = result.scalar_one_or_none()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if request.shipment_ids:
        result = await db.execute(
            select(BatchShipment).where(
                BatchShipment.batch_id == batch.id,
                BatchShipment.shipment_id.in_(request.shipment_ids)
            )
        )
        for shipment in result.scalars():
            await db.delete(shipment)
    
    if request.rate_ids:
        result = await db.execute(
            select(BatchRate).where(
                BatchRate.batch_id == batch.id,
                BatchRate.rate_id.in_(request.rate_ids)
            )
        )
        for rate in result.scalars():
            await db.delete(rate)
    
    await db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
