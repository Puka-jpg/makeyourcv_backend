from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.summary_operations import SummaryOperations
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.summary_schemas import (
    SummaryCreateSchema,
    SummaryResponseSchema,
    SummaryUpdateSchema,
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
            "model": SummaryResponseSchema,
            "description": "Summary created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found or summary already exists",
        },
    },
)
async def create_summary(
    payload: SummaryCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a summary for the current user"""
    ops = SummaryOperations(db)
    existing = await ops.get_summary_by_user_id(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Summary already exists for this user. Use PUT to update.",
        )

    summary = await ops.create_summary(payload, user_id=current_user.id)
    return summary


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SummaryResponseSchema,
            "description": "Summary retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Summary not found",
        },
    },
)
async def get_my_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get current user's summary"""
    ops = SummaryOperations(db)
    summary = await ops.get_summary_by_user_id(current_user.id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return summary


@router.put(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SummaryResponseSchema,
            "description": "Summary updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Summary not found",
        },
    },
)
async def update_my_summary(
    payload: SummaryUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update current user's summary"""
    ops = SummaryOperations(db)
    summary = await ops.update_summary_by_user(current_user.id, payload)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return summary


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Summary deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Summary not found",
        },
    },
)
async def delete_my_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete current user's summary"""
    ops = SummaryOperations(db)
    deleted = await ops.delete_summary_by_user(current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found",
        )

    return None
