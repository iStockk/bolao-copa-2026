from bolao.pontuacao import pontos_jogo, total_participante, montar_ranking


def test_acerto_cheio_vale_5():
    # resultado(2) + gols1(1) + gols2(1) + total(1)
    assert pontos_jogo(4, 2, 4, 2) == 5


def test_so_resultado_certo_vale_2():
    # mandante vence em ambos; placares e total errados
    assert pontos_jogo(3, 1, 1, 0) == 2


def test_so_gols_mandante_vale_1():
    # palpite 2x0 (mandante vence), real 2x3 (visitante vence): só acerta gols do time1
    assert pontos_jogo(2, 0, 2, 3) == 1


def test_so_total_vale_1():
    # palpite 3x0 e real 0x3: resultado oposto, gols errados, mas total 3==3
    assert pontos_jogo(3, 0, 0, 3) == 1


def test_empate_acertado_vale_2():
    # palpite empate 1x1, real empate 2x2: acerta o resultado (empate), resto errado
    assert pontos_jogo(1, 1, 2, 2) == 2


def test_sem_numero_vale_0():
    assert pontos_jogo(None, 1, 2, 0) == 0
    assert pontos_jogo(1, 1, None, None) == 0


def test_total_participante_soma_e_bonus():
    palpites = {1: (2, 1), 2: (0, 0)}
    resultados = {1: (2, 1), 2: (1, 1), 3: (None, None)}
    # jogo1: acerto cheio = 5; jogo2: palpite 0x0 vs real 1x1 -> só acerta o empate = 2; +bonus 10
    assert total_participante(palpites, resultados, bonus=10) == 5 + 2 + 10


def test_total_ignora_jogos_excluidos():
    palpites = {1: (2, 0), 5: (1, 0)}
    resultados = {1: (2, 0), 5: (1, 0)}  # acerto cheio nos dois (5 cada)
    assert total_participante(palpites, resultados) == 10
    assert total_participante(palpites, resultados, ignorar={1}) == 5


def test_montar_ranking_ordena_desc_com_desempate():
    palpites = {"Ana": {1: (1, 0)}, "Bia": {1: (0, 0)}, "Cau": {1: (1, 0)}}
    # real 1x0: Ana e Cau acertam cheio (5); Bia (0x0) acerta só os gols do time2 (0==0) = 1
    resultados = {1: (1, 0)}
    ranking = montar_ranking(palpites, resultados, bonus_map={})
    assert ranking == [("Ana", 5), ("Cau", 5), ("Bia", 1)]


# --- Mata-mata: jogo decidido nos pênaltis (placar vale até 120min). O +2 vai
# --- para quem apontou o TIME QUE PASSOU **ou** para quem CRAVOU o empate dos
# --- 120min (regra 01/07/2026 — empate cravado também pode valer os 5).
# --- avanca=1 -> passou o time1 (casa); avanca=2 -> passou o time2 (visitante).

def test_penaltis_quem_apontou_o_time_que_passou_ganha_o_2():
    # real 1x1, passou o visitante (avanca=2). Palpite 0x2 (apontou o visitante):
    # +2 (passou quem ele disse) + 1 (total 2==2); gols errados.
    assert pontos_jogo(0, 2, 1, 1, avanca=2) == 3


def test_penaltis_empate_cravado_vale_5():
    # regra 01/07/2026: real 1x1 (foi pros pênaltis), palpite empate 1x1 CRAVADO:
    # +2 (cravou o empate dos 120min) +1 casa +1 visitante +1 total = 5.
    assert pontos_jogo(1, 1, 1, 1, avanca=2) == 5


def test_penaltis_empate_no_sinal_mas_gols_errados_leva_so_o_2():
    # real 1x1 nos pênaltis, palpite 2x2 (empate, mas gols errados):
    # +2 (acertou o empate) + 0 gols (2!=1) + 0 total (4!=2) = 2.
    assert pontos_jogo(2, 2, 1, 1, avanca=2) == 2


def test_penaltis_quem_apontou_o_time_errado_nao_ganha_o_2():
    # real 1x1, passou o visitante. Palpite 2x0 (apontou o mandante): sem +2;
    # só o +1 do total (2==2).
    assert pontos_jogo(2, 0, 1, 1, avanca=2) == 1


def test_penaltis_passou_o_mandante():
    # real 0x0, passou o mandante (avanca=1). Palpite 1x0 (apontou o mandante):
    # +2 + 1 (gols visitante 0==0); total 1!=0.
    assert pontos_jogo(1, 0, 0, 0, avanca=1) == 3


def test_total_participante_usa_avancos_dos_penaltis():
    palpites = {1: (0, 2)}            # apontou o visitante
    resultados = {1: (1, 1)}          # 1x1, foi pros pênaltis
    # com avancos (passou o visitante): +2 + total = 3
    assert total_participante(palpites, resultados, avancos={1: 2}) == 3
    # sem avancos (tratado como empate normal): só o +1 do total = 1
    assert total_participante(palpites, resultados) == 1


def test_montar_ranking_propaga_avancos():
    palpites = {"Ana": {1: (0, 1)}, "Bia": {1: (2, 0)}}
    resultados = {1: (1, 1)}          # 1x1 nos pênaltis, passou o visitante
    ranking = montar_ranking(palpites, resultados, bonus_map={}, avancos={1: 2})
    # Ana apontou o visitante (+2, +1 visitante) = 3; Bia apontou o mandante = só total = 1
    assert ranking == [("Ana", 3), ("Bia", 1)]
