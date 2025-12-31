from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.education_operations import (
    EducationOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.education_schemas import (
    EducationCreateSchema,
    EducationResponseSchema,
    EducationUpdateSchema,
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
            "model": EducationResponseSchema,
            "description": "Education created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_education(
    payload: EducationCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create education entry"""
    ops = EducationOperations(db)

    education = await ops.create_education(payload, user_id=current_user.id)
    return education


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[EducationResponseSchema],
            "description": "List of education entries retrieved successfully",
        },
    },
)
async def get_all_education(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all education entries for a user"""
    ops = EducationOperations(db)
    education_list = await ops.get_all_education(
        user_id=current_user.id, skip=skip, limit=limit
    )
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
    education_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get single education entry by ID"""
    ops = EducationOperations(db)
    education = await ops.get_education_by_id(education_id, current_user.id)

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
    education_id: UUID,
    payload: EducationUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update education entry"""
    ops = EducationOperations(db)
    education = await ops.update_education(education_id, payload, current_user.id)

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
    education_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete education entry"""
    ops = EducationOperations(db)
    deleted = await ops.delete_education(education_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Education with id {education_id} not found",
        )

    return None
