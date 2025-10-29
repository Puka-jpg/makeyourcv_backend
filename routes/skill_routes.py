from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.skill_operations import SkillOperations
from schemas.skill_schemas import (
    SkillCreateSchema,
    SkillResponseSchema,
    SkillUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": SkillResponseSchema,
            "description": "Skill created successfully",
        },
    },
)
async def create_skill(
    skill_payload: SkillCreateSchema, db: AsyncSession = Depends(get_db)
):
    """Create a new skill"""
    skill_ops = SkillOperations(db)
    skill = await skill_ops.create_skill(skill_payload)
    return skill


@router.get(
    "/get_all_skills",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[SkillResponseSchema],
            "description": "List of all skills retrieved successfully",
        },
    },
)
async def get_all_skills(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all skills with optional pagination"""
    skill_ops = SkillOperations(db)
    skills = await skill_ops.get_all_skills(skip=skip, limit=limit)
    return skills


@router.get(
    "/get_skill/{skill_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SkillResponseSchema,
            "description": "Skill retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Skill not found",
        },
    },
)
async def get_skill_by_id(skill_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single skill by ID"""
    skill_ops = SkillOperations(db)
    skill = await skill_ops.get_skill_by_id(skill_id)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found",
        )

    return skill


@router.put(
    "/update_skill/{skill_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": SkillResponseSchema,
            "description": "Skill updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Skill not found",
        },
    },
)
async def update_skill(
    skill_id: int, skill_payload: SkillUpdateSchema, db: AsyncSession = Depends(get_db)
):
    """Update an existing skill"""
    skill_ops = SkillOperations(db)
    skill = await skill_ops.update_skill(skill_id, skill_payload)

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found",
        )

    return skill


@router.delete(
    "/delete_skill/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Skill deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Skill not found",
        },
    },
)
async def delete_skill(skill_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a skill"""
    skill_ops = SkillOperations(db)
    deleted = await skill_ops.delete_skill(skill_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} not found",
        )

    return None
