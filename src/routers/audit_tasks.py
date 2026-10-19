"""
Rotas REST da API: Gestão de Tarefas de Auditoria e Governança
==============================================================
Disponibiliza endpoints para importação de planilhas do e-CGU,
atribuição de áreas responsáveis, listagem operacional e métricas analíticas.
"""

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..resources.database import get_app_db_session
from ..services.audit_service import (
    import_ecgu_spreadsheet,
    list_governance_units,
    list_responsible_areas,
    assign_responsible_area,
    get_audit_tasks,
    get_dashboard_metrics,
)

router = APIRouter(prefix="/api", tags=["Tarefas de Auditoria e Governança"])


class AreaAssignmentPayload(BaseModel):
    responsible_area_id: Optional[int] = None


@router.post(
    "/audit-tasks/import",
    summary="Importar Planilha do e-CGU",
    description="Faz upload da planilha oficial do e-CGU (.xlsx), processa tarefas incrementalmente e atualiza a base.",
)
async def import_audit_tasks(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_app_db_session),
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo inválido. Envie um arquivo Excel com extensão .xlsx ou .xls",
        )

    try:
        content = await file.read()
        res = await import_ecgu_spreadsheet(session, content, file.filename)
        return {
            "message": "Importação concluída com sucesso",
            "data": res,
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao processar arquivo: {str(e)}",
        )


@router.get(
    "/governance-units",
    summary="Listar Gerências (Governança)",
    description="Retorna as 4 gerências executivas (SUP, GAD, GAS, GEP) e seus respectivos setores.",
)
async def get_governance(session: AsyncSession = Depends(get_app_db_session)):
    return await list_governance_units(session)


@router.get(
    "/responsible-areas",
    summary="Listar Áreas Responsáveis",
    description="Lista as divisões e setores cadastrados, com filtro opcional por gerência.",
)
async def get_areas(
    governance_unit_id: Optional[int] = Query(None, description="ID da Gerência"),
    sigla: Optional[str] = Query(None, description="Sigla da Gerência (SUP, GAD, GAS, GEP)"),
    session: AsyncSession = Depends(get_app_db_session),
):
    return await list_responsible_areas(session, governance_unit_id, sigla)


@router.patch(
    "/audit-tasks/{task_id}/responsible-area",
    summary="Atribuir Área Responsável à Tarefa",
    description="Permite ao administrador vincular ou alterar a divisão/setor encarregado pela tarefa.",
)
async def set_task_area(
    task_id: str,
    payload: AreaAssignmentPayload,
    session: AsyncSession = Depends(get_app_db_session),
):
    try:
        res = await assign_responsible_area(session, task_id, payload.responsible_area_id)
        return {
            "message": "Área Responsável atualizada com sucesso",
            "data": res,
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@router.get(
    "/audit-tasks",
    summary="Listagem Operacional de Tarefas",
    description="Consulta paginada com busca textual e filtros dinâmicos por gerência, situação, prazo e tarefas sem área.",
)
async def list_tasks(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=500, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Busca textual por ID, Título ou Monitoramento"),
    sigla: Optional[str] = Query(None, description="Filtrar por sigla da Gerência (SUP, GAD, GAS, GEP)"),
    situation: Optional[str] = Query(None, description="Filtrar por Situação (Não atendida, Parcialmente Atendida, Concluída)"),
    prazo: Optional[str] = Query(None, description="Filtrar por Semáforo de Prazo (Prazo Amplo, Prazo Encerrando, Prazo Venceu)"),
    unassigned: Optional[bool] = Query(None, description="Filtrar tarefas pendentes sem Área Responsável"),
    is_active: bool = Query(True, description="Listar apenas tarefas ativas"),
    session: AsyncSession = Depends(get_app_db_session),
):
    return await get_audit_tasks(
        session=session,
        page=page,
        page_size=page_size,
        search=search,
        sigla=sigla,
        situation=situation,
        prazo=prazo,
        unassigned=unassigned,
        is_active=is_active,
    )


@router.get(
    "/audit-tasks/dashboard",
    summary="Métricas e Analytics do Dashboard",
    description="Retorna KPIs consolidados, distribuição por situação, semáforos de prazo e histórico mensal (RNA).",
)
async def dashboard_metrics(
    sigla: Optional[str] = Query(None, description="Filtrar métricas por Gerência ou omitir para Quadro Geral"),
    session: AsyncSession = Depends(get_app_db_session),
):
    return await get_dashboard_metrics(session, sigla)
