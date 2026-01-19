from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.project_operations import ProjectOperations
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.project_schemas import (
    ProjectCreateSchema,
    ProjectResponseSchema,
    ProjectUpdateSchema,
)

router = APIRouter(
    dependencies=[Depends(get_current_user)],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponseSchema,
            "description": "Forbidden Response",
        }
    },
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": ProjectResponseSchema,
            "description": "Project created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_project(
    payload: ProjectCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create project entry"""
    ops = ProjectOperations(db)
    project = await ops.create_project(payload, current_user.id)
    return project


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[ProjectResponseSchema],
            "description": "List of projects retrieved successfully",
        },
    },
)
async def get_all_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all projects for a user"""
    ops = ProjectOperations(db)
    projects = await ops.get_all_projects(current_user.id, skip=skip, limit=limit)
    return projects


@router.get(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": ProjectResponseSchema,
            "description": "Project retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found",
        },
    },
)
async def get_project_by_id(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get single project by ID"""
    ops = ProjectOperations(db)
    project = await ops.get_project_by_id(project_id, current_user.id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return project


@router.put(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": ProjectResponseSchema,
            "description": "Project updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found",
        },
    },
)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update project entry"""
    ops = ProjectOperations(db)
    project = await ops.update_project(project_id, current_user.id, payload)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Project deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found",
        },
    },
)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete project entry"""
    ops = ProjectOperations(db)
    deleted = await ops.delete_project(project_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return None
