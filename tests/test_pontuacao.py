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


def test_montar_ranking_ordena_desc_com_desempate():
    palpites = {"Ana": {1: (1, 0)}, "Bia": {1: (0, 0)}, "Cau": {1: (1, 0)}}
    # real 1x0: Ana e Cau acertam cheio (5); Bia (0x0) acerta só os gols do time2 (0==0) = 1
    resultados = {1: (1, 0)}
    ranking = montar_ranking(palpites, resultados, bonus_map={})
    assert ranking == [("Ana", 5), ("Cau", 5), ("Bia", 1)]
