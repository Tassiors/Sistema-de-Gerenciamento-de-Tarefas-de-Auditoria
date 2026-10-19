"""
Rotas REST da API: Gestão de Tarefas de Auditoria e Governança
==============================================================
Disponibiliza endpoints para importação de planilhas do e-CGU,
atribuição de áreas responsáveis, listagem operacional, detalhes de tarefa e métricas analíticas.
"""

from typing import Optional, Set, List
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from ..resources.database import get_app_db_session
from ..auth.auth import require_admin, auth_handler
from ..models import AuditTask
from ..services.visibility_service import get_user_visible_area_ids
from ..services.audit_service import (
    import_ecgu_spreadsheet,
    list_governance_units,
    list_responsible_areas,
    assign_responsible_area,
    assign_responsible_areas,
    get_audit_tasks,
    get_dashboard_metrics,
    calculate_prazo_status,
)

router = APIRouter(prefix="/api", tags=["Tarefas de Auditoria e Governança"])

security_optional = HTTPBearer(auto_error=False)


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)):
    if not credentials:
        return None
    try:
        payload = auth_handler.decode_token(credentials.credentials)
        return payload
    except Exception:
        return None


class AreaAssignmentPayload(BaseModel):
    responsible_area_id: Optional[int] = None


class MultipleAreasAssignmentPayload(BaseModel):
    responsible_area_ids: List[int] = []


@router.post(
    "/audit-tasks/import",
    summary="Importar Planilha do e-CGU",
    description="Faz upload da planilha oficial do e-CGU (.xlsx), processa tarefas incrementalmente e atualiza a base.",
)
async def import_audit_tasks(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin),
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
    "/audit-tasks/{task_id}/responsible-areas",
    summary="Atribuir Múltiplas Áreas Responsáveis à Tarefa",
    description="Permite vincular uma ou mais divisões/setores encarregados pela tarefa de auditoria.",
)
async def set_task_areas(
    task_id: str,
    payload: MultipleAreasAssignmentPayload,
    session: AsyncSession = Depends(get_app_db_session),
):
    try:
        res = await assign_responsible_areas(session, task_id, payload.responsible_area_ids)
        return {
            "message": "Áreas Responsáveis atualizadas com sucesso",
            "data": res,
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


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
    description="Consulta paginada com busca textual, visibilidade hierárquica por gestor e filtros dinâmicos por gerência, situação, prazo e tarefas sem área.",
)
async def list_tasks(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=500, description="Tamanho da página"),
    search: Optional[str] = Query(None, description="Busca textual por ID, Título ou Monitoramento"),
    sigla: Optional[str] = Query(None, description="Filtrar por sigla da Gerência (SUP, GAD, GAS, GEP)"),
    situation: Optional[str] = Query(None, description="Filtrar por Situação (Não atendida, Parcialmente Atendida, Concluída)"),
    prazo: Optional[str] = Query(None, description="Filtrar por Semáforo de Prazo"),
    unassigned: Optional[bool] = Query(None, description="Filtrar tarefas pendentes sem Área Responsável"),
    is_active: bool = Query(True, description="Listar apenas tarefas ativas"),
    current_user: Optional[dict] = Depends(get_optional_user),
    session: AsyncSession = Depends(get_app_db_session),
):
    visible_area_ids = None
    if current_user and current_user.get("username"):
        visible_area_ids = await get_user_visible_area_ids(session, current_user["username"])

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
        visible_area_ids=visible_area_ids,
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


@router.get(
    "/audit-tasks/{task_id}",
    summary="Detalhes Completos da Tarefa de Auditoria",
    description="Retorna todas as informações da tarefa: descrição completa, monitoramento, providência adotada, datas e área responsável.",
)
async def get_task_detail(
    task_id: str,
    session: AsyncSession = Depends(get_app_db_session),
):
    stmt = (
        select(AuditTask)
        .options(
            selectinload(AuditTask.governance_unit),
            selectinload(AuditTask.responsible_area),
            selectinload(AuditTask.responsible_areas),
        )
        .where(or_(AuditTask.task_id == task_id, AuditTask.id == (int(task_id) if task_id.isdigit() else -1)))
    )
    res = await session.execute(stmt)
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tarefa '{task_id}' não encontrada.")

    today = date.today()
    p_status, dias = calculate_prazo_status(t.deadline, today)

    areas_list = [
        {"id": a.id, "nome": a.nome, "sigla": a.sigla, "level": a.level}
        for a in t.responsible_areas
    ]
    if not areas_list and t.responsible_area:
        areas_list = [{
            "id": t.responsible_area.id,
            "nome": t.responsible_area.nome,
            "sigla": t.responsible_area.sigla,
            "level": t.responsible_area.level,
        }]

    siglas_str = ", ".join(filter(None, [a["sigla"] for a in areas_list])) or None
    nomes_str = ", ".join([a["nome"] for a in areas_list]) if areas_list else None

    return {
        "id": t.id,
        "task_id": t.task_id,
        "title": t.title,
        "state": t.state,
        "start_date": t.start_date.isoformat() if t.start_date else None,
        "start_year": t.start_date.year if t.start_date else None,
        "end_date": t.end_date.isoformat() if t.end_date else None,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "dias_restantes": dias,
        "prazo_status": p_status,
        "situation": t.situation,
        "monitoring_text": t.monitoring_text,
        "action_taken": t.action_taken,
        "governance_sigla": t.governance_unit.sigla if t.governance_unit else None,
        "governance_nome": t.governance_unit.nome if t.governance_unit else None,
        "responsible_area_id": t.responsible_area_id or (areas_list[0]["id"] if areas_list else None),
        "responsible_area_nome": nomes_str,
        "responsible_area_sigla": siglas_str,
        "responsible_area_level": t.responsible_area.level if t.responsible_area else (areas_list[0]["level"] if areas_list else None),
        "responsible_areas": areas_list,
    }
