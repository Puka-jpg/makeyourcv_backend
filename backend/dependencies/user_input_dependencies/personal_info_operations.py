from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import PersonalInfo
from schemas.user_input_schemas.personal_info_schemas import (
    PersonalInfoCreateSchema,
    PersonalInfoUpdateSchema,
)


class PersonalInfoOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_personal_info(
        self, payload: PersonalInfoCreateSchema, user_id: UUID
    ) -> PersonalInfo:
        """Create personal info in the database"""
        personal_info = PersonalInfo(
            user_id=user_id,
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            location=payload.location,
            linkedin_url=payload.linkedin_url,
            github_url=payload.github_url,
            portfolio_url=payload.portfolio_url,
            website_url=payload.website_url,
            professional_title=payload.professional_title,
        )
        self.db.add(personal_info)
        await self.db.commit()
        await self.db.refresh(personal_info)
        return personal_info

    async def get_personal_info_by_id(
        self, info_id: UUID, user_id: UUID
    ) -> Optional[PersonalInfo]:
        """Retrieve personal info by ID"""
        query = select(PersonalInfo).where(
            PersonalInfo.id == info_id, PersonalInfo.user_id == user_id
        )
        result = await self.db.execute(query)
        personal_info = result.scalar_one_or_none()
        return personal_info

    async def get_personal_info_by_user_id(
        self, user_id: UUID
    ) -> Optional[PersonalInfo]:
        """Retrieve personal info by User ID"""
        query = select(PersonalInfo).where(PersonalInfo.user_id == user_id)
        result = await self.db.execute(query)
        personal_info = result.scalar_one_or_none()
        return personal_info

    async def update_personal_info(
        self, info_id: UUID, user_id: UUID, payload: PersonalInfoUpdateSchema
    ) -> Optional[PersonalInfo]:
        """Update existing personal info"""
        personal_info = await self.get_personal_info_by_id(info_id, user_id)
        return await self._update_fields(personal_info, payload)

    async def update_personal_info_by_user(
        self, user_id: UUID, payload: PersonalInfoUpdateSchema
    ) -> Optional[PersonalInfo]:
        """Update existing personal info by User ID"""
        personal_info = await self.get_personal_info_by_user_id(user_id)
        return await self._update_fields(personal_info, payload)

    async def _update_fields(
        self, personal_info: Optional[PersonalInfo], payload: PersonalInfoUpdateSchema
    ) -> Optional[PersonalInfo]:
        if not personal_info:
            return None

        # Update only the fields that are provided
        if payload.full_name is not None:
            personal_info.full_name = payload.full_name

        if payload.email is not None:
            personal_info.email = payload.email

        if payload.phone is not None:
            personal_info.phone = payload.phone

        if payload.location is not None:
            personal_info.location = payload.location

        if payload.linkedin_url is not None:
            personal_info.linkedin_url = payload.linkedin_url

        if payload.github_url is not None:
            personal_info.github_url = payload.github_url

        if payload.portfolio_url is not None:
            personal_info.portfolio_url = payload.portfolio_url

        if payload.website_url is not None:
            personal_info.website_url = payload.website_url

        if payload.professional_title is not None:
            personal_info.professional_title = payload.professional_title

        await self.db.commit()
        await self.db.refresh(personal_info)
        return personal_info

    async def delete_personal_info(self, info_id: UUID, user_id: UUID) -> bool:
        """Delete personal info by ID"""
        personal_info = await self.get_personal_info_by_id(info_id, user_id)
        return await self._delete_obj(personal_info)

    async def delete_personal_info_by_user(self, user_id: UUID) -> bool:
        """Delete personal info by User ID"""
        personal_info = await self.get_personal_info_by_user_id(user_id)
        return await self._delete_obj(personal_info)

    async def _delete_obj(self, obj) -> bool:
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True
