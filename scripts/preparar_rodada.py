"""Parte 1 da rodada: monta o molde com os confrontos E estende a mestre.

Rodada atual = QUARTAS DE FINAL (jogos 97..100). O chaveamento fecha quando o
ÚLTIMO jogo das oitavas (J96 Suíça×Colômbia) terminar — terça 07/07 à noite.
1. Preencha a lista CONFRONTOS abaixo com os 4 jogos NA ORDEM do chaveamento
   (nomes em PT, como na planilha). Dois já estão definidos (J97, J99); troque
   os placeholders "?VENC_Jxx?" dos outros dois pelos vencedores reais de J93-96
   (J93/J94 saem hoje 06/07; J95/J96 amanhã 07/07).
2. Rode (na raiz do repo):  python -m scripts.preparar_rodada
   -> gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar no grupo);
   -> adiciona os jogos 97..100 na mestre (Resultados + 13 abas, com a fórmula K)
      e estende as somas da aba "Total Pontos".
3. Confira o resumo impresso e depois faça commit/push da mestre.

IMPORTANTE: a ORDEM dos confrontos aqui define o casamento jogo-do-molde <->
jogo-da-mestre (molde 1 = jogo 97, ..., molde 4 = jogo 100). Não mude a ordem
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

PRIMEIRO_JOGO = 97     # as QUARTAS DE FINAL começam no jogo 97
RODADA = "QF"          # rótulo que vai na coluna GRUPO (quartas de final)
TITULO = "COPA 2026 - APOSTAS MATA-MATA (QUARTAS DE FINAL - 4 JOGOS)"

# >>> 4 confrontos das QUARTAS DE FINAL na ORDEM do chaveamento FIFA (M97..M100)
# <<<. Datas/horas em horário de Brasília (BRT = ET + 1h).
# Chaveamento oficial FIFA 2026 (olympics.com + FOX, batem):
#   M97 = venc.J89 x venc.J90   |   M98 = venc.J93 x venc.J94
#   M99 = venc.J91 x venc.J92   |   M100 = venc.J95 x venc.J96
# JÁ DEFINIDOS (J89-92 encerrados):
#   M97 = França (J89 Paraguai 0x1 França) x Marrocos (J90 Canadá 0x3 Marrocos)
#   M99 = Noruega (J91 Brasil 1x2 Noruega) x Inglaterra (J92 México 2x3 Inglaterra)
# A DEFINIR (o script se recusa a rodar enquanto sobrar algum "?"):
#   M98 = ?VENC_J93? (Portugal ou Espanha) x ?VENC_J94? (EUA ou Bélgica)  [J93/J94 = hoje 06/07]
#   M100 = ?VENC_J95? (Argentina ou Egito) x ?VENC_J96? (Suíça ou Colômbia)  [J95/J96 = amanhã 07/07]
CONFRONTOS = [
    dict(time1="França",     time2="Marrocos",   data="2026-07-09", hora="17:00"),  # 97  v.J89 x v.J90  (1º jogo = PRAZO)
    dict(time1="?VENC_J93?", time2="?VENC_J94?", data="2026-07-10", hora="13:00"),  # 98  v.J93 x v.J94
    dict(time1="Noruega",    time2="Inglaterra", data="2026-07-11", hora="18:00"),  # 99  v.J91 x v.J92
    dict(time1="?VENC_J95?", time2="?VENC_J96?", data="2026-07-11", hora="21:00"),  # 100 v.J95 x v.J96
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
