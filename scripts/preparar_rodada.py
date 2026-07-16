"""Parte 1 da rodada: monta o molde com os confrontos E estende a mestre.

Rodada atual = ÚLTIMA (3º LUGAR + FINAL, jogos 103..104), num molde só de 2 jogos.
NORMALMENTE use o `preencher_vencedores` (deriva da mestre os perdedores das semis
para o 3º lugar e os vencedores para a Final, e chama este módulo sozinho). Esta
lista CONFRONTOS é só FALLBACK manual:
1. Preencha os 2 jogos NA ORDEM do chaveamento (nomes em PT, como na planilha):
   J103 = 3º lugar = PERDEDOR de J101 x PERDEDOR de J102;
   J104 = Final    = VENCEDOR de J101 x VENCEDOR de J102.
2. Rode (na raiz do repo):  python -m scripts.preparar_rodada
   -> gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar no grupo);
   -> adiciona os jogos 103..104 na mestre (Resultados + 13 abas, com a fórmula K)
      e estende as somas da aba "Total Pontos".
3. Confira o resumo impresso e depois faça commit/push da mestre.

IMPORTANTE: a ORDEM dos confrontos aqui define o casamento jogo-do-molde <->
jogo-da-mestre (molde 1 = jogo 103 = 3º lugar, molde 2 = jogo 104 = Final). Não
mude a ordem depois de mandar o molde, senão o merge das respostas sai trocado.
"""
import sys

import openpyxl

try:  # no Windows o console é cp1252 e quebra com emoji/acento; força UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from bolao.planilha import adicionar_jogos, estender_somas_total_pontos
from scripts.gerar_molde_mata_mata import gerar_molde, MESTRE_PADRAO, SAIDA_PADRAO

PRIMEIRO_JOGO = 103    # a última rodada (3º lugar + Final) começa no jogo 103
RODADA = "Final"       # rótulo default da coluna GRUPO (cada confronto tem o seu abaixo)
TITULO = "COPA 2026 - APOSTAS MATA-MATA (3º LUGAR + FINAL - 2 JOGOS)"

# >>> 2 confrontos da ÚLTIMA RODADA na ORDEM do chaveamento FIFA (M103..M104) <<<.
# Datas/horas em horário de Brasília (BRT = ET + 1h).
# Chaveamento oficial FIFA 2026:
#   M103 (3º lugar) = PERDEDOR de J101 x PERDEDOR de J102
#   M104 (Final)    = VENCEDOR de J101 x VENCEDOR de J102
# JÁ DEFINIDO (semis encerradas): J101 França 0x2 Espanha, J102 Inglaterra 1x2 Argentina
#   -> Espanha e Argentina à FINAL; França e Inglaterra ao 3º lugar.
# (Fonte principal é o preencher_vencedores; esta lista é só fallback manual.)
CONFRONTOS = [
    dict(rodada="3º Lugar", time1="França",  time2="Inglaterra", data="2026-07-18", hora="18:00"),  # 103 perd.J101 x perd.J102 (1º jogo = PRAZO)
    dict(rodada="Final",    time1="Espanha", time2="Argentina",  data="2026-07-19", hora="16:00"),  # 104 venc.J101 x venc.J102
]


def preparar(confrontos=None, mestre=MESTRE_PADRAO, saida_molde=SAIDA_PADRAO,
             primeiro_jogo=PRIMEIRO_JOGO, rodada=RODADA):
    confrontos = confrontos if confrontos is not None else CONFRONTOS
    if not confrontos:
        raise SystemExit("Preencha a lista CONFRONTOS antes de rodar.")
    pendentes = [c for c in confrontos
                 if "?" in str(c.get("time1")) or "?" in str(c.get("time2"))]
    if pendentes:
        raise SystemExit(
            f"{len(pendentes)} confronto(s) ainda com placeholder '?VENC_Jxx?'. "
            "Troque pelos vencedores reais de J93-96 antes de rodar.")
    confrontos = [{"rodada": rodada, **c} for c in confrontos]

    # 1) molde pronto pra mandar
    caminho = gerar_molde(mestre, saida_molde, titulo=TITULO, confrontos=confrontos)
    print(f"Molde gerado (pronto pra mandar): {caminho}")

    # 2) estende a mestre: jogos primeiro_jogo .. primeiro_jogo+N-1
    wb = openpyxl.load_workbook(mestre)
    jogos = [{"numero": primeiro_jogo + i, **c} for i, c in enumerate(confrontos)]
    adicionar_jogos(wb, jogos)
    somas = estender_somas_total_pontos(wb)
    wb.save(mestre)
    print(f"Mestre estendida: jogos {jogos[0]['numero']}..{jogos[-1]['numero']} "
          f"adicionados; {somas} somas estendidas. Salvo em {mestre}.")
    print("Confira a mestre e depois faça commit/push.")


if __name__ == "__main__":
    preparar()
