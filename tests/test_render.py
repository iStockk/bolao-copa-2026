from bolao.render import render_pagina
from bolao.modelo import PARTICIPANTES, PREMIO


def _ranking_exemplo():
    return [(nome, 100 - i * 3) for i, (nome, _aba) in enumerate(PARTICIPANTES)]


def test_html_tem_titulo_nomes_data_e_premio():
    ranking = _ranking_exemplo()
    html = render_pagina(
        ranking,
        variacao={ranking[0][0]: 2, ranking[1][0]: -1},
        resultados_rodada=[("Brasil", 3, 0, "Escócia")],
        pontos_rodada={ranking[0][0]: 7},
        premio=PREMIO,
        atualizado_em="25/06/2026 às 10:00",
        data_rodada="24/06",
    )
    assert "Bolão Copa 2026" in html
    assert "25/06/2026 às 10:00" in html
    for nome, _ in ranking:
        assert nome in html, nome
    # valores do prêmio
    assert "325" in html and "195" in html and "130" in html
    # documento html válido começa com doctype
    assert html.lstrip().startswith("<!doctype html>")


def test_resultados_opcionais_podem_faltar():
    # sem resultados/rodada, ainda renderiza (sem seção de jogos)
    html = render_pagina([("Ana", 10), ("Bia", 5)], atualizado_em="x")
    assert "Ana" in html and "Bia" in html
    assert "Resultados" not in html  # seção de resultados omitida


def test_kicker_usa_a_fase_informada():
    html = render_pagina([("Ana", 10)], atualizado_em="x", fase="Mata-mata")
    assert "Mata-mata" in html
    assert "Fase de Grupos" not in html


def test_kicker_default_e_fase_de_grupos():
    html = render_pagina([("Ana", 10)], atualizado_em="x")
    assert "Fase de Grupos" in html
