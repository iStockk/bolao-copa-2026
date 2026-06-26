"""Leitura e escrita da planilha do bolão (openpyxl).

Layout: jogos 1..72 nas linhas 5..76. Colunas:
  A(1)=nº  B(2)=grupo  C(3)=time1  D(4)=gols1  E(5)="X"  F(6)=gols2
  G(7)=time2  H(8)=data  I(9)=data  J(10)=hora  K(11)=pontos
A aba "Resultados" guarda o placar oficial; cada aba de participante guarda o palpite (D/F).
A aba "Total Pontos" tem a tabela de classificação em D12:E24.
"""
import datetime as _dt

from bolao.modelo import (
    PARTICIPANTES, BONUS, PRIMEIRA_LINHA, ULTIMA_LINHA, Jogo,
)

ABA_RESULTADOS = "Resultados"
ABA_TOTAL = "Total Pontos"
COL = {"num": 1, "grupo": 2, "time1": 3, "gols1": 4, "gols2": 6, "time2": 7,
       "data": 8, "hora": 10}
RANKING_PRIMEIRA_LINHA = 12  # D12:E24


def _linha(num):
    return num + 4  # jogo 1 -> linha 5


def _nums():
    return range(1, ULTIMA_LINHA - PRIMEIRA_LINHA + 2)  # 1..72


def _fmt_data(v):
    if isinstance(v, (_dt.datetime, _dt.date)):
        return v.strftime("%Y-%m-%d")
    return str(v) if v is not None else ""


def _fmt_hora(v):
    if isinstance(v, _dt.time):
        return v.strftime("%H:%M")
    if isinstance(v, _dt.datetime):
        return v.strftime("%H:%M")
    return str(v) if v is not None else ""


def ler_jogos(wb):
    """dict {num: Jogo} a partir da aba Resultados."""
    ws = wb[ABA_RESULTADOS]
    jogos = {}
    for num in _nums():
        r = _linha(num)
        t1 = ws.cell(r, COL["time1"]).value
        t2 = ws.cell(r, COL["time2"]).value
        if t1 is None or t2 is None:
            continue
        jogos[num] = Jogo(
            numero=num,
            grupo=ws.cell(r, COL["grupo"]).value,
            time1=t1,
            time2=t2,
            data=_fmt_data(ws.cell(r, COL["data"]).value),
            hora=_fmt_hora(ws.cell(r, COL["hora"]).value),
        )
    return jogos


def _ler_placar(ws):
    placar = {}
    for num in _nums():
        r = _linha(num)
        placar[num] = (ws.cell(r, COL["gols1"]).value, ws.cell(r, COL["gols2"]).value)
    return placar


def ler_palpites(wb, aba):
    """dict {num: (gols1, gols2)} de uma aba de participante."""
    return _ler_placar(wb[aba])


def ler_resultados(wb):
    """dict {num: (gols1, gols2) | (None, None)} da aba Resultados."""
    return _ler_placar(wb[ABA_RESULTADOS])


def escrever_resultado(wb, num, casa, fora):
    """Escreve o placar de um jogo na aba Resultados, SÓ se ainda estiver vazio.

    Retorna True se escreveu, False se já havia placar (não sobrescreve).
    """
    ws = wb[ABA_RESULTADOS]
    r = _linha(num)
    if ws.cell(r, COL["gols1"]).value is None and ws.cell(r, COL["gols2"]).value is None:
        ws.cell(r, COL["gols1"]).value = casa
        ws.cell(r, COL["gols2"]).value = fora
        return True
    return False


def escrever_palpites(wb, aba, palpites):
    """Grava os palpites de um participante na aba dele (cols D=gols1, F=gols2).

    palpites: dict {num_jogo: (gols1, gols2)}. Usado no merge das respostas do
    Google Forms (mata-mata). Sobrescreve o que estiver lá (re-merge é seguro).
    """
    ws = wb[aba]
    for num, (g1, g2) in palpites.items():
        r = _linha(num)
        ws.cell(r, COL["gols1"]).value = g1
        ws.cell(r, COL["gols2"]).value = g2


def reordenar_classificacao(wb, ranking):
    """Reescreve a tabela de classificação (D12:E24) na ordem do ranking,
    preservando as fórmulas =SUM('aba'!K5:K76)[+bonus] (Excel recalcula ao abrir)."""
    ws = wb[ABA_TOTAL]
    aba_por_nome = dict(PARTICIPANTES)
    for i, (nome, _pts) in enumerate(ranking):
        r = RANKING_PRIMEIRA_LINHA + i
        aba = aba_por_nome[nome]
        bonus = BONUS.get(nome, 0)
        formula = f"=SUM('{aba}'!K5:K76)" + (f"+{bonus}" if bonus else "")
        ws.cell(r, 4).value = nome
        ws.cell(r, 5).value = formula
