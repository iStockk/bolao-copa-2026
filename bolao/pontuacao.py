"""Pontuação do bolão — espelha EXATAMENTE a fórmula da coluna K da planilha.

Por jogo (máx. 5):
  +2 se acertou o resultado (V/E/D), via sinal de (gols1 - gols2)
  +1 se acertou os gols do time1
  +1 se acertou os gols do time2
  +1 se acertou o total de gols
Só pontua se palpite e resultado forem ambos numéricos.
"""


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _sign(n):
    return (n > 0) - (n < 0)


def pontos_jogo(pc, pf, rc, rf):
    """Pontos de um palpite (pc, pf) contra o resultado real (rc, rf)."""
    if not all(_num(v) for v in (pc, pf, rc, rf)):
        return 0
    p = 2 if _sign(pc - pf) == _sign(rc - rf) else 0
    p += 1 if pc == rc else 0
    p += 1 if pf == rf else 0
    p += 1 if pc + pf == rc + rf else 0
    return p


def total_participante(palpites, resultados, bonus=0):
    """Soma os pontos de um participante sobre todos os jogos com resultado.

    palpites: dict {num_jogo: (gols1, gols2)}
    resultados: dict {num_jogo: (gols1, gols2) | (None, None)}
    """
    total = bonus
    for num, res in resultados.items():
        rc, rf = res
        if rc is None or rf is None:
            continue
        pc, pf = palpites.get(num, (None, None))
        total += pontos_jogo(pc, pf, rc, rf)
    return total


def montar_ranking(palpites_por_part, resultados, bonus_map):
    """Lista (nome, pontos) ordenada por pontos desc, desempate alfabético."""
    linhas = [
        (nome, total_participante(palpites, resultados, bonus_map.get(nome, 0)))
        for nome, palpites in palpites_por_part.items()
    ]
    linhas.sort(key=lambda x: (-x[1], x[0]))
    return linhas
