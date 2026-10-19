import asyncio
import os
import sys

proj_dir = r"C:\Users\tassio.silva\OneDrive - HU BRASIL\HC_DEV\Sistema de Gerenciamento de Tarefas de Auditoria"
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)

from sqlalchemy import select, update
from src.resources.database import DatabaseManager, Base
from src.models import GovernanceUnit, ResponsibleArea, AuditTask

ORGANOGRAMA = {
    "SUP": [
        "Colegiado Executivo",
        "Conselho Consultivo",
        "Ouvidoria",
        "Auditoria",
        "Setor de Gestão da Qualidade - SGQ",
        "Unidade de Vigilância em Saúde - UVS",
        "Unidade de Gestão da Qualidade e Segurança do Paciente - UGQSP",
        "Setor de Governança e Estratégia - SGE",
        "Unidade de Gestão Estratégica, de Riscos e Controles Internos - UGERCI",
        "Setor de Contratualização e Regulação - SCR",
        "Unidade de Contratualização - UCONT",
        "Unidade de Regulação Interna - URI",
        "Unidade de Gestão de Processamento da Informação Assistencial - UGPIA",
        "Setor de Tecnologia da Informação e Saúde Digital - SETISD",
        "Unidade de Sistemas da Informação e Inteligência de Dados - USIID",
        "Unidade de Infraestrutura, Suporte e Segurança de TI - UISTI",
    ],
    "GAD": [
        "Divisão de Gestão de Pessoas - DGP",
        "Unidade de Desenvolvimento de Pessoal - UDP",
        "Unidade de Administração de Pessoal - UAP",
        "Unidade de Saúde Ocupacional e Segurança do Trabalho - USOST",
        "Divisão de Administração e Finanças - DAF",
        "Setor de Administração - SAD",
        "Unidade de Compras e Licitações - UCL",
        "Unidade de Contratos - UCONTR",
        "Unidade de Patrimônio - UPAT",
        "Unidade de Fiscalização Administrativa de Contratos - UFAC",
        "Setor de Gestão Orçamentária e Financeira - SGOF",
        "Unidade de Execução Orçamentária e Financeira - UEOF",
        "Unidade de Planejamento e Gestão Orçamentária - UPGO",
        "Setor de Contabilidade - SCONT",
        "Divisão de Logística e Infraestrutura Hospitalar - DLIH",
        "Setor de Infraestrutura Física - SINFRA",
        "Setor de Hotelaria Hospitalar - SHH",
        "Unidade de Suporte Operacional - USOP",
        "Setor de Engenharia Clínica - SEC",
        "Setor de Abastecimento Farmacêutico e Suprimentos - SAFS",
        "Unidade de Almoxarifado e Controle de Estoques - UACE",
        "Unidade de Planejamento e Dimensionamento de Estoques - UPDE",
    ],
    "GAS": [
        "Divisão Médica - DMED",
        "Divisão de Enfermagem - DENF",
        "Divisão de Gestão do Cuidado - DGC",
        "Unidade de Clínica Médica",
        "Unidade de Saúde da Mulher",
        "Unidade de Cabeça e Pescoço",
        "Unidade de Clínica Cirúrgica",
        "Unidade de Hematologia, Hemoterapia e Oncologia",
        "Unidade de Saúde Mental",
        "Unidade de Apoio à Gestão em Enfermagem",
        "Unidade de Ambulatório",
        "Unidade da Criança e do Adolescente",
        "Unidade de Transplante",
        "Unidade do Sistema Urinário",
        "Unidade Multiprofissional",
        "Unidade de Sistema Neuro-Músculo-Esquelético",
        "Unidade de Sistema Cardiovascular",
        "Divisão de Apoio Diagnóstico e Terapêutico - DADT",
        "Setor de Apoio Diagnóstico e Terapêutico",
        "Unidade de Diagnóstico por Imagem",
        "Unidade de Diagnósticos Especializados",
        "Unidade de Análises Clínicas e Anatomia Patológica",
        "Setor de Farmácia Hospitalar",
        "Unidade de Farmácia Clínica e Dispensação Farmacêutica",
        "Setor de Paciente Crítico",
        "Unidade de Urgência e Emergência",
        "Unidade de Bloco Cirúrgico e Processamento de Material Esterilizado",
        "Unidade de Terapia Intensiva - Pediátrico e Neonatal",
        "Unidade de Terapia Intensiva - Adulto",
    ],
    "GEP": [
        "Unidade de e-Saúde",
        "Setor de Gestão do Ensino - SGE",
        "Unidade de Gestão de Pós-Graduação - UGPG",
        "Unidade de Gestão de Graduação, Ensino Técnico e Extensão - UGGETE",
        "Setor de Gestão da Pesquisa e da Inovação Tecnológica em Saúde - SGPITS",
        "Unidade de Gestão da Pesquisa - UGPESQ",
        "Unidade de Gestão da Inovação Tecnológica em Saúde - UGITS",
    ],
}

ALIAS_MAP = {
    "SETISD": "Setor de Tecnologia da Informação e Saúde Digital - SETISD",
    "SGQ": "Setor de Gestão da Qualidade - SGQ",
    "SGE": "Setor de Governança e Estratégia - SGE",
    "SCR": "Setor de Contratualização e Regulação - SCR",
    "SINFRA": "Setor de Infraestrutura Física - SINFRA",
    "DGP": "Divisão de Gestão de Pessoas - DGP",
    "DAF": "Divisão de Administração e Finanças - DAF",
    "DLIH": "Divisão de Logística e Infraestrutura Hospitalar - DLIH",
    "GEP": "Setor de Gestão do Ensino - SGE",
    "DGC": "Divisão de Gestão do Cuidado - DGC",
    "DADT": "Divisão de Apoio Diagnóstico e Terapêutico - DADT",
    "DMED": "Divisão Médica - DMED",
    "DENF": "Divisão de Enfermagem - DENF",
}


async def seed_organograma():
    db_dsn = "sqlite+aiosqlite:///" + os.path.join(proj_dir, "data", "app.db")
    db = DatabaseManager(db_dsn)
    print(f"[*] Conectando ao banco de dados: {db_dsn}")

    async with db.async_session_maker() as session:
        # 1. Carregar Unidades de Governança
        gov_res = await session.execute(select(GovernanceUnit))
        gov_units = {u.sigla: u for u in gov_res.scalars().all()}

        # 2. Mapeamento de áreas existentes
        areas_res = await session.execute(select(ResponsibleArea))
        existing_areas = {a.nome: a for a in areas_res.scalars().all()}

        # 3. Inserir ou atualizar áreas do organograma
        name_to_area_id = {}
        for sigla, area_list in ORGANOGRAMA.items():
            gov = gov_units.get(sigla)
            if not gov:
                continue

            for name in area_list:
                area = existing_areas.get(name)
                if not area:
                    # Checar se alguma antiga corresponde
                    for old_name, full_name in ALIAS_MAP.items():
                        if full_name == name and old_name in existing_areas:
                            area = existing_areas[old_name]
                            area.nome = name
                            area.governance_unit_id = gov.id
                            break

                if not area:
                    area = ResponsibleArea(nome=name, governance_unit_id=gov.id)
                    session.add(area)
                    await session.flush()
                else:
                    area.governance_unit_id = gov.id

                name_to_area_id[name] = area.id

        await session.commit()
        print(f"[+] Total de unidades organizacionais no organograma oficial: {len(name_to_area_id)}")

        # 4. Ajustar tarefas vinculadas a nomes antigos
        all_areas_res = await session.execute(select(ResponsibleArea))
        final_areas = {a.nome: a.id for a in all_areas_res.scalars().all()}

        for old_sigla, full_name in ALIAS_MAP.items():
            if full_name in final_areas:
                target_id = final_areas[full_name]
                old_area = existing_areas.get(old_sigla)
                if old_area and old_area.id != target_id:
                    await session.execute(
                        update(AuditTask)
                        .where(AuditTask.responsible_area_id == old_area.id)
                        .values(responsible_area_id=target_id)
                    )

        await session.commit()
        print("[+] Atribuições de tarefas migradas com sucesso para as unidades do organograma oficial.")

    await db.close_connection()

    dest_path = os.path.join(proj_dir, "src", "scripts", "seed_organograma_hcufpe.py")
    with open(__file__, "r", encoding="utf-8") as f_src:
        code = f_src.read()
        with open(dest_path, "w", encoding="utf-8") as f_dst:
            f_dst.write(code)
    print(f"[+] Salvo em: {dest_path}")


if __name__ == "__main__":
    asyncio.run(seed_organograma())
