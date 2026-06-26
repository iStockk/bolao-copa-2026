"""Orquestrador do bolão.

Fluxo: busca placares na ESPN -> grava na planilha (sem sobrescrever) ->
calcula ranking/variação/pontos da rodada -> reordena a classificação na
planilha -> gera site/index.html -> salva estado.json.

Uso: python gerar.py
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import openpyxl

from bolao.modelo import (
    PARTICIPANTES, BONUS, PREMIO, JOGOS_IGNORADOS, ULTIMO_JOGO_GRUPOS,
)
from bolao.planilha import (
    ler_jogos, ler_palpites, ler_resultados, escrever_resultado,
    reordenar_classificacao,
)
from bolao.pontuacao import montar_ranking, pontos_jogo
from bolao.fetcher import buscar_partidas_finalizadas
from bolao.render import render_pagina

ARQUIVO = "TABELA_APOSTAS_-_COPA_2026.xlsx"
SITE_DIR = "site"
ESTADO = "estado.json"
TZ_BR = timezone(timedelta(hours=-3))


def _datas_a_buscar(wb):
    """Datas YYYYMMDD a consultar. Inclui:
    - a janela recente (anteontem..hoje em UTC);
    - a data de TODO jogo ainda sem placar, e o dia seguinte (auto-recuperação +
      cobertura do fuso: jogos de 22h BRT caem no dia seguinte em UTC).
    Buscar datas extras é inofensivo: nunca sobrescreve placar e ignora não-finalizados."""
    jogos = ler_jogos(wb)
    resultados = ler_resultados(wb)
    datas = set()
    for num, j in jogos.items():
        if num in JOGOS_IGNORADOS:
            continue
        rc, rf = resultados[num]
        if rc is None or rf is None:
            try:
                d = datetime.strptime(j.data, "%Y-%m-%d").date()
                datas.add(d.strftime("%Y%m%d"))
                datas.add((d + timedelta(days=1)).strftime("%Y%m%d"))
            except (ValueError, TypeError):
                pass
    hoje = datetime.now(timezone.utc).date()
    for k in (2, 1, 0):
        datas.add((hoje - timedelta(days=k)).strftime("%Y%m%d"))
    return sorted(datas)


def _br_data(iso):
    a, m, d = iso.split("-")
    return f"{d}/{m}"


def _dist_dias(d1, d2):
    """Distância em dias entre duas datas 'YYYY-MM-DD' (grande se alguma inválida)."""
    try:
        a = datetime.strptime(d1, "%Y-%m-%d").date()
        b = datetime.strptime(d2, "%Y-%m-%d").date()
        return abs((a - b).days)
    except (ValueError, TypeError):
        return 10 ** 6


def casar_partidas(jogos, partidas):
    """Casa cada Partida a um jogo da planilha pelo PAR de times.

    Quando o mesmo par aparece em mais de um jogo (reencontro grupos x mata-mata),
    desempata pela proximidade de data. Casar por par garante a invariante
    {time1,time2} == par, então o placar é reorientado para a ordem da planilha
    sem risco de inverter em silêncio.

    Retorna (casados, nao_encontradas):
      casados[num] = (casa, fora, avanca) — gols na orientação time1/time2 da
        planilha; avanca = 1|2 (quem passou nos pênaltis) ou None.
      nao_encontradas = lista de Partida cujo par não existe na planilha.
    """
    por_par = {}
    for num, j in jogos.items():
        por_par.setdefault(frozenset((j.time1, j.time2)), []).append((num, j))
    casados = {}
    nao_encontradas = []
    for p in partidas:
        cands = por_par.get(frozenset((p.time1, p.time2)))
        if not cands:
            nao_encontradas.append(p)
            continue
        num, j = (cands[0] if len(cands) == 1
                  else min(cands, key=lambda c: _dist_dias(c[1].data, p.data)))
        casa, fora = (p.gols1, p.gols2) if j.time1 == p.time1 else (p.gols2, p.gols1)
        avanca = 1 if p.avanca == j.time1 else (2 if p.avanca == j.time2 else None)
        casados[num] = (casa, fora, avanca)
    return casados, nao_encontradas


def _aplicar_resultados(wb, partidas):
    """Grava os placares casados na aba Resultados (sem sobrescrever) e devolve
    (novos, avancos): nº de jogos novos e {num: 1|2} dos jogos de pênaltis.
    Uma partida problemática é logada e pulada — nunca aborta as demais."""
    jogos = ler_jogos(wb)
    casados, nao_encontradas = casar_partidas(jogos, partidas)
    for p in nao_encontradas:
        print(f"AVISO: jogo {p.time1} x {p.time2} não encontrado na planilha",
              file=sys.stderr)
    novos = 0
    avancos = {}
    for num, (casa, fora, avanca) in casados.items():
        try:
            if num in JOGOS_IGNORADOS:
                continue  # jogo fora do bolão (decisão do time) — nunca preencher
            j = jogos[num]
            if escrever_resultado(wb, num, casa, fora):
                novos += 1
                print(f"  + jogo {num}: {j.time1} {casa} x {fora} {j.time2}")
            if avanca is not None:
                avancos[num] = avanca  # persiste mesmo se o placar já existia
        except Exception as e:  # noqa: BLE001 — uma partida ruim não derruba as outras
            print(f"AVISO: erro ao aplicar jogo {num}: {e}", file=sys.stderr)
    return novos, avancos


def _merge_avancos(prev, novos):
    """Une os avanços persistidos no estado.json (chaves viram string no JSON)
    com os detectados nesta run (chaves int). Detecção nova tem prioridade."""
    out = {}
    for k, v in (prev or {}).items():
        try:
            out[int(k)] = v
        except (ValueError, TypeError):
            pass
    out.update(novos or {})
    return out


def _fase_atual(resultados):
    """Rótulo da fase para o site: "Mata-mata" assim que algum jogo acima do
    último da fase de grupos tiver placar; senão "Fase de Grupos"."""
    for num, (rc, rf) in resultados.items():
        if num > ULTIMO_JOGO_GRUPOS and rc is not None and rf is not None:
            return "Mata-mata"
    return "Fase de Grupos"


def _dados_rodada(jogos, resultados, palpites, avancos=None):
    """Resultados do dia mais recente com placar + pontos de cada um nesse dia."""
    avancos = avancos or {}
    por_data = {}
    for num, j in jogos.items():
        if num in JOGOS_IGNORADOS:
            continue
        rc, rf = resultados[num]
        if rc is not None and rf is not None:
            por_data.setdefault(j.data, []).append(num)
    if not por_data:
        return None, [], {}
    data = max(por_data)
    nums = sorted(por_data[data])
    # (time1, g1, g2, time2) para cada jogo do dia
    lista = [(jogos[n].time1, resultados[n][0], resultados[n][1], jogos[n].time2) for n in nums]
    pontos = {}
    for disp, _aba in PARTICIPANTES:
        pal = palpites[disp]
        s = 0
        for n in nums:
            rc, rf = resultados[n]
            pc, pf = pal.get(n, (None, None))
            s += pontos_jogo(pc, pf, rc, rf, avanca=avancos.get(n))
        pontos[disp] = s
    return data, lista, pontos


def _carregar_estado():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def calcular_variacao(ranking, estado_ant):
    """Setas de posição vs a última ordem ESTÁVEL (não vs o run anterior).

    O robô roda várias vezes por dia; se comparássemos com o run anterior, runs
    sem jogos novos zerariam tudo pra '–'. Aqui o baseline só avança quando a
    classificação muda, então as setas persistem e refletem o movimento desde a
    última mexida.

    ranking: list[(nome, pts)] já ordenado. estado_ant: dict do estado.json (ou {}).
    Retorna (variacao, ordem_atual, ordem_baseline):
      variacao[nome] = +n subiu | -n caiu | 0 igual | None sem histórico.
    """
    ordem_atual = [nome for nome, _ in ranking]
    ordem_prev = estado_ant.get("ordem", [])               # "atual" do run anterior
    ordem_baseline = estado_ant.get("ordem_anterior", [])  # baseline congelado
    if ordem_atual != ordem_prev:
        # a classificação mudou → baseline passa a ser a última ordem estável
        ordem_baseline = ordem_prev
    pos_base = {nome: i for i, nome in enumerate(ordem_baseline)}
    variacao = {nome: (pos_base[nome] - i if nome in pos_base else None)
                for i, (nome, _) in enumerate(ranking)}
    return variacao, ordem_atual, ordem_baseline


def main(buscar=buscar_partidas_finalizadas):
    agora = datetime.now(TZ_BR)
    estado_ant = _carregar_estado()
    wb = openpyxl.load_workbook(ARQUIVO)

    # 1) buscar placares (só a rede fica no try) e gravar (com tratamento por partida)
    partidas = []
    try:
        partidas = buscar(_datas_a_buscar(wb))
    except Exception as e:  # noqa: BLE001 — robustez: regenera com o que já há
        print(f"AVISO: falha ao buscar placares ({e}). Gerando com dados atuais.",
              file=sys.stderr)
    novos, avancos_novos = _aplicar_resultados(wb, partidas)
    print(f"{novos} jogo(s) novo(s) gravado(s).")

    # avanços nos pênaltis: une o que já estava no estado com o detectado agora.
    # A fonte (ESPN) só expõe o classificado por alguns dias; persistir garante
    # que o +2 do mata-mata siga correto mesmo quando o jogo sai da janela de busca.
    avancos = _merge_avancos(estado_ant.get("avancos"), avancos_novos)

    # 2) calcular ranking
    jogos = ler_jogos(wb)
    resultados = ler_resultados(wb)
    palpites = {disp: ler_palpites(wb, aba) for disp, aba in PARTICIPANTES}
    ranking = montar_ranking(palpites, resultados, BONUS,
                             ignorar=JOGOS_IGNORADOS, avancos=avancos)

    # 3) variação vs a última ordem estável (baseline congelado entre runs no-op)
    variacao, ordem_atual, ordem_baseline = calcular_variacao(ranking, estado_ant)

    # 4) dados da rodada mais recente
    data_rodada, resultados_rodada, pontos_rodada = _dados_rodada(
        jogos, resultados, palpites, avancos)

    # 5) reordenar a classificação na planilha e salvar
    reordenar_classificacao(wb, ranking)
    wb.save(ARQUIVO)

    # 6) gerar página
    os.makedirs(SITE_DIR, exist_ok=True)
    html = render_pagina(
        ranking,
        variacao=variacao,
        resultados_rodada=resultados_rodada,
        pontos_rodada=pontos_rodada,
        premio=PREMIO,
        atualizado_em=agora.strftime("%d/%m/%Y às %H:%M"),
        data_rodada=_br_data(data_rodada) if data_rodada else "",
        fase=_fase_atual(resultados),
    )
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # 7) salvar estado
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump({
            "ordem": ordem_atual,
            "ordem_anterior": ordem_baseline,  # baseline p/ as setas persistirem
            "pontos": {nome: pts for nome, pts in ranking},
            "avancos": {str(k): v for k, v in avancos.items()},  # pênaltis (mata-mata)
            "atualizado_em": agora.isoformat(),
        }, f, ensure_ascii=False, indent=2)

    print("Líder:", ranking[0][0], ranking[0][1], "pts |", "site/index.html gerado.")
    return ranking


if __name__ == "__main__":
    main()
