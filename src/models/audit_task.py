"""
Modelos de Dados do Domínio de Auditoria (e-CGU / Governança / Áreas Responsáveis)
================================================================================
Define a estrutura relacional para importação de tarefas da CGU, controle de
prazos, áreas responsáveis e governança das gerências executivas do HC-UFPE.
"""

from datetime import datetime, date
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from ..resources.database import Base


class GovernanceUnit(Base):
    """
    Representa uma Gerência Executiva do HC-UFPE (Governança).
    Exemplos: SUP (Superintendência), GAD (Gerência Administrativa),
    GAS (Gerência de Atenção à Saúde), GEP (Gerência de Ensino e Pesquisa).
    """
    __tablename__ = "governance_units"

    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String(10), unique=True, nullable=False, index=True)
    nome = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    responsible_areas = relationship(
        "ResponsibleArea",
        back_populates="governance_unit",
        cascade="all, delete-orphan",
    )
    audit_tasks = relationship("AuditTask", back_populates="governance_unit")


task_responsible_areas = Table(
    "task_responsible_areas",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("audit_tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("responsible_area_id", Integer, ForeignKey("responsible_areas.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)


class ResponsibleArea(Base):
    """
    Representa uma Divisão, Setor ou Unidade Operacional responsável pela
    implementação das recomendações de auditoria vinculada a uma Gerência.
    """
    __tablename__ = "responsible_areas"

    id = Column(Integer, primary_key=True, index=True)
    governance_unit_id = Column(
        Integer,
        ForeignKey("governance_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nome = Column(String(200), nullable=False, index=True)
    sigla = Column(String(50), nullable=True)
    level = Column(String(50), nullable=True)  # 'GERENCIA', 'DIVISAO', 'SETOR', 'UNIDADE'
    parent_id = Column(Integer, ForeignKey("responsible_areas.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    governance_unit = relationship("GovernanceUnit", back_populates="responsible_areas")
    audit_tasks = relationship("AuditTask", back_populates="responsible_area")
    audit_tasks_multiple = relationship(
        "AuditTask",
        secondary="task_responsible_areas",
        back_populates="responsible_areas",
    )
    parent = relationship("ResponsibleArea", remote_side=[id], backref="children")


class ImportBatch(Base):
    """
    Registra cada lote/arquivo de importação do e-CGU (.xlsx),
    garantindo rastreabilidade e histórico de cargas.
    """
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
    total_rows = Column(Integer, default=0)
    inserted_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    ignored_count = Column(Integer, default=0)
    imported_by = Column(String(100), nullable=True)

    # Relacionamentos
    audit_tasks = relationship("AuditTask", back_populates="import_batch")


class AuditTask(Base):
    """
    Representa uma Tarefa / Apontamento de Auditoria do e-CGU.
    Contém os metadados oficiais e a correlação com a estrutura interna do hospital.
    """
    __tablename__ = "audit_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    state = Column(String(100), nullable=False, index=True)  # Em Análise..., Concluída, Cancelada
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True, index=True)
    audited_unit_raw = Column(String(200), nullable=True)
    monitoring_text = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    situation = Column(String(100), nullable=True, index=True)  # Não atendida, Parcialmente Atendida, Concluída

    governance_unit_id = Column(
        Integer,
        ForeignKey("governance_units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    responsible_area_id = Column(
        Integer,
        ForeignKey("responsible_areas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    import_batch_id = Column(
        Integer,
        ForeignKey("import_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relacionamentos
    governance_unit = relationship("GovernanceUnit", back_populates="audit_tasks")
    responsible_area = relationship("ResponsibleArea", back_populates="audit_tasks")
    responsible_areas = relationship(
        "ResponsibleArea",
        secondary="task_responsible_areas",
        back_populates="audit_tasks_multiple",
        lazy="selectin",
    )
    import_batch = relationship("ImportBatch", back_populates="audit_tasks")


class RnaMonthlySnapshot(Base):
    """Série temporal mensal de Recomendações Não Atendidas (RNA)."""
    __tablename__ = "rna_monthly_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    year_month = Column(String(7), unique=True, nullable=False, index=True)  # ex: '2024-05'
    label = Column(String(20), nullable=False)  # ex: 'Maio/24'
    count_rna = Column(Integer, nullable=False)
    snapshot_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemManager(Base):
    """Gestor pré-cadastrado no sistema com controle de acesso e lotação."""
    __tablename__ = "system_managers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)  # Login corporativo do AD
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="GESTOR")  # 'ADMINISTRADOR', 'SUPERINTENDENTE', 'AUDITOR', 'GESTOR'
    responsible_area_id = Column(Integer, ForeignKey("responsible_areas.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    responsible_area = relationship("ResponsibleArea", foreign_keys=[responsible_area_id])
    extra_units = relationship("ManagerExtraUnit", cascade="all, delete-orphan", back_populates="manager")


class ManagerExtraUnit(Base):
    """Matriz de Visibilidade: Unidades organizacionais extras concedidas ao gestor."""
    __tablename__ = "manager_extra_units"

    id = Column(Integer, primary_key=True, index=True)
    manager_id = Column(Integer, ForeignKey("system_managers.id", ondelete="CASCADE"), nullable=False, index=True)
    responsible_area_id = Column(Integer, ForeignKey("responsible_areas.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    manager = relationship("SystemManager", back_populates="extra_units")
    responsible_area = relationship("ResponsibleArea")
