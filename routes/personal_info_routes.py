from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.personal_info_operations import PersonalInfoOperations
from dependencies.user_operations import UserOperations
from schemas.personal_info_schemas import (
    PersonalInfoCreateSchema,
    PersonalInfoResponseSchema,
    PersonalInfoUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": PersonalInfoResponseSchema,
            "description": "Personal info created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Personal info already exists for this user or user not found",
        },
    },
)
async def create_personal_info(
    info_payload: PersonalInfoCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create personal info for a user"""
    info_ops = PersonalInfoOperations(db)
    user_ops = UserOperations(db)

    # Check if user exists
    user = await user_ops.get_user_by_id(info_payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {info_payload.user_id} not found",
        )

    # Check if personal info already exists for this user
    if await info_ops.personal_info_exists(info_payload.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Personal info already exists for user {info_payload.user_id}",
        )

    personal_info = await info_ops.create_personal_info(info_payload)
    return personal_info


@router.get(
    "/user/{user_id}",
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
async def get_personal_info_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get personal info for a user"""
    info_ops = PersonalInfoOperations(db)
    personal_info = await info_ops.get_personal_info_by_user_id(user_id)

    if not personal_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal info not found for user {user_id}",
        )

    return personal_info


@router.get(
    "/{info_id}",
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
async def get_personal_info_by_id(info_id: int, db: AsyncSession = Depends(get_db)):
    """Get personal info by ID"""
    info_ops = PersonalInfoOperations(db)
    personal_info = await info_ops.get_personal_info_by_id(info_id)

    if not personal_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal info with id {info_id} not found",
        )

    return personal_info


@router.put(
    "/{info_id}",
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
async def update_personal_info(
    info_id: int,
    info_payload: PersonalInfoUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Update personal info"""
    info_ops = PersonalInfoOperations(db)
    personal_info = await info_ops.update_personal_info(info_id, info_payload)

    if not personal_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal info with id {info_id} not found",
        )

    return personal_info


@router.delete(
    "/{info_id}",
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
async def delete_personal_info(info_id: int, db: AsyncSession = Depends(get_db)):
    """Delete personal info"""
    info_ops = PersonalInfoOperations(db)
    deleted = await info_ops.delete_personal_info(info_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Personal info with id {info_id} not found",
        )

    return None
