"""DOMINGO, parte 1: monta o molde com os 16 confrontos E estende a mestre.

Quando o chaveamento sair (domingo de manhã):
1. Preencha a lista CONFRONTOS abaixo com os 16 jogos NA ORDEM do chaveamento
   (nomes em PT, como na planilha — eu passo a lista pronta).
2. Rode (na raiz do repo):  python -m scripts.preparar_rodada
   -> gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar no grupo);
   -> adiciona os jogos 73..88 na mestre (Resultados + 13 abas, com a fórmula K)
      e estende as somas da aba "Total Pontos".
3. Confira o resumo impresso e depois faça commit/push da mestre.

IMPORTANTE: a ORDEM dos confrontos aqui define o casamento jogo-do-molde <->
jogo-da-mestre (molde 1 = jogo 73, ..., molde 16 = jogo 88). Não mude a ordem
depois de mandar o molde, senão o merge das respostas sai trocado.
"""
import sys

import openpyxl

try:  # no Windows o console é cp1252 e quebra com emoji/acento; força UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from bolao.planilha import adicionar_jogos, estender_somas_total_pontos
from scripts.gerar_molde_mata_mata import gerar_molde, MESTRE_PADRAO, SAIDA_PADRAO

PRIMEIRO_JOGO = 73     # a 1ª rodada do mata-mata começa no jogo 73
RODADA = "R32"         # rótulo que vai na coluna GRUPO

# >>> EDITAR DOMINGO: 16 confrontos na ordem do chaveamento <<<
# Cada item: dict(time1=..., time2=..., data="YYYY-MM-DD", hora="HH:MM")
CONFRONTOS = [
    # dict(time1="México", time2="Canadá", data="2026-06-28", hora="16:00"),
    # ... (16 no total)
]


def preparar(confrontos=None, mestre=MESTRE_PADRAO, saida_molde=SAIDA_PADRAO,
             primeiro_jogo=PRIMEIRO_JOGO, rodada=RODADA):
    confrontos = confrontos if confrontos is not None else CONFRONTOS
    if not confrontos:
        raise SystemExit("Preencha a lista CONFRONTOS antes de rodar.")
    confrontos = [{"rodada": rodada, **c} for c in confrontos]

    # 1) molde pronto pra mandar
    caminho = gerar_molde(mestre, saida_molde, confrontos=confrontos)
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
