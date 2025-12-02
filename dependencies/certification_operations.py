from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Certification
from schemas.user_input_schemas.certification_schemas import (
    CertificationCreateSchema,
    CertificationUpdateSchema,
)


class CertificationOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_certification(
        self, payload: CertificationCreateSchema
    ) -> Certification:
        """Create certification in the database"""
        certification = Certification(
            user_id=payload.user_id,
            certification_name=payload.certification_name,
            issuing_organization=payload.issuing_organization,
            issue_date=payload.issue_date,
            expiry_date=payload.expiry_date,
            credential_id=payload.credential_id,
            credential_url=payload.credential_url,
            description=payload.description,
            description_enhanced=None,  # Placeholder for AI
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(certification)
        await self.db.commit()
        await self.db.refresh(certification)
        return certification

    async def get_all_certifications(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Certification]:
        """Retrieve all certifications for a user"""
        query = (
            select(Certification)
            .where(Certification.user_id == user_id)
            .order_by(Certification.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        certifications = result.scalars().all()
        return list(certifications)

    async def get_certification_by_id(
        self, certification_id: int, user_id: int
    ) -> Optional[Certification]:
        """Retrieve single certification by ID"""
        query = select(Certification).where(
            Certification.id == certification_id, Certification.user_id == user_id
        )
        result = await self.db.execute(query)
        certification = result.scalar_one_or_none()
        return certification

    async def update_certification(
        self, certification_id: int, user_id: int, payload: CertificationUpdateSchema
    ) -> Optional[Certification]:
        """Update existing certification"""
        certification = await self.get_certification_by_id(certification_id, user_id)

        if not certification:
            return None

        if payload.certification_name is not None:
            certification.certification_name = payload.certification_name
        if payload.issuing_organization is not None:
            certification.issuing_organization = payload.issuing_organization
        if payload.issue_date is not None:
            certification.issue_date = payload.issue_date
        if payload.expiry_date is not None:
            certification.expiry_date = payload.expiry_date
        if payload.credential_id is not None:
            certification.credential_id = payload.credential_id
        if payload.credential_url is not None:
            certification.credential_url = payload.credential_url
        if payload.description is not None:
            certification.description = payload.description
        if payload.display_order is not None:
            certification.display_order = payload.display_order
        if payload.is_active is not None:
            certification.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(certification)
        return certification

    async def delete_certification(self, certification_id: int, user_id: int) -> bool:
        """Delete certification by ID"""
        certification = await self.get_certification_by_id(certification_id, user_id)

        if not certification:
            return False

        await self.db.delete(certification)
        await self.db.commit()
        return True
