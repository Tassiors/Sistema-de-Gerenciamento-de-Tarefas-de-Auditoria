"""
Rotas REST da API: Gestão de Gestores e Matriz de Visibilidade
==============================================================
Disponibiliza endpoints administrativos para cadastro e controle de gestores
autorizados e concessão de unidades na matriz de visibilidade do organograma.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..resources.database import get_app_db_session
from ..auth.auth import require_admin
from ..models import ResponsibleArea, GovernanceUnit
from ..services.visibility_service import (
    list_managers,
    create_manager,
    update_manager,
    delete_manager,
    get_subordinate_area_ids,
)

router = APIRouter(prefix="/api/admin/managers", tags=["Gestores e Matriz de Visibilidade"])


class ManagerCreatePayload(BaseModel):
    username: str
    name: str
    email: Optional[str] = None
    role: str = "GESTOR"
    responsible_area_id: Optional[int] = None
    is_active: bool = True
    extra_unit_ids: List[int] = []


class ManagerUpdatePayload(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    responsible_area_id: Optional[int] = None
    is_active: Optional[bool] = None
    extra_unit_ids: Optional[List[int]] = None


@router.get("", summary="Listar Gestores Cadastrados")
async def get_all_managers(
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(require_admin),
):
    return await list_managers(session)


@router.post("", summary="Cadastrar Novo Gestor", status_code=status.HTTP_201_CREATED)
async def add_manager(
    payload: ManagerCreatePayload,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(require_admin),
):
    try:
        return await create_manager(session, payload.model_dump())
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.put("/{manager_id}", summary="Atualizar Gestor e Matriz de Visibilidade")
async def edit_manager(
    manager_id: int,
    payload: ManagerUpdatePayload,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(require_admin),
):
    try:
        return await update_manager(session, manager_id, payload.model_dump(exclude_unset=True))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.delete("/{manager_id}", summary="Remover Gestor")
async def remove_manager(
    manager_id: int,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(require_admin),
):
    success = await delete_manager(session, manager_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gestor não encontrado.")
    return {"message": "Gestor removido com sucesso."}


@router.get("/{manager_id}/subordinates", summary="Visualizar Áreas Subordinadas de um Gestor")
async def get_manager_subordinates(
    manager_id: int,
    session: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(require_admin),
):
    from ..services.visibility_service import get_manager_by_id
    try:
        mgr = await get_manager_by_id(session, manager_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))

    area_id = mgr.get("responsible_area_id")
    if not area_id:
        return {"subordinate_area_ids": [], "items": []}

    sub_ids = await get_subordinate_area_ids(session, area_id)
    stmt = select(ResponsibleArea).where(ResponsibleArea.id.in_(sub_ids)).order_by(ResponsibleArea.level, ResponsibleArea.nome)
    res = await session.execute(stmt)
    areas = res.scalars().all()

    return {
        "subordinate_area_ids": list(sub_ids),
        "items": [
            {"id": a.id, "nome": a.nome, "sigla": a.sigla, "level": a.level, "parent_id": a.parent_id}
            for a in areas
        ]
    }
