"""
Serviço de Visibilidade e Hierarquia Organizacional
===================================================
Controla a matriz de visibilidade por organograma (Gerência -> Divisão -> Setor -> Unidade)
e a gestão de gestores pré-cadastrados.
"""

from typing import Optional, Set, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from ..models import ResponsibleArea, SystemManager, ManagerExtraUnit, GovernanceUnit

UNRESTRICTED_ROLES = {"ADMINISTRADOR", "SUPERINTENDENTE", "AUDITOR"}
ADMIN_USERS = {"tassio.silva", "renata.albuquerque.1", "admin"}


async def get_subordinate_area_ids(session: AsyncSession, area_id: int) -> Set[int]:
    """Recupera recursivamente todos os IDs de áreas subordinadas à área informada."""
    if not area_id:
        return set()

    res = await session.execute(select(ResponsibleArea.id, ResponsibleArea.parent_id))
    all_areas = res.all()

    # Mapeamento pai -> filhos
    parent_map: Dict[int, List[int]] = {}
    for aid, pid in all_areas:
        if pid:
            parent_map.setdefault(pid, []).append(aid)

    subordinates = {area_id}
    queue = [area_id]

    while queue:
        curr = queue.pop(0)
        children = parent_map.get(curr, [])
        for ch in children:
            if ch not in subordinates:
                subordinates.add(ch)
                queue.append(ch)

    return subordinates


async def get_user_visible_area_ids(session: AsyncSession, username: Optional[str]) -> Optional[Set[int]]:
    """Retorna o conjunto de IDs de áreas visíveis para o usuário.
    Retorna None caso o usuário possua visibilidade global (Admin, Superintendente ou Auditor).
    """
    if not username:
        return set()

    clean_user = username.strip().lower()
    if clean_user in ADMIN_USERS:
        return None

    stmt = select(SystemManager).options(
        selectinload(SystemManager.extra_units)
    ).where(SystemManager.username == clean_user, SystemManager.is_active == True)
    
    res = await session.execute(stmt)
    manager = res.scalar_one_or_none()

    if not manager:
        return set()

    if manager.role in UNRESTRICTED_ROLES:
        return None

    visible = set()
    if manager.responsible_area_id:
        sub = await get_subordinate_area_ids(session, manager.responsible_area_id)
        visible.update(sub)

    for extra in manager.extra_units:
        visible.add(extra.responsible_area_id)

    return visible


async def list_managers(session: AsyncSession) -> List[Dict[str, Any]]:
    """Lista todos os gestores cadastrados com sua unidade principal e unidades extras."""
    stmt = select(SystemManager).options(
        selectinload(SystemManager.responsible_area),
        selectinload(SystemManager.extra_units).selectinload(ManagerExtraUnit.responsible_area),
    ).order_by(SystemManager.name)

    res = await session.execute(stmt)
    managers = res.scalars().all()

    out = []
    for m in managers:
        subordinates_count = 0
        if m.responsible_area_id:
            subs = await get_subordinate_area_ids(session, m.responsible_area_id)
            subordinates_count = len(subs)

        out.append({
            "id": m.id,
            "username": m.username,
            "name": m.name,
            "email": m.email,
            "role": m.role,
            "is_active": m.is_active,
            "responsible_area_id": m.responsible_area_id,
            "responsible_area_nome": m.responsible_area.nome if m.responsible_area else None,
            "responsible_area_sigla": m.responsible_area.sigla if m.responsible_area else None,
            "responsible_area_level": m.responsible_area.level if m.responsible_area else None,
            "subordinates_count": subordinates_count,
            "extra_units": [
                {
                    "id": ex.responsible_area.id,
                    "nome": ex.responsible_area.nome,
                    "sigla": ex.responsible_area.sigla,
                }
                for ex in m.extra_units if ex.responsible_area
            ],
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return out


async def create_manager(session: AsyncSession, data: Dict[str, Any]) -> Dict[str, Any]:
    """Cadastra um novo gestor no sistema e suas unidades extras."""
    username = data["username"].strip().lower()
    stmt = select(SystemManager).where(SystemManager.username == username)
    exists = (await session.execute(stmt)).scalar_one_or_none()
    if exists:
        raise ValueError(f"O gestor '{username}' já está cadastrado no sistema.")

    manager = SystemManager(
        username=username,
        name=data["name"].strip(),
        email=data.get("email"),
        role=data.get("role", "GESTOR"),
        responsible_area_id=data.get("responsible_area_id"),
        is_active=data.get("is_active", True),
    )
    session.add(manager)
    await session.flush()

    extra_unit_ids = data.get("extra_unit_ids", [])
    for aid in extra_unit_ids:
        session.add(ManagerExtraUnit(manager_id=manager.id, responsible_area_id=aid))

    await session.commit()
    return await get_manager_by_id(session, manager.id)


async def update_manager(session: AsyncSession, manager_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Atualiza dados de um gestor e suas unidades extras."""
    stmt = select(SystemManager).where(SystemManager.id == manager_id)
    manager = (await session.execute(stmt)).scalar_one_or_none()
    if not manager:
        raise ValueError("Gestor não encontrado.")

    if "name" in data:
        manager.name = data["name"].strip()
    if "email" in data:
        manager.email = data["email"]
    if "role" in data:
        manager.role = data["role"]
    if "responsible_area_id" in data:
        manager.responsible_area_id = data["responsible_area_id"]
    if "is_active" in data:
        manager.is_active = data["is_active"]

    if "extra_unit_ids" in data:
        await session.execute(delete(ManagerExtraUnit).where(ManagerExtraUnit.manager_id == manager_id))
        for aid in data["extra_unit_ids"]:
            session.add(ManagerExtraUnit(manager_id=manager.id, responsible_area_id=aid))

    await session.commit()
    return await get_manager_by_id(session, manager.id)


async def delete_manager(session: AsyncSession, manager_id: int) -> bool:
    """Remove um gestor do sistema."""
    stmt = select(SystemManager).where(SystemManager.id == manager_id)
    manager = (await session.execute(stmt)).scalar_one_or_none()
    if not manager:
        return False
    await session.delete(manager)
    await session.commit()
    return True


async def get_manager_by_id(session: AsyncSession, manager_id: int) -> Dict[str, Any]:
    stmt = select(SystemManager).options(
        selectinload(SystemManager.responsible_area),
        selectinload(SystemManager.extra_units).selectinload(ManagerExtraUnit.responsible_area),
    ).where(SystemManager.id == manager_id)

    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise ValueError("Gestor não encontrado.")

    return {
        "id": m.id,
        "username": m.username,
        "name": m.name,
        "email": m.email,
        "role": m.role,
        "is_active": m.is_active,
        "responsible_area_id": m.responsible_area_id,
        "responsible_area_nome": m.responsible_area.nome if m.responsible_area else None,
        "extra_units": [
            {"id": ex.responsible_area.id, "nome": ex.responsible_area.nome, "sigla": ex.responsible_area.sigla}
            for ex in m.extra_units if ex.responsible_area
        ],
    }
