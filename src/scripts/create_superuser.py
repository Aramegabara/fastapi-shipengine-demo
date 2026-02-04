import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import AsyncSessionLocal
from src.app.core.config import settings
from src.app.crud.crud_user import user as crud_user
from src.app.schemas.user import UserCreate


async def create_superuser():
    """
    Create initial superuser for the application
    """
    async with AsyncSessionLocal() as db:
        # Check if superuser already exists
        existing_user = await crud_user.get_by_email(db, email=settings.ADMIN_EMAIL)

        if existing_user:
            print(f"Superuser with email {settings.ADMIN_EMAIL} already exists")
            return

        # Create superuser
        user_in = UserCreate(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            full_name="Admin User",
            is_superuser=True,
            is_active=True,
        )

        user_obj = await crud_user.create(db, obj_in=user_in)
        await db.commit()

        print(f"Superuser created successfully!")
        print(f"Email: {user_obj.email}")
        print(f"ID: {user_obj.id}")
        print(f"Remember to change the default password!")


if __name__ == "__main__":
    asyncio.run(create_superuser())
