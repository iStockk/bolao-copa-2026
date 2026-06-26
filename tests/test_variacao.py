"""Setas de variação de posição (▲ subiu / ▼ caiu / – igual / · sem histórico).

Regra: o baseline de comparação é a última ordem ESTÁVEL — só avança quando a
classificação muda. Assim as setas persistem entre execuções no-op (o robô roda
várias vezes por dia) e sempre refletem o movimento desde a última mexida.
"""
from gerar import calcular_variacao


def test_setas_aparecem_quando_a_classificacao_muda():
    # ontem A,B,C; hoje B passou A
    estado_ant = {"ordem": ["A", "B", "C"], "ordem_anterior": ["A", "B", "C"]}
    ranking = [("B", 50), ("A", 48), ("C", 40)]
    variacao, ordem_atual, ordem_baseline = calcular_variacao(ranking, estado_ant)
    assert variacao == {"B": 1, "A": -1, "C": 0}
    assert ordem_atual == ["B", "A", "C"]
    assert ordem_baseline == ["A", "B", "C"]


def test_setas_persistem_em_execucao_sem_mudanca():
    # robô roda de novo SEM jogos novos: ordem idêntica à do run anterior, mas
    # as setas NÃO podem zerar — devem seguir mostrando o movimento desde a
    # última vez que a classificação mexeu (este era o bug: tudo virava '–').
    estado_ant = {"ordem": ["B", "A", "C"], "ordem_anterior": ["A", "B", "C"]}
    ranking = [("B", 50), ("A", 48), ("C", 40)]
    variacao, ordem_atual, ordem_baseline = calcular_variacao(ranking, estado_ant)
    assert variacao == {"B": 1, "A": -1, "C": 0}
    assert ordem_baseline == ["A", "B", "C"]  # baseline congelado


def test_participante_sem_historico_nao_tem_seta():
    estado_ant = {"ordem": ["A", "B"], "ordem_anterior": ["A", "B"]}
    ranking = [("A", 50), ("C", 30), ("B", 20)]  # C entrou agora
    variacao, _, _ = calcular_variacao(ranking, estado_ant)
    assert variacao["C"] is None
    assert variacao["A"] == 0
    assert variacao["B"] == -1


def test_estado_vazio_nao_quebra():
    variacao, ordem_atual, ordem_baseline = calcular_variacao([("A", 1), ("B", 0)], {})
    assert variacao == {"A": None, "B": None}
    assert ordem_atual == ["A", "B"]
