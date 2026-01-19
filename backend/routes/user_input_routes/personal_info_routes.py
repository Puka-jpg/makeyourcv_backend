from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.personal_info_operations import (
    PersonalInfoOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.personal_info_schemas import (
    PersonalInfoCreateSchema,
    PersonalInfoResponseSchema,
    PersonalInfoUpdateSchema,
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
            "model": PersonalInfoResponseSchema,
            "description": "Personal info created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Personal info already exists  ",
        },
    },
)
async def create_personal_info(
    info_payload: PersonalInfoCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create personal info for a user"""
    info_ops = PersonalInfoOperations(db)

    # Check for existing
    existing = await info_ops.get_personal_info_by_user_id(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Personal Info already exists for this user. Use PUT to update.",
        )

    personal_info = await info_ops.create_personal_info(info_payload, current_user.id)
    return personal_info


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": PersonalInfoResponseSchema,
            "description": "Personal info retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Personal info not found",
        },
    },
)
async def get_my_personal_info(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get personal info for current user"""
    info_ops = PersonalInfoOperations(db)
    personal_info = await info_ops.get_personal_info_by_user_id(current_user.id)

    if not personal_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal info not found",
        )

    return personal_info


@router.put(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": PersonalInfoResponseSchema,
            "description": "Personal info updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Personal info not found",
        },
    },
)
async def update_my_personal_info(
    info_payload: PersonalInfoUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update personal info"""
    info_ops = PersonalInfoOperations(db)
    personal_info = await info_ops.update_personal_info_by_user(
        current_user.id, info_payload
    )

    if not personal_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal info not found",
        )

    return personal_info


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Personal info deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Personal info not found",
        },
    },
)
async def delete_my_personal_info(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete personal info"""
    info_ops = PersonalInfoOperations(db)
    deleted = await info_ops.delete_personal_info_by_user(current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal info not found",
        )

    return None
