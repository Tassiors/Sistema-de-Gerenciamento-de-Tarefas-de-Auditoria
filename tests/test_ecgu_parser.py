import pytest
from datetime import date
from src.services.ecgu_parser import map_situation, parse_date, parse_ecgu_workbook
import openpyxl
import io


def test_map_situation():
    assert map_situation("Recomendação implementada") == "Concluída"
    assert map_situation("Recomendação implementada parcialmente") == "Parcialmente Atendida"
    assert map_situation("Não houve providência") == "Não atendida"
    assert map_situation("Recomendação não implementada: Ação inadequada ou insuficiente") == "Não atendida"
    assert map_situation(None) == "Não atendida"
    assert map_situation("") == "Não atendida"


def test_parse_date():
    assert parse_date("2026-10-30") == date(2026, 10, 30)
    assert parse_date("30/10/2026") == date(2026, 10, 30)
    assert parse_date(None) is None


def test_parse_ecgu_workbook_synthetic():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        "Id da Tarefa", "Estado", "Título da Tarefa", "Data de Início",
        "Data de Fim", "Data Limite", "Unidade Auditada", "Texto do Monitoramento", "Providência"
    ])
    # 1. Tarefa ativa pendente
    ws.append([
        1001, "Em Análise pela Unidade Auditada", "Tarefa 1", "01/05/2024",
        None, "30/10/2026", "SUP - Superintendência", "Monitoramento 1", "Recomendação implementada parcialmente"
    ])
    # 2. Tarefa ativa concluída
    ws.append([
        1002, "Concluída", "Tarefa 2", "01/05/2024",
        "15/06/2024", "30/06/2024", "GAD - Adm", "Monitoramento 2", "Recomendação implementada"
    ])
    # 3. Tarefa antiga filtrada por data
    ws.append([
        1003, "Concluída", "Tarefa Antiga", "01/01/2023",
        "10/01/2024", "15/01/2024", "GAS - Saúde", "Monitoramento 3", "Recomendação implementada"
    ])
    # 4. Tarefa cancelada
    ws.append([
        1004, "Cancelada", "Tarefa Cancelada", "01/05/2024",
        None, "30/10/2026", "GEP - Pesquisa", "Monitoramento 4", "Não houve providência"
    ])

    buf = io.BytesIO()
    wb.save(buf)
    data = buf.getvalue()

    tasks, stats = parse_ecgu_workbook(data)
    assert stats["total_rows"] == 4
    assert stats["active_rows"] == 2
    assert stats["filtered_out_date"] == 1
    assert stats["cancelled_rows"] == 1

    active_tasks = [t for t in tasks if t["is_active"]]
    assert len(active_tasks) == 2
    assert active_tasks[0]["situation"] == "Parcialmente Atendida"
    assert active_tasks[0]["sigla"] == "SUP"
    assert active_tasks[1]["situation"] == "Concluída"
    assert active_tasks[1]["sigla"] == "GAD"
