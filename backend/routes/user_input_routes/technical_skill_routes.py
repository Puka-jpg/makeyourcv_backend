from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.technical_skill_operations import (
    TechnicalSkillOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.technical_skill_schemas import (
    TechnicalSkillCreateSchema,
    TechnicalSkillResponseSchema,
    TechnicalSkillUpdateSchema,
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
            "model": TechnicalSkillResponseSchema,
            "description": "Technical skill created successfully",
        },
    },
)
async def create_technical_skill(
    payload: TechnicalSkillCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ops = TechnicalSkillOperations(db)
    experience = await ops.create_technical_skill(payload, user_id=current_user.id)
    return experience


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[TechnicalSkillResponseSchema],
            "description": "List of technical skills retrieved successfully",
        },
    },
)
async def get_all_technical_skills(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all technical skills for a user"""
    ops = TechnicalSkillOperations(db)
    skills = await ops.get_all_technical_skills(current_user.id, skip=skip, limit=limit)
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
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get single technical skill by ID"""
    ops = TechnicalSkillOperations(db)
    skill = await ops.get_technical_skill_by_id(skill_id, current_user.id)

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
    skill_id: UUID,
    payload: TechnicalSkillUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update technical skill entry"""
    ops = TechnicalSkillOperations(db)
    skill = await ops.update_technical_skill(skill_id, current_user.id, payload)

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
    skill_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete technical skill entry"""
    ops = TechnicalSkillOperations(db)
    deleted = await ops.delete_technical_skill(skill_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technical skill with id {skill_id} not found",
        )

    return None
