from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.education_operations import EducationOperations
from dependencies.user_operations import UserOperations
from schemas.education_schemas import (
    EducationCreateSchema,
    EducationResponseSchema,
    EducationUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": EducationResponseSchema,
            "description": "Education created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_education(
    payload: EducationCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create education entry"""
    ops = EducationOperations(db)
    user_ops = UserOperations(db)

    # Validate user exists
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )

    education = await ops.create_education(payload)
    return education


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[EducationResponseSchema],
            "description": "List of education entries retrieved successfully",
        },
    },
)
async def get_all_education(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all education entries for a user"""
    ops = EducationOperations(db)
    education_list = await ops.get_all_education(user_id, skip=skip, limit=limit)
    return education_list


@router.get(
    "/{education_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": EducationResponseSchema,
            "description": "Education retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Education not found",
        },
    },
)
async def get_education_by_id(
    education_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get single education entry by ID"""
    ops = EducationOperations(db)
    education = await ops.get_education_by_id(education_id, user_id)

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education with id {education_id} not found",
        )

    return education


@router.put(
    "/{education_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": EducationResponseSchema,
            "description": "Education updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Education not found",
        },
    },
)
async def update_education(
    education_id: int,
    payload: EducationUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Update education entry"""
    ops = EducationOperations(db)
    education = await ops.update_education(education_id, user_id, payload)

    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education with id {education_id} not found",
        )

    return education


@router.delete(
    "/{education_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Education deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Education not found",
        },
    },
)
async def delete_education(
    education_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete education entry"""
    ops = EducationOperations(db)
    deleted = await ops.delete_education(education_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education with id {education_id} not found",
        )

    return None
