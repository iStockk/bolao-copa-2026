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

from bolao.modelo import PARTICIPANTES, BONUS, PREMIO, JOGOS_IGNORADOS
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


def _aplicar_resultados(wb, partidas):
    """Casa cada partida (por par de times) com o jogo da planilha e grava
    o placar na ordem time1/time2 da planilha. Retorna nº de jogos novos.
    Uma partida problemática é logada e pulada — nunca aborta as demais."""
    jogos = ler_jogos(wb)
    indice = {frozenset((j.time1, j.time2)): num for num, j in jogos.items()}
    novos = 0
    for t1, t2, g1, g2 in partidas:
        try:
            num = indice.get(frozenset((t1, t2)))
            if num is None:
                print(f"AVISO: jogo {t1} x {t2} não encontrado na planilha", file=sys.stderr)
                continue
            if num in JOGOS_IGNORADOS:
                continue  # jogo fora do bolão (decisão do time) — nunca preencher
            j = jogos[num]
            # Invariante do casamento por par: {t1,t2} == {time1,time2}. Validamos
            # explicitamente para JAMAIS gravar um placar invertido em silêncio.
            if {t1, t2} != {j.time1, j.time2}:
                print(f"AVISO: par {t1} x {t2} não confere com o jogo {num} "
                      f"({j.time1} x {j.time2}); pulando", file=sys.stderr)
                continue
            casa, fora = (g1, g2) if j.time1 == t1 else (g2, g1)
            if escrever_resultado(wb, num, casa, fora):
                novos += 1
                print(f"  + jogo {num}: {j.time1} {casa} x {fora} {j.time2}")
        except Exception as e:  # noqa: BLE001 — uma partida ruim não derruba as outras
            print(f"AVISO: erro ao aplicar {t1} x {t2}: {e}", file=sys.stderr)
    return novos


def _dados_rodada(jogos, resultados, palpites):
    """Resultados do dia mais recente com placar + pontos de cada um nesse dia."""
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
            s += pontos_jogo(pc, pf, rc, rf)
        pontos[disp] = s
    return data, lista, pontos


def _carregar_estado():
    if os.path.exists(ESTADO):
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main(buscar=buscar_partidas_finalizadas):
    agora = datetime.now(TZ_BR)
    wb = openpyxl.load_workbook(ARQUIVO)

    # 1) buscar placares (só a rede fica no try) e gravar (com tratamento por partida)
    partidas = []
    try:
        partidas = buscar(_datas_a_buscar(wb))
    except Exception as e:  # noqa: BLE001 — robustez: regenera com o que já há
        print(f"AVISO: falha ao buscar placares ({e}). Gerando com dados atuais.",
              file=sys.stderr)
    novos = _aplicar_resultados(wb, partidas)
    print(f"{novos} jogo(s) novo(s) gravado(s).")

    # 2) calcular ranking
    jogos = ler_jogos(wb)
    resultados = ler_resultados(wb)
    palpites = {disp: ler_palpites(wb, aba) for disp, aba in PARTICIPANTES}
    ranking = montar_ranking(palpites, resultados, BONUS, ignorar=JOGOS_IGNORADOS)

    # 3) variação vs estado anterior
    ordem_ant = _carregar_estado().get("ordem", [])
    pos_ant = {nome: i for i, nome in enumerate(ordem_ant)}
    variacao = {nome: (pos_ant[nome] - i if nome in pos_ant else None)
                for i, (nome, _) in enumerate(ranking)}

    # 4) dados da rodada mais recente
    data_rodada, resultados_rodada, pontos_rodada = _dados_rodada(jogos, resultados, palpites)

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
    )
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # 7) salvar estado
    with open(ESTADO, "w", encoding="utf-8") as f:
        json.dump({
            "ordem": [nome for nome, _ in ranking],
            "pontos": {nome: pts for nome, pts in ranking},
            "atualizado_em": agora.isoformat(),
        }, f, ensure_ascii=False, indent=2)

    print("Líder:", ranking[0][0], ranking[0][1], "pts |", "site/index.html gerado.")
    return ranking


if __name__ == "__main__":
    main()
