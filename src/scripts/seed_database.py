import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import AsyncSessionLocal
from src.app.core.config import settings
from src.app.crud.crud_user import user as crud_user
from src.app.crud.crud_batch import batch as crud_batch
from src.app.schemas.user import UserCreate
from src.app.schemas.batch import BatchCreate
from src.app.models.batch import BatchShipment, BatchRate, BatchError


async def seed_database():
    print("=" * 60)
    print("SEEDING DATABASE")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            # Create admin
            admin = await crud_user.get_by_email(db, email=settings.ADMIN_EMAIL)
            if not admin:
                admin = await crud_user.create(db, obj_in=UserCreate(
                    email=settings.ADMIN_EMAIL,
                    password=settings.ADMIN_PASSWORD,
                    full_name="Admin User",
                    is_superuser=True,
                ))
                print(f"✓ Admin: {admin.email}")
            else:
                print(f"✓ Admin exists: {admin.email}")
            
            # Create test users
            users = [admin]
            for i in range(1, 4):
                email = f"user{i}@example.com"
                user = await crud_user.get_by_email(db, email=email)
                if not user:
                    user = await crud_user.create(db, obj_in=UserCreate(
                        email=email,
                        password="password123",
                        full_name=f"Test User {i}",
                    ))
                    print(f"✓ User: {email}")
                users.append(user)
            
            await db.commit()
            
            # Create batches
            carriers = ["fedex", "ups", "usps", "dhl_express"]
            statuses = ["pending", "processing", "completed", "failed"]
            
            print("\nCreating batches...")
            for user in users[:2]:
                for i in range(5):
                    batch_id = f"se-{random.randint(10000000, 99999999)}"
                    existing = await crud_batch.get_by_batch_id(db, batch_id=batch_id)
                    if existing:
                        continue
                    
                    batch = await crud_batch.create_with_user(
                        db,
                        obj_in=BatchCreate(
                            batch_id=batch_id,
                            ship_date=datetime.utcnow() + timedelta(days=i+1),
                            label_layout="4x6",
                            label_format="pdf",
                            display_scheme="label",
                        ),
                        user_id=user.id
                    )
                    batch.status = random.choice(statuses)
                    
                    # Add shipments
                    for j in range(random.randint(2, 4)):
                        db.add(BatchShipment(
                            batch_id=batch.id,
                            shipment_id=f"ship-{random.randint(100000, 999999)}",
                            tracking_number=f"1Z{random.randint(100000, 999999):08d}",
                            carrier=random.choice(carriers),
                            service_code="priority",
                        ))
                    
                    # Add rates
                    for j in range(2):
                        db.add(BatchRate(
                            batch_id=batch.id,
                            rate_id=f"rate-{random.randint(100000, 999999)}",
                            carrier=random.choice(carriers),
                            service_type="priority",
                            amount=round(random.uniform(15.0, 100.0), 2),
                            currency="USD",
                        ))
                    
                    print(f"✓ Batch: {batch_id} ({batch.status})")
                
                await db.commit()
            
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
            print(f"\nAdmin: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
            print("User1: user1@example.com / password123")
            print("\nAPI: http://localhost:8000/docs")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
