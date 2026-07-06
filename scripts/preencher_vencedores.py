"""Auto-preenche os confrontos das QUARTAS a partir dos resultados na mestre.

Em vez de digitar os vencedores das oitavas na mão em `preparar_rodada.py`, este
script LÊ a aba Resultados (que o robô preenche sozinho conforme os jogos saem) +
os avanços de pênaltis do estado.json, deriva quem passou em J89..J96 e monta os
4 confrontos das quartas (bracket oficial FIFA 2026):

    M97 = venc.J89 x venc.J90   |   M98 = venc.J93 x venc.J94
    M99 = venc.J91 x venc.J92   |   M100 = venc.J95 x venc.J96

Uso (na raiz do repo):  python -m scripts.preencher_vencedores
- Se algum feeder (J89..J96) ainda não tem resultado, mostra o que já dá e diz
  quais faltam — NÃO gera o molde (jogo empatado sem avanço registrado conta como
  pendente; rode `python gerar.py` antes, pra o robô gravar o classificado).
- Quando os 8 vencedores estiverem definidos, chama preparar_rodada.preparar():
  gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar) e estende a mestre
  (jogos 97..100). Idempotente — pode rodar quantas vezes quiser.
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

# Bracket das quartas: (jogo_qf, feeder1, feeder2, data, hora) em horário BRT.
QF_BRACKET = [
    (97,  89, 90, "2026-07-09", "17:00"),  # 1º jogo = PRAZO
    (98,  93, 94, "2026-07-10", "13:00"),
    (99,  91, 92, "2026-07-11", "18:00"),
    (100, 95, 96, "2026-07-11", "21:00"),
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

    confrontos: lista de dicts {time1,time2,data,hora} na ordem M97..M100 (com
      None onde o vencedor ainda não saiu).
    pendentes: lista de nº de feeder (J89..J96) ainda sem vencedor definido."""
    wb = openpyxl.load_workbook(mestre, data_only=False)
    jogos = ler_jogos(wb)
    resultados = ler_resultados(wb)
    avancos = _carregar_avancos()

    confrontos, pendentes = [], []
    for _qf, f1, f2, data, hora in QF_BRACKET:
        v1, v2 = vencedor(f1, jogos, resultados, avancos), vencedor(f2, jogos, resultados, avancos)
        if v1 is None:
            pendentes.append(f1)
        if v2 is None:
            pendentes.append(f2)
        confrontos.append(dict(time1=v1, time2=v2, data=data, hora=hora))
    return confrontos, pendentes


def main(mestre=MESTRE_PADRAO):
    confrontos, pendentes = montar_confrontos(mestre)

    print("Confrontos das QUARTAS derivados da mestre:")
    for (qf, f1, f2, _d, _h), c in zip(QF_BRACKET, confrontos):
        t1 = c["time1"] or f"?venc.J{f1}?"
        t2 = c["time2"] or f"?venc.J{f2}?"
        print(f"  J{qf}: {t1} x {t2}  ({c['data']} {c['hora']})")

    if pendentes:
        faltam = ", ".join(f"J{n}" for n in sorted(set(pendentes)))
        print(f"\n⏳ Ainda sem vencedor definido: {faltam}. "
              "Molde NÃO gerado. (Se um deles já jogou e empatou, rode `python "
              "gerar.py` antes pra o robô gravar quem passou nos pênaltis.)")
        return

    print("\n✅ Os 8 vencedores estão definidos — gerando molde + estendendo a mestre:\n")
    pr.preparar(confrontos=confrontos, mestre=mestre)


if __name__ == "__main__":
    main()
