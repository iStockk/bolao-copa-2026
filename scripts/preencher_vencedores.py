"""Auto-preenche os confrontos das SEMIFINAIS a partir dos resultados na mestre.

Em vez de digitar os vencedores das quartas na mão em `preparar_rodada.py`, este
script LÊ a aba Resultados (que o robô preenche sozinho conforme os jogos saem) +
os avanços de pênaltis do estado.json, deriva quem passou em J97..J100 e monta os
2 confrontos das semifinais (bracket oficial FIFA 2026):

    M101 = venc.J97 x venc.J98   |   M102 = venc.J99 x venc.J100

Uso (na raiz do repo):  python -m scripts.preencher_vencedores
- Se algum feeder (J97..J100) ainda não tem resultado, mostra o que já dá e diz
  quais faltam — NÃO gera o molde (jogo empatado sem avanço registrado conta como
  pendente; rode `python gerar.py` antes, pra o robô gravar o classificado).
- Quando os 4 vencedores estiverem definidos, chama preparar_rodada.preparar():
  gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar) e estende a mestre
  (jogos 101..102). Idempotente — pode rodar quantas vezes quiser.
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

# Bracket das semifinais: (jogo_sf, feeder1, feeder2, data, hora) em horário BRT.
# Semis FIFA 2026: SF1 14/jul (Dallas), SF2 15/jul (Atlanta); ambas 15h ET = 16h BRT.
SF_BRACKET = [
    (101, 97, 98,  "2026-07-14", "16:00"),  # 1º jogo = PRAZO
    (102, 99, 100, "2026-07-15", "16:00"),
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


def montar_confrontos(mestre=MESTRE_PADRAO):
    """Retorna (confrontos, pendentes).

    confrontos: lista de dicts {time1,time2,data,hora} na ordem M101..M102 (com
      None onde o vencedor ainda não saiu).
    pendentes: lista de nº de feeder (J97..J100) ainda sem vencedor definido."""
    wb = openpyxl.load_workbook(mestre, data_only=False)
    jogos = ler_jogos(wb)
    resultados = ler_resultados(wb)
    avancos = _carregar_avancos()

    confrontos, pendentes = [], []
    for _sf, f1, f2, data, hora in SF_BRACKET:
        v1, v2 = vencedor(f1, jogos, resultados, avancos), vencedor(f2, jogos, resultados, avancos)
        if v1 is None:
            pendentes.append(f1)
        if v2 is None:
            pendentes.append(f2)
        confrontos.append(dict(time1=v1, time2=v2, data=data, hora=hora))
    return confrontos, pendentes


def main(mestre=MESTRE_PADRAO):
    confrontos, pendentes = montar_confrontos(mestre)

    print("Confrontos das SEMIFINAIS derivados da mestre:")
    for (sf, f1, f2, _d, _h), c in zip(SF_BRACKET, confrontos):
        t1 = c["time1"] or f"?venc.J{f1}?"
        t2 = c["time2"] or f"?venc.J{f2}?"
        print(f"  J{sf}: {t1} x {t2}  ({c['data']} {c['hora']})")

    if pendentes:
        faltam = ", ".join(f"J{n}" for n in sorted(set(pendentes)))
        print(f"\n⏳ Ainda sem vencedor definido: {faltam}. "
              "Molde NÃO gerado. (Se um deles já jogou e empatou, rode `python "
              "gerar.py` antes pra o robô gravar quem passou nos pênaltis.)")
        return

    print("\n✅ Os 4 vencedores estão definidos — gerando molde + estendendo a mestre:\n")
    pr.preparar(confrontos=confrontos, mestre=mestre)


if __name__ == "__main__":
    main()
