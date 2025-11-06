from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.experience_operations import ExperienceOperations
from dependencies.user_operations import UserOperations
from schemas.experience_schemas import (
    ExperienceCreateSchema,
    ExperienceResponseSchema,
    ExperienceUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": ExperienceResponseSchema,
            "description": "Experience created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_experience(
    payload: ExperienceCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create experience entry"""
    ops = ExperienceOperations(db)
    user_ops = UserOperations(db)

    # Validate user exists
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )

    experience = await ops.create_experience(payload)
    return experience


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[ExperienceResponseSchema],
            "description": "List of experience entries retrieved successfully",
        },
    },
)
async def get_all_experience(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all experience entries for a user"""
    ops = ExperienceOperations(db)
    experience_list = await ops.get_all_experiences(user_id, skip=skip, limit=limit)
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
    experience_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get single experience entry by ID"""
    ops = ExperienceOperations(db)
    experience = await ops.get_experience_by_id(experience_id, user_id)

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
    experience_id: int,
    payload: ExperienceUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Update experience entry"""
    ops = ExperienceOperations(db)
    experience = await ops.update_experience(experience_id, user_id, payload)

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
    experience_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete experience entry"""
    ops = ExperienceOperations(db)
    deleted = await ops.delete_experience(experience_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experience with id {experience_id} not found",
        )

    return None
