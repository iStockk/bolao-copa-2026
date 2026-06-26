"""Busca placares oficiais no scoreboard público da ESPN (sem chave de API).

Endpoint: site.api.espn.com/.../soccer/fifa.world/scoreboard?dates=YYYYMMDD
Retorna apenas jogos finalizados, com os times já convertidos para PT.
"""
import json
import sys
import time
import urllib.request
from collections import namedtuple

from bolao.nomes import casar_time

# Uma partida finalizada e mapeada para PT.
#   data  : 'YYYY-MM-DD' da fonte (UTC) — usado p/ desambiguar reencontros.
#   avanca: nome PT de quem se classificou QUANDO o jogo foi decidido nos
#           pênaltis (mata-mata); None em jogo normal. O placar (gols1/gols2) é
#           sempre o dos 120min — pênaltis NÃO contam como gols (regra do bolão).
Partida = namedtuple("Partida", "time1 time2 gols1 gols2 data avanca")

ESPN_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/"
    "fifa.world/scoreboard?dates={}"
)


def _baixar(data_yyyymmdd, tentativas=3):
    url = ESPN_URL.format(data_yyyymmdd)
    req = urllib.request.Request(url, headers={"User-Agent": "bolao-copa-2026"})
    erro = None
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 — tenta de novo com backoff
            erro = e
            if i < tentativas - 1:
                time.sleep(2 ** i)
    raise erro


def _gols(c):
    try:
        return int(c.get("score"))
    except (TypeError, ValueError):
        return None


def _avanca_pt(comp):
    """Nome PT de quem passou se o jogo foi decidido nos PÊNALTIS; senão None.

    A ESPN marca pênaltis com status.type.name == 'STATUS_FINAL_PEN' e sinaliza
    o classificado com competitor.winner == True (o score continua sendo o dos
    120min). Em jogo decidido em campo, o sinal V/E/D já cobre o resultado, então
    retornamos None (não precisa do 'avanca')."""
    stype = (comp.get("status") or {}).get("type") or {}
    if stype.get("name") != "STATUS_FINAL_PEN":
        return None
    for c in comp.get("competitors", []):
        if c.get("winner"):
            return casar_time((c.get("team") or {}).get("displayName"))
    return None


def parse_eventos(payload):
    """Extrai partidas de um payload da ESPN.

    Retorna lista de dicts com a ordem home/away da fonte:
      {time1, gols1, time2, gols2, time1_pt, time2_pt, completo, data, avanca}
    (time*_pt = nome PT da planilha ou None se não mapeado; avanca = nome PT de
    quem passou nos pênaltis ou None; data = 'YYYY-MM-DD' da fonte.)
    """
    partidas = []
    for ev in payload.get("events", []):
        comps = ev.get("competitions") or []
        if not comps:
            continue
        comp = comps[0]
        completo = bool(comp.get("status", {}).get("type", {}).get("completed"))
        home = away = None
        for c in comp.get("competitors", []):
            nome = (c.get("team") or {}).get("displayName")
            if c.get("homeAway") == "home":
                home = (nome, _gols(c))
            elif c.get("homeAway") == "away":
                away = (nome, _gols(c))
        if not home or not away:
            continue
        partidas.append({
            "time1": home[0], "gols1": home[1],
            "time2": away[0], "gols2": away[1],
            "time1_pt": casar_time(home[0]),
            "time2_pt": casar_time(away[0]),
            "completo": completo,
            "data": (ev.get("date") or "")[:10],
            "avanca": _avanca_pt(comp),
        })
    return partidas


def buscar_partidas_finalizadas(datas, baixar=_baixar):
    """Lista de `Partida` (time1, time2, gols1, gols2, data, avanca) de jogos
    FINALIZADOS e mapeados.

    `datas`: iterável de strings 'YYYYMMDD'. `baixar`: função injetável (testes).
    Times não reconhecidos são logados em stderr (nunca silenciados).
    """
    out = []
    nao_mapeados = set()
    for d in datas:
        try:
            payload = baixar(d)
        except Exception as e:  # noqa: BLE001 — uma data com falha não perde as outras
            print(f"AVISO: falha ao buscar data {d}: {e}", file=sys.stderr)
            continue
        for p in parse_eventos(payload):
            if not p["completo"]:
                continue
            if p["time1_pt"] is None:
                nao_mapeados.add(p["time1"])
            if p["time2_pt"] is None:
                nao_mapeados.add(p["time2"])
            if (p["time1_pt"] and p["time2_pt"]
                    and p["gols1"] is not None and p["gols2"] is not None):
                out.append(Partida(p["time1_pt"], p["time2_pt"], p["gols1"],
                                   p["gols2"], p["data"], p["avanca"]))
    if nao_mapeados:
        print(f"AVISO: times não mapeados da fonte: {sorted(nao_mapeados)}",
              file=sys.stderr)
    return out
