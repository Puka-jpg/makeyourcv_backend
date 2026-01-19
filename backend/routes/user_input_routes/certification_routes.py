from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from dependencies.auth_dependencies.auth import get_current_user
from dependencies.user_input_dependencies.certification_operations import (
    CertificationOperations,
)
from schemas.common import ErrorResponseSchema
from schemas.user_input_schemas.certification_schemas import (
    CertificationCreateSchema,
    CertificationResponseSchema,
    CertificationUpdateSchema,
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
            "model": CertificationResponseSchema,
            "description": "Certification created successfully",
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "User not found",
        },
    },
)
async def create_certification(
    payload: CertificationCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ops = CertificationOperations(db)
    certification = await ops.create_certification(payload, current_user.id)
    return certification


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": List[CertificationResponseSchema],
            "description": "List of certifications retrieved successfully",
        },
    },
)
async def get_all_certifications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ops = CertificationOperations(db)
    certifications = await ops.get_all_certifications(
        current_user.id, skip=skip, limit=limit
    )
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
    certification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ops = CertificationOperations(db)
    certification = await ops.get_certification_by_id(certification_id, current_user.id)
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
    certification_id: UUID,
    payload: CertificationUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ops = CertificationOperations(db)
    certification = await ops.update_certification(
        certification_id, current_user.id, payload
    )
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
    certification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ops = CertificationOperations(db)
    deleted = await ops.delete_certification(certification_id, current_user)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certification with id {certification_id} not found",
        )
    return None
