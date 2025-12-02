from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.custom_section_operations import CustomSectionOperations
from dependencies.user_operations import UserOperations
from schemas.user_input_schemas.custom_section_schemas import (
    CustomSectionCreateSchema,
    CustomSectionResponseSchema,
    CustomSectionUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": CustomSectionResponseSchema,
            "description": "Custom section created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_custom_section(
    payload: CustomSectionCreateSchema, db: AsyncSession = Depends(get_db)
):
    ops = CustomSectionOperations(db)
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )
    custom_section = await ops.create_custom_section(payload)
    return custom_section


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[CustomSectionResponseSchema],
            "description": "List of custom sections retrieved successfully",
        },
    },
)
async def get_all_custom_sections(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    ops = CustomSectionOperations(db)
    custom_sections = await ops.get_all_custom_sections(user_id, skip=skip, limit=limit)
    return custom_sections


@router.get(
    "/{custom_section_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomSectionResponseSchema,
            "description": "Custom section retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Custom section not found",
        },
    },
)
async def get_custom_section_by_id(
    custom_section_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    ops = CustomSectionOperations(db)
    custom_section = await ops.get_custom_section_by_id(custom_section_id, user_id)
    if not custom_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom section with id {custom_section_id} not found",
        )
    return custom_section


@router.put(
    "/{custom_section_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CustomSectionResponseSchema,
            "description": "Custom section updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Custom section not found",
        },
    },
)
async def update_custom_section(
    custom_section_id: int,
    payload: CustomSectionUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    ops = CustomSectionOperations(db)
    custom_section = await ops.update_custom_section(
        custom_section_id, user_id, payload
    )
    if not custom_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom section with id {custom_section_id} not found",
        )
    return custom_section


@router.delete(
    "/{custom_section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Custom section deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Custom section not found",
        },
    },
)
async def delete_custom_section(
    custom_section_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    ops = CustomSectionOperations(db)
    deleted = await ops.delete_custom_section(custom_section_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom section with id {custom_section_id} not found",
        )
    return None
