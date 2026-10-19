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

    # 2. Testar listagem de Áreas do Organograma Oficial (mais de 50 setores cadastrados)
    res_areas = client.get("/api/responsible-areas?sigla=SUP")
    assert res_areas.status_code == 200
    areas_sup = res_areas.json()
    assert len(areas_sup) > 0
    primeira_area_id = areas_sup[0]["id"]

    res_all_areas = client.get("/api/responsible-areas")
    assert res_all_areas.status_code == 200
    assert len(res_all_areas.json()) >= 50

    # 3. Testar restrição de importação a Administradores
    excel_bytes = create_sample_excel()
    files = {"file": ("ecgu_teste.xlsx", excel_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    
    # Tentativa anônima deve ser negada
    res_unauth = client.post("/api/audit-tasks/import", files=files)
    assert res_unauth.status_code in (401, 403)

    # Login como administrador tassio.silva
    res_login = client.post(
        "/api/login",
        data={"username": "tassio.silva", "password": "admin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # Upload com token de administrador deve ter sucesso
    res_upload = client.post("/api/audit-tasks/import", files=files, headers=admin_headers)
    assert res_upload.status_code == 200
    upload_data = res_upload.json()["data"]
    assert upload_data["total_rows"] == 2
    assert upload_data["active_rows"] == 2

    # 4. Testar listagem de tarefas com filtro múltiplo de situações
    res_tasks = client.get("/api/audit-tasks?situation=Não atendida,Parcialmente Atendida")
    assert res_tasks.status_code == 200
    tasks_data = res_tasks.json()
    assert tasks_data["total"] >= 1
    for item in tasks_data["items"]:
        assert item["situation"] in ("Não atendida", "Parcialmente Atendida")

    # 5. Testar atribuição de Área Responsável
    task_items = client.get("/api/audit-tasks?sigla=SUP").json()["items"]
    target_task = next(t for t in task_items if t["task_id"] == "1706209")
    res_assign = client.patch(
        f"/api/audit-tasks/{target_task['task_id']}/responsible-area",
        json={"responsible_area_id": primeira_area_id}
    )
    assert res_assign.status_code == 200

    # 6. Testar endpoint de Dashboard e Série Temporal RNA
    res_dash = client.get("/api/audit-tasks/dashboard")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "kpis" in dash_data
    assert "situacao" in dash_data
    assert "prazo" in dash_data
    assert "por_ano" in dash_data
    assert "rna_historico" in dash_data
    assert len(dash_data["rna_historico"]) >= 15
    # Último ponto da série temporal deve ser o mês corrente
    last_point = dash_data["rna_historico"][-1]
    assert last_point["is_current"] is True
    assert last_point["quantidade"] == dash_data["kpis"]["total_pendentes"]
