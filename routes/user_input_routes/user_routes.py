from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.user_operations import UserOperations
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.user_schemas import (
    UserResponseSchema,
    UserUpdateSchema,
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


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserResponseSchema,
            "description": "Current user retrieved successfully",
        },
    },
)
async def get_current_user_profile(current_user=Depends(get_current_user)):
    """Get current user's profile"""
    return current_user


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserResponseSchema,
            "description": "User updated successfully",
        },
    },
)
async def update_current_user(
    user_payload: UserUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update current user"""
    user_ops = UserOperations(db)
    user = await user_ops.update_user(current_user, user_payload)
    return user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User deleted successfully",
        },
    },
)
async def delete_current_user(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete current user"""
    user_ops = UserOperations(db)
    await user_ops.delete_user(current_user)
    return None
