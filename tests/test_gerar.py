"""Testes do orquestrador (gerar.py): casamento de partidas e merge de avanços."""
from bolao.modelo import Jogo
from bolao.fetcher import Partida
from gerar import casar_partidas, _merge_avancos, _fase_atual


def test_casar_partidas_par_unico_orienta_pela_planilha():
    jogos = {73: Jogo(73, "MM", "Brasil", "Croácia", "2026-07-05", "16:00")}
    # ESPN trouxe Croácia como mandante (ordem invertida vs planilha)
    partidas = [Partida("Croácia", "Brasil", 1, 2, "2026-07-05", None)]
    casados, faltam = casar_partidas(jogos, partidas)
    assert faltam == []
    # reorientado p/ Brasil(time1) x Croácia(time2): Brasil 2 x 1 Croácia
    assert casados == {73: (2, 1, None)}


def test_casar_partidas_penaltis_marca_quem_avancou():
    jogos = {73: Jogo(73, "MM", "Brasil", "Croácia", "2026-07-05", "16:00")}
    # 1x1, Croácia (time2 da planilha) passou nos pênaltis
    partidas = [Partida("Croácia", "Brasil", 1, 1, "2026-07-05", "Croácia")]
    casados, _ = casar_partidas(jogos, partidas)
    assert casados[73] == (1, 1, 2)  # avanca=2 -> classificado é o time2


def test_casar_partidas_penaltis_avanca_time1():
    jogos = {73: Jogo(73, "MM", "Brasil", "Croácia", "2026-07-05", "16:00")}
    partidas = [Partida("Brasil", "Croácia", 0, 0, "2026-07-05", "Brasil")]
    casados, _ = casar_partidas(jogos, partidas)
    assert casados[73] == (0, 0, 1)  # avanca=1 -> classificado é o time1


def test_casar_partidas_reencontro_desempata_por_data():
    jogos = {
        30: Jogo(30, "C", "Brasil", "Croácia", "2026-06-20", "16:00"),   # grupos
        80: Jogo(80, "MM", "Brasil", "Croácia", "2026-07-05", "16:00"),  # mata-mata
    }
    partidas = [Partida("Brasil", "Croácia", 0, 0, "2026-07-05", "Croácia")]
    casados, _ = casar_partidas(jogos, partidas)
    assert 80 in casados and 30 not in casados  # casa no jogo de data próxima
    assert casados[80] == (0, 0, 2)


def test_casar_partidas_par_inexistente_vai_para_nao_encontradas():
    jogos = {73: Jogo(73, "MM", "Brasil", "Croácia", "2026-07-05", "16:00")}
    partidas = [Partida("Argentina", "França", 2, 0, "2026-07-05", None)]
    casados, faltam = casar_partidas(jogos, partidas)
    assert casados == {}
    assert [(p.time1, p.time2) for p in faltam] == [("Argentina", "França")]


def test_merge_avancos_normaliza_chaves_e_prioriza_novos():
    prev = {"73": 1, "74": 2}   # do estado.json (chaves viram string no JSON)
    novos = {74: 1, 75: 2}      # detectados nesta run (chaves int)
    out = _merge_avancos(prev, novos)
    assert out == {73: 1, 74: 1, 75: 2}  # novos[74] sobrescreve prev["74"]


def test_fase_atual_grupos_quando_so_ha_jogos_ate_72():
    resultados = {1: (1, 0), 72: (2, 2)}
    assert _fase_atual(resultados) == "Fase de Grupos"


def test_fase_atual_mata_mata_quando_ha_placar_apos_72():
    resultados = {72: (2, 2), 73: (1, 0)}
    assert _fase_atual(resultados) == "Mata-mata"


def test_fase_atual_ignora_jogo_do_mata_mata_ainda_sem_placar():
    resultados = {72: (2, 2), 73: (None, None)}  # confronto criado, jogo não rolou
    assert _fase_atual(resultados) == "Fase de Grupos"
