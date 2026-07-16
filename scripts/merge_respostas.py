"""Parte 2 da rodada (depois do apito do 1º jogo): merge dos .xlsx na mestre.

Última rodada (3º lugar + Final): o 1º jogo (M103, 3º lugar) é sábado 18/07 às
18h (BRT) = PRAZO. Cada participante devolve o arquivo; o Caio renomeia com o
nome no fim (ex.: "APOSTAS_MATA-MATA_COPA_2026 Kim.xlsx") e joga na pasta
"planilha respostas final/". Então, na raiz do repo:

    python -m scripts.merge_respostas

Lê todos os .xlsx da pasta, grava os palpites nas abas da mestre e imprime um
resumo: quem entrou (e quantos jogos), quem ainda FALTA, e arquivos cujo nome
não foi reconhecido. Depois: conferir e commitar/pushar a mestre (o robô segue
sozinho a partir daí).
"""
import glob
import os
import sys

import openpyxl

try:  # no Windows o console é cp1252 e quebra com emoji/acento; força UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from bolao.modelo import PARTICIPANTES
from bolao.respostas_planilha import merge_arquivos
from scripts.gerar_molde_mata_mata import MESTRE_PADRAO

PASTA_RESPOSTAS = "planilha respostas final"   # respostas da última rodada (semis usaram "planilha respostas semis")
PRIMEIRO_JOGO = 103    # última rodada (3º lugar + Final) = jogos 103..104


def main(pasta=PASTA_RESPOSTAS, mestre=MESTRE_PADRAO, primeiro_jogo=PRIMEIRO_JOGO):
    arquivos = sorted(
        f for f in glob.glob(os.path.join(pasta, "*.xlsx"))
        if not os.path.basename(f).startswith("~$")  # temporários do Excel aberto
    )
    if not arquivos:
        raise SystemExit(f"Nenhum .xlsx em '{pasta}'.")
    print(f"{len(arquivos)} arquivo(s) em '{pasta}'.")

    wb = openpyxl.load_workbook(mestre)
    gravados, sem_dono = merge_arquivos(wb, arquivos, primeiro_jogo=primeiro_jogo)
    wb.save(mestre)

    print("\nMerge feito na mestre:")
    for aba, n in sorted(gravados.items()):
        print(f"  {aba.strip()}: {n} jogos")

    faltando = [disp for disp, aba in PARTICIPANTES if aba not in gravados]
    if faltando:
        print(f"\n⚠️ AINDA SEM palpite: {', '.join(faltando)} "
              f"(pela regra, quem não enviar no prazo zera a rodada).")
    if sem_dono:
        print("\n⚠️ Nome do arquivo NÃO reconhecido (renomeie com o nome no fim):")
        for f in sem_dono:
            print(f"  {os.path.basename(f)}")
    print(f"\nSalvo em {mestre}. Confira e faça commit/push.")


if __name__ == "__main__":
    main()
