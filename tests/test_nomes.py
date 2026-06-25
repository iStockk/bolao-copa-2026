import openpyxl

import bolao.nomes as n
from bolao.nomes import casar_time, normalizar
from bolao.planilha import ler_jogos

ARQUIVO = "TABELA_APOSTAS_-_COPA_2026.xlsx"


def test_todos_os_times_da_planilha_tem_mapeamento():
    wb = openpyxl.load_workbook(ARQUIVO, data_only=True)
    times = set()
    for j in ler_jogos(wb).values():
        times.add(j.time1)
        times.add(j.time2)
    valores = set(n.MAPA.values())
    faltando = times - valores
    assert faltando == set(), f"sem mapeamento: {faltando}"


def test_aliases_chave_da_espn():
    assert casar_time("Brazil") == "Brasil"
    assert casar_time("Scotland") == "Escócia"
    assert casar_time("Türkiye") == "Turquia"
    assert casar_time("Turkey") == "Turquia"
    assert casar_time("South Korea") == "Coreia do Sul"
    assert casar_time("Czechia") == "Tchéquia"
    assert casar_time("Bosnia-Herzegovina") == "Bósnia"
    assert casar_time("Côte d'Ivoire") == "Costa do Marfim"
    assert casar_time("DR Congo") == "RD Congo"
    assert casar_time("United States") == "EUA"


def test_nome_desconhecido_retorna_none():
    assert casar_time("Atlantis") is None
    assert casar_time(None) is None


def test_normalizar_remove_acentos_e_pontuacao():
    assert normalizar("São Tomé!") == "saotome"
    assert normalizar("Bosnia-Herzegovina") == "bosniaherzegovina"
