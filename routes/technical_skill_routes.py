from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.technical_skill_operations import TechnicalSkillOperations
from dependencies.user_operations import UserOperations
from schemas.technical_skill_schemas import (
    TechnicalSkillCreateSchema,
    TechnicalSkillResponseSchema,
    TechnicalSkillUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": TechnicalSkillResponseSchema,
            "description": "Technical skill created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_technical_skill(
    payload: TechnicalSkillCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create technical skill entry"""
    ops = TechnicalSkillOperations(db)
    user_ops = UserOperations(db)

    # Validate user exists
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )

    skill = await ops.create_technical_skill(payload)
    return skill


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[TechnicalSkillResponseSchema],
            "description": "List of technical skills retrieved successfully",
        },
    },
)
async def get_all_technical_skills(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all technical skills for a user"""
    ops = TechnicalSkillOperations(db)
    skills = await ops.get_all_technical_skills(user_id, skip=skip, limit=limit)
    return skills


@router.get(
    "/{skill_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": TechnicalSkillResponseSchema,
            "description": "Technical skill retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Technical skill not found",
        },
    },
)
async def get_technical_skill_by_id(
    skill_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Get single technical skill by ID"""
    ops = TechnicalSkillOperations(db)
    skill = await ops.get_technical_skill_by_id(skill_id, user_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical skill with id {skill_id} not found",
        )

    return skill


@router.put(
    "/{skill_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": TechnicalSkillResponseSchema,
            "description": "Technical skill updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Technical skill not found",
        },
    },
)
async def update_technical_skill(
    skill_id: int,
    payload: TechnicalSkillUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Update technical skill entry"""
    ops = TechnicalSkillOperations(db)
    skill = await ops.update_technical_skill(skill_id, user_id, payload)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical skill with id {skill_id} not found",
        )

    return skill


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Technical skill deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Technical skill not found",
        },
    },
)
async def delete_technical_skill(
    skill_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Delete technical skill entry"""
    ops = TechnicalSkillOperations(db)
    deleted = await ops.delete_technical_skill(skill_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical skill with id {skill_id} not found",
        )

    return None
