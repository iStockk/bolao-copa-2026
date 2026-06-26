"""Leitura da planilha de respostas do Google Forms (coleta do mata-mata).

A planilha exportada do Forms tem, na 1ª aba, as colunas:
  Timestamp | Quem é você? | Gols <time casa> (Jogo N) | Gols <time visit.> (Jogo N) | ...
Dois campos de gols por jogo (casa, depois visitante).

Regras:
- vale só a ÚLTIMA resposta de cada participante (mudou de ideia => sobrescreve);
- se houver prazo, respostas depois do apito não contam.
"""
import datetime as dt

import openpyxl

from bolao.respostas_form import ler_respostas_form


def _wb_respostas(linhas, headers=None):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Form Responses 1"
    if headers is None:
        headers = [
            "Timestamp", "Quem é você?",
            "Gols 🇿🇦 África do Sul (Jogo 1)", "Gols 🇨🇦 Canadá (Jogo 1)",
            "Gols Time A (Jogo 2)", "Gols Time B (Jogo 2)",
        ]
    ws.append(headers)
    for linha in linhas:
        ws.append(linha)
    return wb


def test_le_palpites_por_participante():
    ts = dt.datetime(2026, 6, 27, 20, 0)
    wb = _wb_respostas([[ts, "Caio", "0", "3", "1", "0"]])
    assert ler_respostas_form(wb) == {"Caio": {1: (0, 3), 2: (1, 0)}}


def test_considera_apenas_a_ultima_resposta_de_cada_um():
    t1 = dt.datetime(2026, 6, 27, 18, 0)
    t2 = dt.datetime(2026, 6, 27, 19, 0)
    wb = _wb_respostas([
        [t1, "Caio", "1", "1", "0", "0"],   # primeira tentativa
        [t2, "Caio", "0", "3", "2", "2"],   # mudou de ideia depois -> vale esta
    ])
    assert ler_respostas_form(wb)["Caio"] == {1: (0, 3), 2: (2, 2)}


def test_ignora_respostas_depois_do_prazo():
    prazo = dt.datetime(2026, 6, 28, 13, 0)
    wb = _wb_respostas([
        [dt.datetime(2026, 6, 28, 12, 0), "Su", "1", "0", "1", "1"],   # no prazo
        [dt.datetime(2026, 6, 28, 14, 0), "Su", "5", "5", "5", "5"],   # atrasada
        [dt.datetime(2026, 6, 28, 14, 5), "Kim", "2", "2", "2", "2"],  # só atrasada
    ])
    palpites = ler_respostas_form(wb, prazo=prazo)
    assert palpites["Su"] == {1: (1, 0), 2: (1, 1)}   # vale a do prazo
    assert "Kim" not in palpites                        # atrasou em tudo -> fora


def test_aceita_gols_numericos_alem_de_texto():
    # o formulário antigo gravava número (3.0); o novo grava texto ("3"). Aceitar ambos.
    ts = dt.datetime(2026, 6, 27, 20, 0)
    wb = _wb_respostas([[ts, "Mané", 0, 3.0, "1", "2"]])
    assert ler_respostas_form(wb)["Mané"] == {1: (0, 3), 2: (1, 2)}
