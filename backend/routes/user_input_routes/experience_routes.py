from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.experience_operations import (
    ExperienceOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.experience_schemas import (
    ExperienceCreateSchema,
    ExperienceResponseSchema,
    ExperienceUpdateSchema,
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
            "model": ExperienceResponseSchema,
            "description": "Experience created successfully",
        },
    },
)
async def create_experience(
    payload: ExperienceCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create experience entry"""
    ops = ExperienceOperations(db)
    experience = await ops.create_experience(payload, user_id=current_user.id)
    return experience


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[ExperienceResponseSchema],
            "description": "List of experience entries retrieved successfully",
        },
    },
)
async def get_all_experience(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all experience entries for a user"""
    ops = ExperienceOperations(db)
    experience_list = await ops.get_all_experiences(
        current_user.id, skip=skip, limit=limit
    )
    return experience_list


@router.get(
    "/{experience_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": ExperienceResponseSchema,
            "description": "Experience retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experience not found",
        },
    },
)
async def get_experience_by_id(
    experience_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get single experience entry by ID"""
    ops = ExperienceOperations(db)
    experience = await ops.get_experience_by_id(experience_id, current_user.id)

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {experience_id} not found",
        )

    return experience


@router.put(
    "/{experience_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": ExperienceResponseSchema,
            "description": "Experience updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experience not found",
        },
    },
)
async def update_experience(
    experience_id: UUID,
    payload: ExperienceUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update experience entry"""
    ops = ExperienceOperations(db)
    experience = await ops.update_experience(experience_id, current_user.id, payload)

    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {experience_id} not found",
        )

    return experience


@router.delete(
    "/{experience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Experience deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Experience not found",
        },
    },
)
async def delete_experience(
    experience_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete experience entry"""
    ops = ExperienceOperations(db)
    deleted = await ops.delete_experience(experience_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {experience_id} not found",
        )

    return None
