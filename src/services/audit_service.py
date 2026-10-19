"""
Serviço Central de Negócio: Gestão, Analytics e Auditoria
==========================================================
Concentra operações de banco de dados para tarefas de auditoria,
governança, cálculo dinâmico de semáforos de prazos e métricas de dashboard.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.orm import selectinload

from ..models import AuditTask, GovernanceUnit, ResponsibleArea, ImportBatch, RnaMonthlySnapshot
from .ecgu_parser import parse_ecgu_workbook

# Série histórica oficial de Recomendações Não Atendidas (RNA)
RNA_HISTORICAL_DATA = [
    {"mes": "2024-05-01", "label": "maio de 2024", "quantidade": 111},
    {"mes": "2024-09-01", "label": "setembro de 2024", "quantidade": 132},
    {"mes": "2024-11-01", "label": "novembro de 2024", "quantidade": 114},
    {"mes": "2025-03-01", "label": "março de 2025", "quantidade": 88},
    {"mes": "2025-05-01", "label": "maio de 2025", "quantidade": 73},
    {"mes": "2025-08-01", "label": "agosto de 2025", "quantidade": 79},
    {"mes": "2025-11-01", "label": "novembro de 2025", "quantidade": 60},
    {"mes": "2026-02-01", "label": "fevereiro de 2026", "quantidade": 64},
    {"mes": "2026-03-01", "label": "março de 2026", "quantidade": 46},
    {"mes": "2026-04-01", "label": "abril de 2026", "quantidade": 31},
    {"mes": "2026-05-01", "label": "maio de 2026", "quantidade": 28},
    {"mes": "2026-06-01", "label": "junho de 2026", "quantidade": 26},
    {"mes": "2026-07-01", "label": "julho de 2026", "quantidade": 26},
    {"mes": "2026-08-01", "label": "agosto de 2026", "quantidade": 26},
    {"mes": "2026-09-01", "label": "setembro de 2026", "quantidade": 34},
    {"mes": "2026-10-01", "label": "outubro de 2026", "quantidade": 49},
]


def calculate_prazo_status(deadline: Optional[date], today: Optional[date] = None) -> Tuple[str, Optional[int]]:
    """Calcula dinamicamente a classificação do prazo e os dias restantes."""
    if today is None:
        today = date.today()
    if not deadline:
        return "Sem Prazo", None
    
    dias = (deadline - today).days
    if dias <= 0:
        return "Prazo Venceu", dias
    if dias <= 20:
        return "Prazo Encerrando", dias
    return "Prazo Amplo", dias


async def import_ecgu_spreadsheet(
    session: AsyncSession,
    file_bytes: bytes,
    filename: str,
    imported_by: Optional[str] = "Administrador",
) -> Dict[str, Any]:
    """Processa upload da planilha e-CGU e persiste tarefas incrementalmente."""
    parsed_tasks, stats = parse_ecgu_workbook(file_bytes)

    # 1. Criar lote de importação
    batch = ImportBatch(
        filename=filename,
        total_rows=stats["total_rows"],
        imported_by=imported_by,
    )
    session.add(batch)
    await session.flush()

    # 2. Carregar gerências existentes para mapeamento
    gov_res = await session.execute(select(GovernanceUnit))
    gov_map = {g.sigla: g.id for g in gov_res.scalars().all()}

    # 3. Carregar tarefas já existentes no banco
    existing_res = await session.execute(select(AuditTask))
    existing_tasks = {t.task_id: t for t in existing_res.scalars().all()}

    inserted_count = 0
    updated_count = 0

    for t_data in parsed_tasks:
        tid = t_data["task_id"]
        gov_id = gov_map.get(t_data["sigla"]) if t_data["sigla"] else None

        if tid in existing_tasks:
            # Atualização incremental preservando Área Responsável previamente definida
            task = existing_tasks[tid]
            task.title = t_data["title"]
            task.state = t_data["state"]
            task.start_date = t_data["start_date"]
            task.end_date = t_data["end_date"]
            task.deadline = t_data["deadline"]
            task.audited_unit_raw = t_data["audited_unit_raw"]
            task.monitoring_text = t_data["monitoring_text"]
            task.action_taken = t_data["action_taken"]
            task.situation = t_data["situation"]
            task.is_active = t_data["is_active"]
            task.import_batch_id = batch.id
            if gov_id and not task.governance_unit_id:
                task.governance_unit_id = gov_id
            updated_count += 1
        else:
            task = AuditTask(
                task_id=tid,
                title=t_data["title"],
                state=t_data["state"],
                start_date=t_data["start_date"],
                end_date=t_data["end_date"],
                deadline=t_data["deadline"],
                audited_unit_raw=t_data["audited_unit_raw"],
                monitoring_text=t_data["monitoring_text"],
                action_taken=t_data["action_taken"],
                situation=t_data["situation"],
                is_active=t_data["is_active"],
                governance_unit_id=gov_id,
                import_batch_id=batch.id,
            )
            session.add(task)
            inserted_count += 1

    batch.inserted_count = inserted_count
    batch.updated_count = updated_count
    batch.ignored_count = stats["total_rows"] - stats["active_rows"]
    await session.commit()

    return {
        "batch_id": batch.id,
        "filename": filename,
        "total_rows": stats["total_rows"],
        "active_rows": stats["active_rows"],
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "ignored_count": batch.ignored_count,
    }


async def list_governance_units(session: AsyncSession) -> List[Dict[str, Any]]:
    """Retorna todas as gerências com suas respectivas áreas."""
    stmt = select(GovernanceUnit).options(selectinload(GovernanceUnit.responsible_areas)).order_by(GovernanceUnit.sigla)
    res = await session.execute(stmt)
    units = res.scalars().all()
    return [
        {
            "id": u.id,
            "sigla": u.sigla,
            "nome": u.nome,
            "areas": [{"id": a.id, "nome": a.nome} for a in u.responsible_areas]
        }
        for u in units
    ]


async def list_responsible_areas(
    session: AsyncSession,
    governance_unit_id: Optional[int] = None,
    sigla: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lista áreas responsáveis com filtro opcional por gerência."""
    stmt = select(ResponsibleArea).options(selectinload(ResponsibleArea.governance_unit))
    if governance_unit_id:
        stmt = stmt.where(ResponsibleArea.governance_unit_id == governance_unit_id)
    if sigla:
        stmt = stmt.join(ResponsibleArea.governance_unit).where(GovernanceUnit.sigla == sigla.upper())
    
    stmt = stmt.order_by(ResponsibleArea.nome)
    res = await session.execute(stmt)
    areas = res.scalars().all()
    return [
        {
            "id": a.id,
            "nome": a.nome,
            "governance_unit_id": a.governance_unit_id,
            "governance_sigla": a.governance_unit.sigla if a.governance_unit else None,
            "governance_nome": a.governance_unit.nome if a.governance_unit else None,
        }
        for a in areas
    ]


async def assign_responsible_area(
    session: AsyncSession,
    task_id: str,
    responsible_area_id: Optional[int],
) -> Dict[str, Any]:
    """Atribui ou altera a Área Responsável de uma tarefa de auditoria."""
    stmt = select(AuditTask).where(AuditTask.task_id == task_id)
    res = await session.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise ValueError(f"Tarefa de auditoria {task_id} não encontrada.")

    task.responsible_area_id = responsible_area_id
    if responsible_area_id:
        area_res = await session.execute(select(ResponsibleArea).where(ResponsibleArea.id == responsible_area_id))
        area = area_res.scalar_one_or_none()
        if area:
            task.governance_unit_id = area.governance_unit_id

    await session.commit()
    await session.refresh(task)
    return {
        "task_id": task.task_id,
        "responsible_area_id": task.responsible_area_id,
        "governance_unit_id": task.governance_unit_id,
    }


async def get_audit_tasks(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    sigla: Optional[str] = None,
    situation: Optional[str] = None,
    prazo: Optional[str] = None,
    unassigned: Optional[bool] = None,
    is_active: bool = True,
    visible_area_ids: Optional[Set[int]] = None,
) -> Dict[str, Any]:
    """Retorna listagem filtrada e paginada de tarefas com cálculo dinâmico de semáforos e controle de visibilidade."""
    stmt = select(AuditTask).options(
        selectinload(AuditTask.governance_unit),
        selectinload(AuditTask.responsible_area),
    ).where(AuditTask.is_active == is_active)

    # Controle de visibilidade hierárquica por gestor (None = irrestrito / admin / super / auditor)
    if visible_area_ids is not None:
        stmt = stmt.where(AuditTask.responsible_area_id.in_(list(visible_area_ids)))

    if sigla:
        stmt = stmt.join(AuditTask.governance_unit).where(GovernanceUnit.sigla == sigla.upper())

    # Filtro de Situações (Lógica OR múltipla escolha com mapeamento Concluída/Atendida)
    if situation:
        if isinstance(situation, str):
            raw_situations = [s.strip() for s in situation.split(",") if s.strip()]
        else:
            raw_situations = list(situation)
        
        mapped_situations = set()
        for s in raw_situations:
            if s.lower() in ("concluída", "concluida", "atendida"):
                mapped_situations.add("Concluída")
                mapped_situations.add("Atendida")
            else:
                mapped_situations.add(s)
        
        if mapped_situations:
            stmt = stmt.where(
                or_(
                    AuditTask.situation.in_(list(mapped_situations)),
                    AuditTask.state.in_(list(mapped_situations))
                )
            )

    if unassigned is True:
        stmt = stmt.where(AuditTask.responsible_area_id.is_(None))

    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                AuditTask.task_id.ilike(term),
                AuditTask.title.ilike(term),
                AuditTask.monitoring_text.ilike(term),
            )
        )

    # Executar busca para contagem e ordenação
    res = await session.execute(stmt.order_by(AuditTask.deadline.asc().nulls_last()))
    all_matched = res.scalars().all()

    # Filtro de Prazos (Lógica OR múltipla escolha)
    prazo_list = []
    if prazo:
        if isinstance(prazo, str):
            prazo_list = [p.strip() for p in prazo.split(",") if p.strip()]
        else:
            prazo_list = list(prazo)

    today = date.today()
    items = []
    for t in all_matched:
        p_status, dias = calculate_prazo_status(t.deadline, today)
        if prazo_list and p_status not in prazo_list:
            continue

        items.append({
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
            "responsible_area_id": t.responsible_area_id,
            "responsible_area_nome": t.responsible_area.nome if t.responsible_area else None,
            "responsible_area_sigla": t.responsible_area.sigla if t.responsible_area else None,
            "responsible_area_level": t.responsible_area.level if t.responsible_area else None,
        })

    total = len(items)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = items[start_idx:end_idx]

    return {
        "items": paginated,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1,
    }


async def get_dashboard_metrics(
    session: AsyncSession,
    sigla: Optional[str] = None,
) -> Dict[str, Any]:
    """Gera métricas agregadas do Dashboard (Quadro Geral ou por Gerência)."""
    stmt = select(AuditTask).options(selectinload(AuditTask.governance_unit)).where(AuditTask.is_active == True)

    if sigla:
        stmt = stmt.join(AuditTask.governance_unit).where(GovernanceUnit.sigla == sigla.upper())

    res = await session.execute(stmt)
    tasks = res.scalars().all()

    today = date.today()
    pendentes_count = 0
    atendidas_count = 0
    unassigned_count = 0

    situacao_dist = {"Não atendida": 0, "Parcialmente Atendida": 0}
    prazo_dist = {"Prazo Amplo": 0, "Prazo Encerrando": 0, "Prazo Venceu": 0}
    ano_dist = {}

    for t in tasks:
        if t.state == "Concluída":
            atendidas_count += 1
        elif t.state == "Em Análise pela Unidade Auditada":
            pendentes_count += 1
            if not t.responsible_area_id:
                unassigned_count += 1

            # Situação
            sit = t.situation or "Não atendida"
            situacao_dist[sit] = situacao_dist.get(sit, 0) + 1

            # Prazo
            p_status, _ = calculate_prazo_status(t.deadline, today)
            prazo_dist[p_status] = prazo_dist.get(p_status, 0) + 1

            # Ano de início
            ano = t.start_date.year if t.start_date else "Sem Ano"
            ano_dist[str(ano)] = ano_dist.get(str(ano), 0) + 1

    # Série temporal de Recomendações Não Atendidas (RNA a partir de MAIO/24)
    # Regra: Total do dia atual para o mês corrente; ao transicionar de mês,
    # o total do mês anterior é congelado com o total no seu último dia.
    snap_stmt = select(RnaMonthlySnapshot).order_by(RnaMonthlySnapshot.year_month.asc())
    snap_res = await session.execute(snap_stmt)
    snapshots = list(snap_res.scalars().all())

    current_ym = f"{today.year}-{today.month:02d}"
    month_labels = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Maio", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    current_label = f"{month_labels.get(today.month, str(today.month))}/{str(today.year)[2:]}"

    # Congelar meses anteriores que ainda não estavam fechados
    for s in snapshots:
        if s.year_month < current_ym and not s.is_closed:
            s.is_closed = True

    # Atualizar ou inserir snapshot do mês corrente com total do dia atual
    current_snap = next((s for s in snapshots if s.year_month == current_ym), None)
    if not sigla:
        if current_snap:
            current_snap.count_rna = pendentes_count
            current_snap.snapshot_date = today
            current_snap.is_closed = False
        else:
            current_snap = RnaMonthlySnapshot(
                year_month=current_ym,
                label=current_label,
                count_rna=pendentes_count,
                snapshot_date=today,
                is_closed=False
            )
            session.add(current_snap)
            snapshots.append(current_snap)
        await session.commit()

    # Formatar série histórica para exibição
    rna_series = []
    for s in snapshots:
        val = s.count_rna
        if sigla and s.year_month == current_ym:
            val = pendentes_count

        rna_series.append({
            "mes": f"{s.year_month}-01",
            "label": s.label,
            "quantidade": val,
            "is_current": (s.year_month == current_ym),
        })

    return {
        "filter": sigla.upper() if sigla else "GERAL",
        "kpis": {
            "total_pendentes": pendentes_count,
            "total_atendidas": atendidas_count,
            "total_ativas": pendentes_count + atendidas_count,
            "pendentes_sem_area": unassigned_count,
        },
        "situacao": [
            {"situacao": k, "quantidade": v} for k, v in situacao_dist.items()
        ],
        "prazo": [
            {"status": k, "quantidade": v} for k, v in prazo_dist.items()
        ],
        "por_ano": [
            {"ano": k, "quantidade": v} for k, v in sorted(ano_dist.items())
        ],
        "rna_historico": rna_series,
    }
