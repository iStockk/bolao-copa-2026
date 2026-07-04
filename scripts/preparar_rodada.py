"""Parte 1 da rodada: monta o molde com os confrontos E estende a mestre.

Quando o chaveamento sair (rodada atual = OITAVAS, sexta 03/07 à noite):
1. Preencha a lista CONFRONTOS abaixo com os 8 jogos NA ORDEM do chaveamento
   (nomes em PT, como na planilha — eu passo a lista pronta). Troque os
   placeholders "?VENC_Jxx?" pelos vencedores reais de J81-88.
2. Rode (na raiz do repo):  python -m scripts.preparar_rodada
   -> gera APOSTAS_MATA-MATA_COPA_2026.xlsx (pronto pra mandar no grupo);
   -> adiciona os jogos 89..96 na mestre (Resultados + 13 abas, com a fórmula K)
      e estende as somas da aba "Total Pontos".
3. Confira o resumo impresso e depois faça commit/push da mestre.

IMPORTANTE: a ORDEM dos confrontos aqui define o casamento jogo-do-molde <->
jogo-da-mestre (molde 1 = jogo 89, ..., molde 8 = jogo 96). Não mude a ordem
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

PRIMEIRO_JOGO = 89     # as OITAVAS DE FINAL começam no jogo 89
RODADA = "R16"         # rótulo que vai na coluna GRUPO (oitavas de final)
TITULO = "COPA 2026 - APOSTAS MATA-MATA (OITAVAS DE FINAL - 8 JOGOS)"

# >>> 8 confrontos das OITAVAS DE FINAL (Round of 16) na ORDEM do chaveamento
# FIFA (M89..M96) <<<. Datas/horas em horário de Brasília (BRT = ET + 1h).
# Chaveamento oficial (Wikipedia + ESPN, batem):
#   M89 = venc.J74 x venc.J77   |   M90 = venc.J73 x venc.J75
#   M91 = venc.J76 x venc.J78   |   M92 = venc.J79 x venc.J80
#   M93 = venc.J83 x venc.J84   |   M94 = venc.J81 x venc.J82
#   M95 = venc.J86 x venc.J88   |   M96 = venc.J85 x venc.J87
# JÁ DEFINIDOS (J73-80 encerrados): 89, 90, 91, 92.
# A DEFINIR na sexta 03/07 à noite: trocar os "?VENC_Jxx?" pelos vencedores
# reais (o script se recusa a rodar enquanto sobrar algum "?").
CONFRONTOS = [
    dict(time1="Paraguai",   time2="França",     data="2026-07-04", hora="18:00"),  # 89  v.J74 x v.J77
    dict(time1="Canadá",     time2="Marrocos",   data="2026-07-04", hora="14:00"),  # 90  v.J73 x v.J75  (1º jogo = PRAZO)
    dict(time1="Brasil",     time2="Noruega",    data="2026-07-05", hora="17:00"),  # 91  v.J76 x v.J78
    dict(time1="México",     time2="Inglaterra", data="2026-07-05", hora="21:00"),  # 92  v.J79 x v.J80
    dict(time1="Portugal",   time2="Espanha",    data="2026-07-06", hora="16:00"),  # 93  v.J83 (Portugal 2x1 Croácia) x v.J84 (Espanha 3x0 Áustria)
    dict(time1="EUA",        time2="Bélgica",    data="2026-07-06", hora="21:00"),  # 94  v.J81 (EUA 2x0 Bósnia) x v.J82 (Bélgica 3x2 Senegal)  [horário conferir: ESPN=18:00]
    dict(time1="Argentina",  time2="Egito",      data="2026-07-07", hora="13:00"),  # 95  v.J86 (Argentina 3x2 Cabo Verde AET) x v.J88 (Egito pên. s/ Austrália)
    dict(time1="Suíça",      time2="Colômbia",   data="2026-07-07", hora="17:00"),  # 96  v.J85 (Suíça 2x0 Argélia) x v.J87 (Colômbia 1x0 Gana)
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
            "Troque pelos vencedores reais de J81-88 antes de rodar.")
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
