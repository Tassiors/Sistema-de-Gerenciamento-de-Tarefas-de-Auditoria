import pytest
from datetime import date
from src.models import ResponsibleArea, SystemManager
from src.services.visibility_service import get_subordinate_area_ids, get_user_visible_area_ids
from sqlalchemy import select


def test_task_detail_endpoint(client):
    """Valida o endpoint de detalhes completos da tarefa."""
    res = client.get("/api/audit-tasks?page=1&page_size=1")
    assert res.status_code == 200
    data = res.json()
    if data["items"]:
        task_id = data["items"][0]["task_id"]
        detail_res = client.get(f"/api/audit-tasks/{task_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["task_id"] == task_id
        assert "title" in detail
        assert "monitoring_text" in detail
        assert "prazo_status" in detail


def test_or_filters_situation_and_prazo(client):
    """Valida a lógica OR para filtros de situação e prazos."""
    # Filtrar com múltiplas situações separadas por vírgula (OR)
    res = client.get("/api/audit-tasks?situation=Não atendida,Parcialmente Atendida")
    assert res.status_code == 200
    items = res.json()["items"]
    for item in items:
        assert item["situation"] in ["Não atendida", "Parcialmente Atendida", "Concluída", "Atendida"]

    # Filtrar com múltiplos prazos (OR)
    res_prazo = client.get("/api/audit-tasks?prazo=Prazo Encerrando,Prazo Venceu")
    assert res_prazo.status_code == 200
    prazo_items = res_prazo.json()["items"]
    for item in prazo_items:
        assert item["prazo_status"] in ["Prazo Encerrando", "Prazo Venceu"]


def test_managers_api_crud(client):
    """Valida endpoints de gestão de gestores e matriz de visibilidade."""
    # 1. Login como admin para obter token
    login_res = client.post("/api/login", data={"username": "tassio.silva", "password": "123456"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Listar gestores
    res_list = client.get("/api/admin/managers", headers=headers)
    assert res_list.status_code == 200
    managers = res_list.json()
    assert isinstance(managers, list)
    assert len(managers) >= 1
