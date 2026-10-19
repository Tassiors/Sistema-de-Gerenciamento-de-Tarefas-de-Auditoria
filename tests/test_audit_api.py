import pytest
from datetime import date
import io
import openpyxl


def create_sample_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append([
        "Id da Tarefa", "Estado", "Título da Tarefa", "Data de Início",
        "Data de Fim", "Data Limite", "Unidade Auditada", "Texto do Monitoramento", "Providência"
    ])
    ws.append([
        "1706209", "Em Análise pela Unidade Auditada", "Solicitar comissão", "01/05/2024",
        None, "30/10/2026", "SUP - Superintendência", "Monitoramento A", "Recomendação implementada parcialmente"
    ])
    ws.append([
        "1706212", "Concluída", "Plano de ação", "01/05/2024",
        "15/06/2024", "18/12/2026", "SUP - Superintendência", "Monitoramento B", "Recomendação implementada"
    ])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_audit_api_workflow(client):
    # 1. Testar listagem de Governança
    res_gov = client.get("/api/governance-units")
    assert res_gov.status_code == 200
    units = res_gov.json()
    siglas = [u["sigla"] for u in units]
    assert "SUP" in siglas
    assert "GAD" in siglas
    assert "GAS" in siglas
    assert "GEP" in siglas

    # 2. Testar listagem de Áreas
    res_areas = client.get("/api/responsible-areas?sigla=SUP")
    assert res_areas.status_code == 200
    areas_sup = res_areas.json()
    assert len(areas_sup) > 0
    primeira_area_id = areas_sup[0]["id"]

    # 3. Testar upload de planilha e-CGU
    excel_bytes = create_sample_excel()
    files = {"file": ("ecgu_teste.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res_upload = client.post("/api/audit-tasks/import", files=files)
    assert res_upload.status_code == 200
    upload_data = res_upload.json()["data"]
    assert upload_data["total_rows"] == 2
    assert upload_data["active_rows"] == 2

    # 4. Testar listagem de tarefas
    res_tasks = client.get("/api/audit-tasks?sigla=SUP")
    assert res_tasks.status_code == 200
    tasks_data = res_tasks.json()
    assert tasks_data["total"] >= 2
    task_items = tasks_data["items"]
    target_task = next(t for t in task_items if t["task_id"] == "1706209")
    assert target_task["situation"] == "Parcialmente Atendida"
    assert target_task["governance_sigla"] == "SUP"
    assert target_task["prazo_status"] in ("Prazo Amplo", "Prazo Encerrando", "Prazo Venceu")

    # 5. Testar atribuição de Área Responsável
    res_assign = client.patch(
        f"/api/audit-tasks/{target_task['task_id']}/responsible-area",
        json={"responsible_area_id": primeira_area_id}
    )
    assert res_assign.status_code == 200

    # Verificar se foi atualizada
    res_check = client.get(f"/api/audit-tasks?search={target_task['task_id']}")
    assert res_check.status_code == 200
    updated_item = res_check.json()["items"][0]
    assert updated_item["responsible_area_id"] == primeira_area_id

    # 6. Testar endpoint de Dashboard
    res_dash = client.get("/api/audit-tasks/dashboard?sigla=SUP")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "kpis" in dash_data
    assert "situacao" in dash_data
    assert "prazo" in dash_data
    assert "por_ano" in dash_data
    assert "rna_historico" in dash_data
