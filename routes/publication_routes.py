from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.publication_operations import PublicationOperations
from dependencies.user_operations import UserOperations
from schemas.publication_schemas import (
    PublicationCreateSchema,
    PublicationResponseSchema,
    PublicationUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": PublicationResponseSchema,
            "description": "Publication created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_publication(
    payload: PublicationCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create publication entry"""
    ops = PublicationOperations(db)
    user_ops = UserOperations(db)

    # Validate user exists
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )

    publication = await ops.create_publication(payload)
    return publication


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[PublicationResponseSchema],
            "description": "List of publications retrieved successfully",
        },
    },
)
async def get_all_publications(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all publications for a user"""
    ops = PublicationOperations(db)
    publications = await ops.get_all_publications(user_id, skip=skip, limit=limit)
    return publications


@router.get(
    "/{publication_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": PublicationResponseSchema,
            "description": "Publication retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Publication not found",
        },
    },
)
async def get_publication_by_id(
    publication_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get single publication by ID"""
    ops = PublicationOperations(db)
    publication = await ops.get_publication_by_id(publication_id, user_id)

    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {publication_id} not found",
        )

    return publication


@router.put(
    "/{publication_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": PublicationResponseSchema,
            "description": "Publication updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Publication not found",
        },
    },
)
async def update_publication(
    publication_id: int,
    payload: PublicationUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Update publication entry"""
    ops = PublicationOperations(db)
    publication = await ops.update_publication(publication_id, user_id, payload)

    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {publication_id} not found",
        )

    return publication


@router.delete(
    "/{publication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Publication deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Publication not found",
        },
    },
)
async def delete_publication(
    publication_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete publication entry"""
    ops = PublicationOperations(db)
    deleted = await ops.delete_publication(publication_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {publication_id} not found",
        )

    return None
