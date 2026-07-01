"""Leitura e escrita da planilha do bolão (openpyxl).

Layout: jogo N na linha N+4 (jogo 1 -> linha 5). Colunas:
  A(1)=nº  B(2)=grupo/rodada  C(3)=time1  D(4)=gols1  E(5)="X"  F(6)=gols2
  G(7)=time2  H(8)=data  I(9)=data(=H)  J(10)=hora  K(11)=pontos
A aba "Resultados" guarda o placar oficial; cada aba de participante guarda o palpite (D/F).
A aba "Total Pontos" tem a tabela de classificação em D12:E24.
"""
import datetime as _dt
import re

from bolao.modelo import (
    PARTICIPANTES, BONUS, PRIMEIRA_LINHA, ULTIMA_LINHA, Jogo,
)
from bolao.pontuacao import pontos_jogo

ABA_RESULTADOS = "Resultados"
ABA_TOTAL = "Total Pontos"
COL = {"num": 1, "grupo": 2, "time1": 3, "gols1": 4, "gols2": 6, "time2": 7,
       "data": 8, "hora": 10}
COL_SEP = 5   # E = "X" entre os gols
COL_DATA2 = 9  # I = "=H{linha}"
COL_PONTOS = 11  # K = fórmula de pontos do jogo
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


def _k_formula(r):
    """Fórmula da coluna K (pontos do jogo na linha r) — idêntica às da fase de
    grupos. Compara o palpite (D/F) com o oficial (Resultados!D/F): +2 acerto do
    resultado V/E/D, +1 gols1, +1 gols2, +1 total. (No mata-mata os pênaltis são
    tratados no motor Python; ver NOTA em adicionar_jogos.)"""
    return (
        f"=IF(AND(ISNUMBER(D{r}),ISNUMBER(F{r}),ISNUMBER(Resultados!D{r}),"
        f"ISNUMBER(Resultados!F{r})),"
        f"IF(SIGN(D{r}-F{r})=SIGN(Resultados!D{r}-Resultados!F{r}),2,0)"
        f"+IF(D{r}=Resultados!D{r},1,0)"
        f"+IF(F{r}=Resultados!F{r},1,0)"
        f"+IF(D{r}+F{r}=Resultados!D{r}+Resultados!F{r},1,0),0)"
    )


def _escrever_cabecalho_jogo(ws, r, j):
    """Escreve nº/rodada/times/data/hora de um jogo na linha r (sem placar)."""
    ws.cell(r, COL["num"]).value = j["numero"]
    ws.cell(r, COL["grupo"]).value = j.get("rodada", "")
    ws.cell(r, COL["time1"]).value = j["time1"]
    ws.cell(r, COL_SEP).value = "X"
    ws.cell(r, COL["time2"]).value = j["time2"]
    ws.cell(r, COL["data"]).value = j["data"]
    ws.cell(r, COL_DATA2).value = f"=H{r}"
    ws.cell(r, COL["hora"]).value = j["hora"]


def adicionar_jogos(wb, jogos):
    """Adiciona linhas de jogos (mata-mata) na aba Resultados e em cada aba de
    participante presente, replicando a fórmula K. NÃO preenche placar nem
    palpite (D/F): o placar oficial vem do robô (Resultados) e os palpites do
    merge do form (abas). Sobrescreve a linha — re-rodar é seguro.

    jogos: lista de dicts {numero, rodada, time1, time2, data, hora}, com
    `data` em 'YYYY-MM-DD'.

    NOTA (pênaltis): a fórmula K do Excel usa só o sinal V/E/D e não sabe quem
    passou nos pênaltis. Por isso, nos jogos decididos nos pênaltis, o robô
    SOBRESCREVE a K com o VALOR exato do motor Python (ver
    `fixar_pontos_penaltis`, chamada em gerar.py antes de salvar) — assim o
    Excel (célula e somas) bate com o site. A classificação publicada vem sempre
    do motor Python (pontuacao.pontos_jogo com `avanca`).
    """
    abas_part = [aba for _disp, aba in PARTICIPANTES if aba in wb.sheetnames]
    for j in jogos:
        r = _linha(j["numero"])
        _escrever_cabecalho_jogo(wb[ABA_RESULTADOS], r, j)  # Resultados não tem K
        for aba in abas_part:
            ws = wb[aba]
            _escrever_cabecalho_jogo(ws, r, j)
            ws.cell(r, COL_PONTOS).value = _k_formula(r)


def estender_somas_total_pontos(wb):
    """Estende toda fórmula =SUM(...K5:K<n>...) da aba Total Pontos até o cap
    atual (ULTIMA_LINHA), para as somas do Excel contarem também os jogos do
    mata-mata. Cobre a tabela horizontal (linha 6) e a vertical (D12:E24).
    Idempotente. Retorna o nº de células alteradas."""
    ws = wb[ABA_TOTAL]
    alvo = f"K5:K{ULTIMA_LINHA}"
    alteradas = 0
    for row in ws.iter_rows():
        for cell in row:
            v = cell.value
            if isinstance(v, str) and "K5:K" in v:
                novo = re.sub(r"K5:K\d+", alvo, v)
                if novo != v:
                    cell.value = novo
                    alteradas += 1
    return alteradas


def reordenar_classificacao(wb, ranking):
    """Reescreve a tabela de classificação (D12:E24) na ordem do ranking,
    preservando as fórmulas =SUM('aba'!K5:K{cap})[+bonus] (Excel recalcula ao
    abrir). A faixa vai até ULTIMA_LINHA p/ cobrir também os jogos do mata-mata."""
    ws = wb[ABA_TOTAL]
    aba_por_nome = dict(PARTICIPANTES)
    for i, (nome, _pts) in enumerate(ranking):
        r = RANKING_PRIMEIRA_LINHA + i
        aba = aba_por_nome[nome]
        bonus = BONUS.get(nome, 0)
        formula = f"=SUM('{aba}'!K5:K{ULTIMA_LINHA})" + (f"+{bonus}" if bonus else "")
        ws.cell(r, 4).value = nome
        ws.cell(r, 5).value = formula


def fixar_pontos_penaltis(wb, palpites, resultados, avancos):
    """Sobrescreve a coluna K (com VALOR, não fórmula) dos jogos decididos nos
    pênaltis, para o Excel bater com o site.

    A fórmula K usa só o sinal V/E/D e não sabe quem passou nos pênaltis; aqui
    gravamos o ponto exato do motor Python (`pontos_jogo` com `avanca`), de modo
    que também a soma do Excel fique correta nesses jogos. Idempotente — o robô
    reescreve a cada run. Só toca jogos com placar e avanço conhecidos.

    palpites: {disp: {num: (g1, g2)}}; resultados: {num: (rc, rf)};
    avancos: {num: 1|2}. Retorna o nº de células gravadas.
    """
    gravadas = 0
    for num, avanca in (avancos or {}).items():
        rc, rf = resultados.get(num, (None, None))
        if rc is None or rf is None:
            continue
        r = _linha(num)
        for disp, aba in PARTICIPANTES:
            if aba not in wb.sheetnames:
                continue
            pc, pf = palpites.get(disp, {}).get(num, (None, None))
            wb[aba].cell(r, COL_PONTOS).value = pontos_jogo(pc, pf, rc, rf, avanca=avanca)
            gravadas += 1
    return gravadas
