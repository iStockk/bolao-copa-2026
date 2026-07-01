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


def pontos_jogo(pc, pf, rc, rf, avanca=None):
    """Pontos de um palpite (pc, pf) contra o resultado real (rc, rf).

    avanca: usado no mata-mata quando o jogo foi decidido nos PÊNALTIS (placar
    empatado nos 120min). Indica quem se classificou — 1=time1 (casa), 2=time2
    (visitante). Nesse caso o +2 do resultado vai para quem APONTOU o time que
    passou OU para quem CRAVOU o empate dos 120min (regra 01/07/2026: empate
    cravado também pode valer os 5). Em jogo normal (avanca=None), o +2 é pelo
    acerto do sinal V/E/D, como sempre.
    """
    if not all(_num(v) for v in (pc, pf, rc, rf)):
        return 0
    if avanca is None:
        p = 2 if _sign(pc - pf) == _sign(rc - rf) else 0
    else:
        # Jogo de pênaltis: leva o +2 quem apontou o time que PASSOU ou quem
        # CRAVOU o empate dos 120min. Como avanca só é setado em jogo empatado
        # nos 120min, "acertar o sinal V/E/D" aqui equivale a ter apostado empate.
        palpite_vencedor = 1 if pc > pf else (2 if pf > pc else 0)  # 0 = apostou empate
        acertou_avanco = palpite_vencedor == avanca
        acertou_resultado = _sign(pc - pf) == _sign(rc - rf)
        p = 2 if (acertou_avanco or acertou_resultado) else 0
    p += 1 if pc == rc else 0
    p += 1 if pf == rf else 0
    p += 1 if pc + pf == rc + rf else 0
    return p


def total_participante(palpites, resultados, bonus=0, ignorar=(), avancos=None):
    """Soma os pontos de um participante sobre todos os jogos com resultado.

    palpites: dict {num_jogo: (gols1, gols2)}
    resultados: dict {num_jogo: (gols1, gols2) | (None, None)}
    ignorar: conjunto de números de jogos que NÃO contam (ex.: os 4 primeiros).
    avancos: dict {num_jogo: 1|2} — quem passou nos jogos decididos por pênaltis.
    """
    avancos = avancos or {}
    total = bonus
    for num, res in resultados.items():
        if num in ignorar:
            continue
        rc, rf = res
        if rc is None or rf is None:
            continue
        pc, pf = palpites.get(num, (None, None))
        total += pontos_jogo(pc, pf, rc, rf, avanca=avancos.get(num))
    return total


def montar_ranking(palpites_por_part, resultados, bonus_map, ignorar=(), avancos=None):
    """Lista (nome, pontos) ordenada por pontos desc, desempate alfabético."""
    linhas = [
        (nome, total_participante(palpites, resultados, bonus_map.get(nome, 0), ignorar, avancos))
        for nome, palpites in palpites_por_part.items()
    ]
    linhas.sort(key=lambda x: (-x[1], x[0]))
    return linhas
