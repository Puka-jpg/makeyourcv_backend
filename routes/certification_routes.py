from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.certification_operations import CertificationOperations
from dependencies.user_operations import UserOperations
from schemas.certification_schemas import (
    CertificationCreateSchema,
    CertificationResponseSchema,
    CertificationUpdateSchema,
)

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": CertificationResponseSchema,
            "description": "Certification created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_certification(
    payload: CertificationCreateSchema, db: AsyncSession = Depends(get_db)
):
    ops = CertificationOperations(db)
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(payload.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {payload.user_id} not found",
        )
    certification = await ops.create_certification(payload)
    return certification


@router.get(
    "/list",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[CertificationResponseSchema],
            "description": "List of certifications retrieved successfully",
        },
    },
)
async def get_all_certifications(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    ops = CertificationOperations(db)
    certifications = await ops.get_all_certifications(user_id, skip=skip, limit=limit)
    return certifications


@router.get(
    "/{certification_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CertificationResponseSchema,
            "description": "Certification retrieved successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Certification not found",
        },
    },
)
async def get_certification_by_id(
    certification_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    ops = CertificationOperations(db)
    certification = await ops.get_certification_by_id(certification_id, user_id)
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certification with id {certification_id} not found",
        )
    return certification


@router.put(
    "/{certification_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": CertificationResponseSchema,
            "description": "Certification updated successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Certification not found",
        },
    },
)
async def update_certification(
    certification_id: int,
    payload: CertificationUpdateSchema,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    ops = CertificationOperations(db)
    certification = await ops.update_certification(certification_id, user_id, payload)
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certification with id {certification_id} not found",
        )
    return certification


@router.delete(
    "/{certification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Certification deleted successfully",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Certification not found",
        },
    },
)
async def delete_certification(
    certification_id: int,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    ops = CertificationOperations(db)
    deleted = await ops.delete_certification(certification_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certification with id {certification_id} not found",
        )
    return None
