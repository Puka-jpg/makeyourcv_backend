from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.publication_operations import (
    PublicationOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.publication_schemas import (
    PublicationCreateSchema,
    PublicationResponseSchema,
    PublicationUpdateSchema,
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
            "model": PublicationResponseSchema,
            "description": "Publication created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_publication(
    payload: PublicationCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create publication entry"""
    ops = PublicationOperations(db)

    publication = await ops.create_publication(payload, current_user.id)
    return publication


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[PublicationResponseSchema],
            "description": "List of publications retrieved successfully",
        },
    },
)
async def get_all_publications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all publications for a user"""
    ops = PublicationOperations(db)
    publications = await ops.get_all_publications(
        current_user.id, skip=skip, limit=limit
    )
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
    publication_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get single publication by ID"""
    ops = PublicationOperations(db)
    publication = await ops.get_publication_by_id(publication_id, current_user.id)

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
    publication_id: UUID,
    payload: PublicationUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update publication entry"""
    ops = PublicationOperations(db)
    publication = await ops.update_publication(publication_id, payload, current_user.id)

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
    publication_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete publication entry"""
    ops = PublicationOperations(db)
    deleted = await ops.delete_publication(publication_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {publication_id} not found",
        )

    return None
