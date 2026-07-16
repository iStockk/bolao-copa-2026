"""Auto-preenche os confrontos da ÚLTIMA RODADA (3º LUGAR + FINAL) a partir dos
resultados das semifinais na mestre.

Esta rodada tem uma pegadinha em relação às anteriores: o jogo do 3º lugar é
entre os PERDEDORES das semis (não os vencedores). Por isso, além do
`vencedor()` (usado na Final), este script tem um `perdedor()` (espelho: o time
que NÃO passou), usado no 3º lugar. Bracket oficial FIFA 2026:

    J103 (3º lugar) = PERDEDOR de J101 x PERDEDOR de J102
    J104 (Final)    = VENCEDOR de J101 x VENCEDOR de J102

Uso (na raiz do repo):  python -m scripts.preencher_vencedores
- Se alguma semi (J101/J102) ainda não tem resultado, mostra o que já dá e diz
  o que falta — NÃO gera o molde (semi empatada sem avanço registrado conta como
  pendente; rode `python gerar.py` antes, pra o robô gravar quem passou nos
  pênaltis).
- Quando as 2 semis estiverem decididas, chama preparar_rodada.preparar():
  gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar) e estende a mestre
  (jogos 103..104). Idempotente — pode rodar quantas vezes quiser.
  Depois: conferir a mestre e fazer commit/push.
"""
import json
import os
import sys

import openpyxl

try:  # no Windows o console é cp1252 e quebra com emoji/acento; força UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from bolao.planilha import ler_jogos, ler_resultados
from scripts.gerar_molde_mata_mata import MESTRE_PADRAO
from scripts import preparar_rodada as pr

ESTADO = "estado.json"

# Bracket da última rodada: (jogo, rótulo, feeder1, lado1, feeder2, lado2, data, hora).
# lado: "V" = pega o VENCEDOR do feeder | "P" = pega o PERDEDOR do feeder.
# Horários em BRT (= ET + 1h). FIFA 2026: 3º lugar sáb 18/jul 17h ET = 18h BRT
# (Miami); Final dom 19/jul 15h ET = 16h BRT (MetLife). O 1º jogo (J103) é o
# PRAZO das apostas.
FINAL_BRACKET = [
    (103, "3º Lugar", 101, "P", 102, "P", "2026-07-18", "18:00"),  # perdedores; 1º jogo = PRAZO
    (104, "Final",    101, "V", 102, "V", "2026-07-19", "16:00"),  # vencedores
]


def _carregar_avancos():
    """{num:int -> 1|2} dos jogos decididos nos pênaltis (chaves viram str no JSON)."""
    if not os.path.exists(ESTADO):
        return {}
    with open(ESTADO, encoding="utf-8") as f:
        estado = json.load(f)
    out = {}
    for k, v in (estado.get("avancos") or {}).items():
        try:
            out[int(k)] = v
        except (ValueError, TypeError):
            pass
    return out


def vencedor(num, jogos, resultados, avancos):
    """Nome do time que passou no jogo `num`, ou None se ainda indefinido.

    Placar decisivo -> quem fez mais gols. Empate nos 120min -> vem de `avancos`
    (1=time1/casa, 2=time2/visitante); empate sem avanço registrado -> None."""
    j = jogos.get(num)
    if j is None:
        return None
    rc, rf = resultados.get(num, (None, None))
    if rc is None or rf is None:
        return None
    if rc > rf:
        return j.time1
    if rf > rc:
        return j.time2
    av = avancos.get(num)  # empate nos 120min -> decidido nos pênaltis
    return j.time1 if av == 1 else (j.time2 if av == 2 else None)


def perdedor(num, jogos, resultados, avancos):
    """Espelho de vencedor(): o time que NÃO passou no jogo `num`, ou None.

    Placar decisivo -> quem fez MENOS gols. Empate nos 120min -> o que NÃO está
    em `avancos` (1=passou casa -> perdedor é o visitante; 2 -> perdedor é a
    casa); empate sem avanço registrado -> None."""
    j = jogos.get(num)
    if j is None:
        return None
    rc, rf = resultados.get(num, (None, None))
    if rc is None or rf is None:
        return None
    if rc > rf:
        return j.time2
    if rf > rc:
        return j.time1
    av = avancos.get(num)  # empate nos 120min -> perdedor é quem NÃO passou
    return j.time2 if av == 1 else (j.time1 if av == 2 else None)


def _time(num, lado, jogos, resultados, avancos):
    """Aplica vencedor() ou perdedor() conforme o lado ('V' ou 'P')."""
    fn = vencedor if lado == "V" else perdedor
    return fn(num, jogos, resultados, avancos)


def montar_confrontos(mestre=MESTRE_PADRAO):
    """Retorna (confrontos, pendentes).

    confrontos: lista de dicts {rodada,time1,time2,data,hora} na ordem J103..J104
      (com None onde o time ainda não saiu).
    pendentes: lista de nº de feeder (J101/J102) ainda sem resultado definido."""
    wb = openpyxl.load_workbook(mestre, data_only=False)
    jogos = ler_jogos(wb)
    resultados = ler_resultados(wb)
    avancos = _carregar_avancos()

    confrontos, pendentes = [], []
    for _jogo, rotulo, f1, l1, f2, l2, data, hora in FINAL_BRACKET:
        v1 = _time(f1, l1, jogos, resultados, avancos)
        v2 = _time(f2, l2, jogos, resultados, avancos)
        if v1 is None:
            pendentes.append(f1)
        if v2 is None:
            pendentes.append(f2)
        confrontos.append(dict(rodada=rotulo, time1=v1, time2=v2, data=data, hora=hora))
    return confrontos, pendentes


def main(mestre=MESTRE_PADRAO):
    confrontos, pendentes = montar_confrontos(mestre)

    print("Confrontos da ÚLTIMA RODADA (3º lugar + Final) derivados da mestre:")
    for (jogo, rotulo, f1, l1, f2, l2, _d, _h), c in zip(FINAL_BRACKET, confrontos):
        t1 = c["time1"] or f"?{'venc' if l1 == 'V' else 'perd'}.J{f1}?"
        t2 = c["time2"] or f"?{'venc' if l2 == 'V' else 'perd'}.J{f2}?"
        print(f"  J{jogo} ({rotulo}): {t1} x {t2}  ({c['data']} {c['hora']})")

    if pendentes:
        faltam = ", ".join(f"J{n}" for n in sorted(set(pendentes)))
        print(f"\n⏳ Ainda sem resultado definido: {faltam}. "
              "Molde NÃO gerado. (Se uma semi já jogou e empatou nos 120min, rode "
              "`python gerar.py` antes pra o robô gravar quem passou nos pênaltis.)")
        return

    print("\n✅ As 2 semifinais estão decididas — gerando molde + estendendo a mestre:\n")
    pr.preparar(confrontos=confrontos, mestre=mestre)


if __name__ == "__main__":
    main()
