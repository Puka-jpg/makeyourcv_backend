from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Publication
from schemas.user_input_schemas.publication_schemas import (
    PublicationCreateSchema,
    PublicationUpdateSchema,
)


class PublicationOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_publication(self, payload: PublicationCreateSchema) -> Publication:
        """Create publication in the database"""
        publication = Publication(
            user_id=payload.user_id,
            title=payload.title,
            authors=payload.authors,
            publication_venue=payload.publication_venue,
            publication_date=payload.publication_date,
            doi=payload.doi,
            url=payload.url,
            description=payload.description,
            description_enhanced=None,  # Placeholder for AI
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(publication)
        await self.db.commit()
        await self.db.refresh(publication)
        return publication

    async def get_all_publications(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Publication]:
        """Retrieve all publications for a user"""
        query = (
            select(Publication)
            .where(Publication.user_id == user_id)
            .order_by(Publication.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        publications = result.scalars().all()
        return list(publications)

    async def get_publication_by_id(
        self, publication_id: int, user_id: int
    ) -> Optional[Publication]:
        """Retrieve single publication by ID"""
        query = select(Publication).where(
            Publication.id == publication_id, Publication.user_id == user_id
        )
        result = await self.db.execute(query)
        publication = result.scalar_one_or_none()
        return publication

    async def update_publication(
        self, publication_id: int, user_id: int, payload: PublicationUpdateSchema
    ) -> Optional[Publication]:
        """Update existing publication"""
        publication = await self.get_publication_by_id(publication_id, user_id)

        if not publication:
            return None

        if payload.title is not None:
            publication.title = payload.title
        if payload.authors is not None:
            publication.authors = payload.authors
        if payload.publication_venue is not None:
            publication.publication_venue = payload.publication_venue
        if payload.publication_date is not None:
            publication.publication_date = payload.publication_date
        if payload.doi is not None:
            publication.doi = payload.doi
        if payload.url is not None:
            publication.url = payload.url
        if payload.description is not None:
            publication.description = payload.description
        if payload.display_order is not None:
            publication.display_order = payload.display_order
        if payload.is_active is not None:
            publication.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(publication)
        return publication

    async def delete_publication(self, publication_id: int, user_id: int) -> bool:
        """Delete publication by ID"""
        publication = await self.get_publication_by_id(publication_id, user_id)

        if not publication:
            return False

        await self.db.delete(publication)
        await self.db.commit()
        return True
