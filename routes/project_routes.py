from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.project_operations import ProjectOperations
from dependencies.user_operations import UserOperations
from schemas.project_schemas import (
    ProjectCreateSchema,
    ProjectResponseSchema,
    ProjectUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
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
    payload: ProjectCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create project entry"""
    ops = ProjectOperations(db)
    user_ops = UserOperations(db)

    # Validate user exists
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )

    project = await ops.create_project(payload)
    return project


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[ProjectResponseSchema],
            "description": "List of projects retrieved successfully",
        },
    },
)
async def get_all_projects(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all projects for a user"""
    ops = ProjectOperations(db)
    projects = await ops.get_all_projects(user_id, skip=skip, limit=limit)
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
    project_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get single project by ID"""
    ops = ProjectOperations(db)
    project = await ops.get_project_by_id(project_id, user_id)

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
    project_id: int,
    payload: ProjectUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Update project entry"""
    ops = ProjectOperations(db)
    project = await ops.update_project(project_id, user_id, payload)

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
    project_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete project entry"""
    ops = ProjectOperations(db)
    deleted = await ops.delete_project(project_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return None
