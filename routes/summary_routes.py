from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.summary_operations import SummaryOperations
from dependencies.user_operations import UserOperations
from schemas.summary_schemas import (
    SummaryCreateSchema,
    SummaryResponseSchema,
    SummaryUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
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
    payload: SummaryCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create a summary for a user"""
    ops = SummaryOperations(db)
    user_ops = UserOperations(db)

    # Validate user exists
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )

    # Check if summary already exists
    if await ops.summary_exists(payload.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Summary already exists for user {payload.user_id}",
        )

    summary = await ops.create_summary(payload)
    return summary


@router.get(
    "/user/{user_id}",
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
async def get_summary_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get summary for a user"""
    ops = SummaryOperations(db)
    summary = await ops.get_summary_by_user_id(user_id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary not found for user {user_id}",
        )

    return summary


@router.get(
    "/{summary_id}",
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
async def get_summary_by_id(summary_id: int, db: AsyncSession = Depends(get_db)):
    """Get summary by ID"""
    ops = SummaryOperations(db)
    summary = await ops.get_summary_by_id(summary_id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary with id {summary_id} not found",
        )

    return summary


@router.put(
    "/{summary_id}",
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
async def update_summary(
    summary_id: int,
    payload: SummaryUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Update summary"""
    ops = SummaryOperations(db)
    summary = await ops.update_summary(summary_id, payload)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary with id {summary_id} not found",
        )

    return summary


@router.delete(
    "/{summary_id}",
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
async def delete_summary(summary_id: int, db: AsyncSession = Depends(get_db)):
    """Delete summary"""
    ops = SummaryOperations(db)
    deleted = await ops.delete_summary(summary_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary with id {summary_id} not found",
        )

    return None
