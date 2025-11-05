from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.user_operations import UserOperations
from schemas.user_schemas import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": UserResponseSchema,
            "description": "User created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User already exists",
        },
    },
)
async def create_user(
    user_payload: UserCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    user_ops = UserOperations(db)

    # Check if user already exists
    if await user_ops.user_exists(
        username=user_payload.username, email=user_payload.email
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )

    user = await user_ops.create_user(user_payload)
    return user


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[UserResponseSchema],
            "description": "List of all users retrieved successfully",
        },
    },
)
async def get_all_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all users with optional pagination"""
    user_ops = UserOperations(db)
    users = await user_ops.get_all_users(skip=skip, limit=limit)
    return users


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserResponseSchema,
            "description": "User retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
    },
)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single user by ID"""
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


@router.put(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": UserResponseSchema,
            "description": "User updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
    },
)
async def update_user(
    user_id: int, user_payload: UserUpdateSchema, db: AsyncSession = Depends(get_db)
):
    """Update an existing user"""
    user_ops = UserOperations(db)
    user = await user_ops.update_user(user_id, user_payload)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "User deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
        },
    },
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a user (cascades to all related data)"""
    user_ops = UserOperations(db)
    deleted = await user_ops.delete_user(user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return None
