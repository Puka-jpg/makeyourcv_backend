from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Project
from schemas.project_schemas import ProjectCreateSchema, ProjectUpdateSchema


class ProjectOperations:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_project(self, payload: ProjectCreateSchema) -> Project:
        """Create project in the database"""
        project = Project(
            user_id=payload.user_id,
            project_name=payload.project_name,
            description=payload.description,
            highlights=payload.highlights,
            description_enhanced=None,  # Placeholder for AI
            highlights_enhanced=None,  # Placeholder for AI
            project_url=payload.project_url,
            github_url=payload.github_url,
            start_date=payload.start_date,
            end_date=payload.end_date,
            technologies_used=payload.technologies_used,
            is_featured=payload.is_featured,
            display_order=payload.display_order,
            is_active=payload.is_active,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_all_projects(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Retrieve all projects for a user"""
        query = (
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.display_order)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        projects = result.scalars().all()
        return list(projects)

    async def get_project_by_id(
        self, project_id: int, user_id: int
    ) -> Optional[Project]:
        """Retrieve single project by ID"""
        query = select(Project).where(
            Project.id == project_id, Project.user_id == user_id
        )
        result = await self.db.execute(query)
        project = result.scalar_one_or_none()
        return project

    async def update_project(
        self, project_id: int, user_id: int, payload: ProjectUpdateSchema
    ) -> Optional[Project]:
        """Update existing project"""
        project = await self.get_project_by_id(project_id, user_id)

        if not project:
            return None

        if payload.project_name is not None:
            project.project_name = payload.project_name
        if payload.description is not None:
            project.description = payload.description
        if payload.highlights is not None:
            project.highlights = payload.highlights
        if payload.project_url is not None:
            project.project_url = payload.project_url
        if payload.github_url is not None:
            project.github_url = payload.github_url
        if payload.start_date is not None:
            project.start_date = payload.start_date
        if payload.end_date is not None:
            project.end_date = payload.end_date
        if payload.technologies_used is not None:
            project.technologies_used = payload.technologies_used
        if payload.is_featured is not None:
            project.is_featured = payload.is_featured
        if payload.display_order is not None:
            project.display_order = payload.display_order
        if payload.is_active is not None:
            project.is_active = payload.is_active

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int, user_id: int) -> bool:
        """Delete project by ID"""
        project = await self.get_project_by_id(project_id, user_id)

        if not project:
            return False

        await self.db.delete(project)
        await self.db.commit()
        return True
