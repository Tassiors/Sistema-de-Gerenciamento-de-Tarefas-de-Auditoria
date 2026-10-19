"""
Script de Seed Inicial: Governança e Áreas Responsáveis do HC-UFPE
==================================================================
Popula as 4 gerências executivas (SUP, GAD, GAS, GEP) e todos os setores
e divisões catalogados no monitoramento de auditoria.
"""

import asyncio
import os
import sys

# Garantir que o diretório raiz do projeto esteja no sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

load_dotenv()

from src.models import GovernanceUnit, ResponsibleArea

GOVERNANCE_DATA = [
    {
        "sigla": "SUP",
        "nome": "Superintendência",
        "areas": [
            "SUPERINTENDÊNCIA",
            "SETOR DE GOVERNANÇA E ESTRATÉGIA",
            "SETOR DE CONTRATUALIZAÇÃO E REGULAÇÃO",
            "UNIDADE DE GESTÃO DA ESTRATÉGIA, RISCOS E CONTROLES INTERNOS (UGERC)",
            "UNIDADE DE COMUNICAÇÃO SOCIAL",
            "OUVIDORIA",
        ]
    },
    {
        "sigla": "GAD",
        "nome": "Gerência Administrativa",
        "areas": [
            "GERÊNCIA ADMINISTRATIVA",
            "DIVISÃO DE ADMINISTRAÇÃO E FINANÇAS",
            "DIVISÃO DE LOGÍSTICA E INFRAESTRUTURA HOSPITALAR (DLIH)",
            "DIVISÃO DE GESTÃO DE PESSOAS",
            "SETOR DE ABASTECIMENTO FARMACÊUTICO E SUPRIMENTOS (SAFS)",
            "SETOR DE INFRAESTRUTURA FÍSICA",
            "SETOR DE ENGENHARIA CLÍNICA",
            "SETOR DE CONTABILIDADE",
            "SETOR DE ORÇAMENTO E FINANÇAS",
            "SETOR DE ADMINISTRAÇÃO",
            "UNIDADE DE PATRIMÔNIO",
            "UNIDADE DE COMPRAS E LICITAÇÕES",
            "UNIDADE DE ALMOXARIFADO",
            "SAFS + SETOR DE INFRAESTRUTURA FÍSICA",
            "SAFS + SETOR DE CONTABILIDADE",
            "DIVISÃO DE ADMINISTRAÇÃO E FINANÇAS + DLIH",
        ]
    },
    {
        "sigla": "GAS",
        "nome": "Gerência de Atenção à Saúde",
        "areas": [
            "GERÊNCIA DE ATENÇÃO À SAÚDE",
            "DIVISÃO MÉDICA",
            "DIVISÃO DE ENFERMAGEM",
            "DIVISÃO DE APOIO DIAGNÓSTICO E TERAPÊUTICO",
            "DIVISÃO DE GESTÃO DO CUIDADO",
            "SETOR DE VIGILÂNCIA EM SAÚDE E SEGURANÇA DO PACIENTE",
            "SETOR DE FARMÁCIA CLÍNICA",
            "SETOR DE PACIENTE CRÍTICO",
        ]
    },
    {
        "sigla": "GEP",
        "nome": "Gerência de Ensino e Pesquisa",
        "areas": [
            "GERÊNCIA DE ENSINO E PESQUISA",
            "SETOR DE GESTÃO DO ENSINO",
            "SETOR DE GESTÃO DA PESQUISA E INOVAÇÃO TECNOLÓGICA",
            "UNIDADE DE PÓS-GRADUAÇÃO",
            "UNIDADE DE GESTÃO DA PESQUISA",
        ]
    }
]


async def seed():
    dsn = os.getenv("SQLITE_DSN") or os.getenv("APP_DB_URL") or "sqlite+aiosqlite:///data/app.db"
    print(f"Connecting to database: {dsn}")
    engine = create_async_engine(dsn, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for gov in GOVERNANCE_DATA:
            stmt = select(GovernanceUnit).where(GovernanceUnit.sigla == gov["sigla"])
            res = await session.execute(stmt)
            unit = res.scalar_one_or_none()

            if not unit:
                unit = GovernanceUnit(sigla=gov["sigla"], nome=gov["nome"])
                session.add(unit)
                await session.flush()
                print(f"[+] Gerência inserida: {unit.sigla} - {unit.nome}")
            else:
                print(f"[*] Gerência já existe: {unit.sigla} - {unit.nome}")

            for area_nome in gov["areas"]:
                stmt_area = select(ResponsibleArea).where(
                    ResponsibleArea.governance_unit_id == unit.id,
                    ResponsibleArea.nome == area_nome
                )
                res_area = await session.execute(stmt_area)
                area = res_area.scalar_one_or_none()

                if not area:
                    area = ResponsibleArea(governance_unit_id=unit.id, nome=area_nome)
                    session.add(area)
                    print(f"    [+] Área vinculada: {area_nome} -> {unit.sigla}")

        await session.commit()
        print("\n[SUCCESS] Seed de Governança e Áreas concluído com sucesso!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
