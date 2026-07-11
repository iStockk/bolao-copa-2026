"""Parte 1 da rodada: monta o molde com os confrontos E estende a mestre.

Rodada atual = SEMIFINAIS (jogos 101..102). O chaveamento fecha quando o ÚLTIMO
jogo das quartas (J100 Argentina×Suíça) terminar — sábado 11/07 à noite.
NORMALMENTE use o `preencher_vencedores` (deriva os vencedores das quartas da
mestre e chama este módulo sozinho). Esta lista CONFRONTOS é só FALLBACK manual:
1. Preencha os 2 jogos NA ORDEM do chaveamento (nomes em PT, como na planilha).
   Um já está definido (J101 tem França de venc.J97); troque os placeholders
   "?VENC_Jxx?" pelos vencedores reais de J98-100 (J98 = Espanha ou Bélgica;
   J99/J100 saem 11/07).
2. Rode (na raiz do repo):  python -m scripts.preparar_rodada
   -> gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar no grupo);
   -> adiciona os jogos 101..102 na mestre (Resultados + 13 abas, com a fórmula K)
      e estende as somas da aba "Total Pontos".
3. Confira o resumo impresso e depois faça commit/push da mestre.

IMPORTANTE: a ORDEM dos confrontos aqui define o casamento jogo-do-molde <->
jogo-da-mestre (molde 1 = jogo 101, molde 2 = jogo 102). Não mude a ordem depois
de mandar o molde, senão o merge das respostas sai trocado.
"""
import sys

import openpyxl

try:  # no Windows o console é cp1252 e quebra com emoji/acento; força UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from bolao.planilha import adicionar_jogos, estender_somas_total_pontos
from scripts.gerar_molde_mata_mata import gerar_molde, MESTRE_PADRAO, SAIDA_PADRAO

PRIMEIRO_JOGO = 101    # as SEMIFINAIS começam no jogo 101
RODADA = "SF"          # rótulo que vai na coluna GRUPO (semifinais)
TITULO = "COPA 2026 - APOSTAS MATA-MATA (SEMIFINAIS - 2 JOGOS)"

# >>> 2 confrontos das SEMIFINAIS na ORDEM do chaveamento FIFA (M101..M102) <<<.
# Datas/horas em horário de Brasília (BRT = ET + 1h; ambas 15h ET = 16h BRT).
# Chaveamento oficial FIFA 2026:
#   M101 = venc.J97 x venc.J98   |   M102 = venc.J99 x venc.J100
# JÁ DEFINIDO (J97 encerrado):
#   M101.time1 = França (J97 França 2x0 Marrocos)
# A DEFINIR (o script se recusa a rodar enquanto sobrar algum "?"):
#   M101.time2 = ?VENC_J98? (Espanha ou Bélgica)                     [J98]
#   M102 = ?VENC_J99? (Noruega ou Inglaterra) x ?VENC_J100? (Argentina ou Suíça)  [J99/J100 = 11/07]
# (Fonte principal é o preencher_vencedores; esta lista é só fallback manual.)
CONFRONTOS = [
    dict(time1="França",     time2="?VENC_J98?",  data="2026-07-14", hora="16:00"),  # 101 v.J97 x v.J98  (1º jogo = PRAZO)
    dict(time1="?VENC_J99?", time2="?VENC_J100?", data="2026-07-15", hora="16:00"),  # 102 v.J99 x v.J100
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
