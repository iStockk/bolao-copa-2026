import json
import os

from bolao.fetcher import parse_eventos, buscar_partidas_finalizadas

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "espn_20260624.json")


def _payload():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def test_buscar_da_fixture_retorna_jogos_de_24jun():
    res = buscar_partidas_finalizadas(["20260624"], baixar=lambda d: _payload())
    # ESPN dá Escócia como mandante; placar Escócia 0 x 3 Brasil
    assert ("Escócia", "Brasil", 0, 3) in res
    assert ("Suíça", "Canadá", 2, 1) in res
    assert ("Bósnia", "Catar", 3, 1) in res
    # todos os 6 jogos da fixture estão finalizados
    assert len(res) == 6


def test_todos_os_times_da_fixture_mapeiam():
    for p in parse_eventos(_payload()):
        assert p["time1_pt"] is not None, p["time1"]
        assert p["time2_pt"] is not None, p["time2"]


def test_ignora_jogo_nao_finalizado():
    payload = {"events": [{"competitions": [{
        "status": {"type": {"completed": False}},
        "competitors": [
            {"homeAway": "home", "score": "1", "team": {"displayName": "Brazil"}},
            {"homeAway": "away", "score": "0", "team": {"displayName": "Scotland"}},
        ],
    }]}]}
    assert buscar_partidas_finalizadas(["x"], baixar=lambda d: payload) == []


def test_ignora_time_nao_mapeado():
    payload = {"events": [{"competitions": [{
        "status": {"type": {"completed": True}},
        "competitors": [
            {"homeAway": "home", "score": "1", "team": {"displayName": "Atlantis"}},
            {"homeAway": "away", "score": "0", "team": {"displayName": "Brazil"}},
        ],
    }]}]}
    assert buscar_partidas_finalizadas(["x"], baixar=lambda d: payload) == []
