from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.custom_section_operations import (
    CustomSectionOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.custom_section_schemas import (
    CustomSectionCreateSchema,
    CustomSectionResponseSchema,
    CustomSectionUpdateSchema,
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
            "model": CustomSectionResponseSchema,
            "description": "Custom Section created successfully",
        },
    },
)
async def create_custom_section(
    payload: CustomSectionCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create custom section entry"""
    ops = CustomSectionOperations(db)
    custom_section = await ops.create_custom_section(payload, current_user.id)
    return custom_section


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[CustomSectionResponseSchema],
            "description": "Custom sections retrieved successfully",
        },
    },
)
async def get_all_custom_sections(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    """Get all custom sections for a user"""
    ops = CustomSectionOperations(db)
    custom_sections = await ops.get_all_custom_sections(current_user.id)
    return custom_sections


@router.get(
    "/{section_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomSectionResponseSchema,
            "description": "Custom section retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Custom section not found"},
    },
)
async def get_custom_section_by_id(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get single custom section by ID"""
    ops = CustomSectionOperations(db)
    custom_section = await ops.get_custom_section_by_id(section_id, current_user.id)
    if not custom_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Custom section not found"
        )
    return custom_section


@router.put(
    "/{section_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomSectionResponseSchema,
            "description": "Custom Section updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Custom section not found"},
    },
)
async def update_custom_section(
    section_id: UUID,
    payload: CustomSectionUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update custom section"""
    ops = CustomSectionOperations(db)
    update_custom_section = await ops.update_custom_section(
        section_id, current_user.id, payload
    )
    if not update_custom_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Custom section not found"
        )
    return update_custom_section


@router.delete(
    "/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Custom Section deleted Successfully"
        }
    },
)
async def delete_custom_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete custom section"""
    ops = CustomSectionOperations(db)
    deleted = await ops.delete_custom_section(section_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error deleting custom section",
        )
    return None
