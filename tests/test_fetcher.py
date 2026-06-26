import json
import os

from bolao.fetcher import parse_eventos, buscar_partidas_finalizadas

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "espn_20260624.json")


def _payload():
    with open(FIXTURE, encoding="utf-8") as f:
        return json.load(f)


def _pares(res):
    return {(p.time1, p.time2, p.gols1, p.gols2) for p in res}


def test_buscar_da_fixture_retorna_jogos_de_24jun():
    res = buscar_partidas_finalizadas(["20260624"], baixar=lambda d: _payload())
    pares = _pares(res)
    # ESPN dá Escócia como mandante; placar Escócia 0 x 3 Brasil
    assert ("Escócia", "Brasil", 0, 3) in pares
    assert ("Suíça", "Canadá", 2, 1) in pares
    assert ("Bósnia", "Catar", 3, 1) in pares
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


# --- Fase 2 (mata-mata): pênaltis e data ---

def _payload_penaltis():
    """Jogo decidido nos pênaltis: 1x1 nos 120min, Croácia passa (winner=True)."""
    return {"events": [{
        "date": "2026-07-05T19:00Z",
        "competitions": [{
            "status": {"type": {"completed": True, "name": "STATUS_FINAL_PEN",
                                 "detail": "FT-Pens"}},
            "competitors": [
                {"homeAway": "home", "score": "1", "shootoutScore": 4,
                 "winner": True, "team": {"displayName": "Croatia"}},
                {"homeAway": "away", "score": "1", "shootoutScore": 2,
                 "winner": False, "team": {"displayName": "Brazil"}},
            ],
        }],
    }]}


def test_penaltis_placar_e_dos_120min_nao_conta_penaltis():
    res = buscar_partidas_finalizadas(["x"], baixar=lambda d: _payload_penaltis())
    assert len(res) == 1
    p = res[0]
    # pênaltis (4x2) NÃO entram como gols: vale o 1x1 dos 120min
    assert (p.gols1, p.gols2) == (1, 1)


def test_penaltis_marca_quem_avancou_em_pt():
    res = buscar_partidas_finalizadas(["x"], baixar=lambda d: _payload_penaltis())
    # winner=True (Croatia) -> nome PT da planilha
    assert res[0].avanca == "Croácia"


def test_jogo_normal_nao_marca_avanca():
    res = buscar_partidas_finalizadas(["20260624"], baixar=lambda d: _payload())
    assert all(p.avanca is None for p in res)


def test_partida_carrega_data_do_evento():
    res = buscar_partidas_finalizadas(["x"], baixar=lambda d: _payload_penaltis())
    assert res[0].data == "2026-07-05"
