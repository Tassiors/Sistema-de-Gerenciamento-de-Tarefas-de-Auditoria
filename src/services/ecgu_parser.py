"""
Serviço de Processamento e Ingestão de Planilhas do e-CGU
=========================================================
Responsável pela leitura de arquivos .xlsx exportados do sistema da CGU,
validação de schema, normalização de tipos e aplicação das regras de negócio
equivalentes às etapas M do Power Query.
"""

import io
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
import openpyxl

CUT_OFF_DATE = date(2024, 4, 30)

REQUIRED_COLUMNS = [
    "Id da Tarefa",
    "Estado",
    "Título da Tarefa",
    "Data de Início",
    "Data de Fim",
    "Data Limite",
    "Unidade Auditada",
    "Texto do Monitoramento",
    "Providência",
]


def parse_date(value: Any) -> Optional[date]:
    """Converte valores variados de data (datetime, string, serial) em date."""
    if value is None or value == "" or str(value).lower() in ("nan", "none", "null"):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    val_str = str(value).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val_str, fmt).date()
        except ValueError:
            continue
    return None


def map_situation(action_taken: Optional[str]) -> str:
    """
    Aplica a regra da coluna calculada DAX 'Situação':
    - Não atendida (vazio, 'Não houve providência', 'Ação inadequada ou insuficiente')
    - Parcialmente Atendida ('Recomendação implementada parcialmente')
    - Concluída ('Recomendação implementada')
    """
    if not action_taken or str(action_taken).strip() == "" or str(action_taken).lower() in ("nan", "none"):
        return "Não atendida"
    clean = str(action_taken).strip()
    if clean in ("Não houve providência", "Recomendação não implementada: Ação inadequada ou insuficiente"):
        return "Não atendida"
    if clean == "Recomendação implementada":
        return "Concluída"
    if clean == "Recomendação implementada parcialmente":
        return "Parcialmente Atendida"
    return clean


def parse_ecgu_workbook(file_bytes: bytes) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Lê o workbook Excel (.xlsx) e extrai a lista de tarefas tratadas.
    Retorna (tarefas_validas, estatisticas_parse).
    """
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    sheet = wb.active

    headers = [str(cell.value).strip() if cell.value is not None else "" for cell in sheet[1]]
    
    # Validar cabeçalhos obrigatórios
    missing = [col for col in REQUIRED_COLUMNS if col not in headers]
    if missing:
        raise ValueError(f"Planilha inválida. Colunas obrigatórias ausentes: {', '.join(missing)}")

    col_idx = {name: headers.index(name) for name in REQUIRED_COLUMNS}

    tasks = []
    stats = {
        "total_rows": 0,
        "active_rows": 0,
        "filtered_out_date": 0,
        "cancelled_rows": 0,
    }

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue

        raw_id = row[col_idx["Id da Tarefa"]]
        if raw_id is None or str(raw_id).strip() == "":
            continue

        stats["total_rows"] += 1
        task_id = str(int(raw_id)) if isinstance(raw_id, (int, float)) else str(raw_id).strip()
        state = str(row[col_idx["Estado"]]).strip() if row[col_idx["Estado"]] else ""
        title = str(row[col_idx["Título da Tarefa"]]).strip() if row[col_idx["Título da Tarefa"]] else ""
        
        start_date = parse_date(row[col_idx["Data de Início"]])
        end_date = parse_date(row[col_idx["Data de Fim"]])
        deadline = parse_date(row[col_idx["Data Limite"]])

        audited_unit_raw = str(row[col_idx["Unidade Auditada"]]).strip() if row[col_idx["Unidade Auditada"]] else ""
        sigla = audited_unit_raw[:3].upper() if len(audited_unit_raw) >= 3 else audited_unit_raw.upper()
        # Mapear para uma das 4 gerências conhecidas se aplicável
        if sigla not in ("SUP", "GAD", "GAS", "GEP"):
            sigla = None

        monitoring_text = str(row[col_idx["Texto do Monitoramento"]]).strip() if row[col_idx["Texto do Monitoramento"]] else None
        action_taken = str(row[col_idx["Providência"]]).strip() if row[col_idx["Providência"]] else None
        situation = map_situation(action_taken)

        # Regra de negócio: data de fim > 30/04/2024 ou nula
        passes_date = (end_date is None) or (end_date > CUT_OFF_DATE)
        is_cancelled = (state.lower() == "cancelada")
        is_active = passes_date and (not is_cancelled)

        if not passes_date:
            stats["filtered_out_date"] += 1
        if is_cancelled:
            stats["cancelled_rows"] += 1
        if is_active:
            stats["active_rows"] += 1

        tasks.append({
            "task_id": task_id,
            "title": title,
            "state": state,
            "start_date": start_date,
            "end_date": end_date,
            "deadline": deadline,
            "audited_unit_raw": audited_unit_raw,
            "sigla": sigla,
            "monitoring_text": monitoring_text,
            "action_taken": action_taken,
            "situation": situation,
            "is_active": is_active,
        })

    return tasks, stats
