"""Leitura da planilha de respostas do Google Forms (coleta de palpites do mata-mata).

A planilha exportada do Forms tem, na 1ª aba, o cabeçalho:
  Timestamp | Quem é você? | Gols <casa> (Jogo N) | Gols <visitante> (Jogo N) | ...
São 2 colunas de gols por jogo, na ordem casa e depois visitante. O número do
jogo é lido do próprio cabeçalho ("(Jogo N)"), então emoji/bandeira no nome do
time não atrapalham.

Regras (decisão do time):
- vale só a ÚLTIMA resposta de cada participante (se respondeu de novo, sobrescreve);
- se `prazo` for dado, respostas com Timestamp depois do apito não contam.
"""
import re

_RE_JOGO = re.compile(r"\(Jogo\s*(\d+)\)")


def _para_int(v):
    """Converte gols (texto '3', float 3.0 ou int 3) para int; vazio -> None."""
    if v is None or v == "":
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def _aba_respostas(wb):
    """A aba de respostas é a que tem 'Timestamp' no cabeçalho."""
    for ws in wb.worksheets:
        primeira = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), ())
        if primeira and any(c == "Timestamp" for c in primeira):
            return ws
    raise ValueError("Não encontrei a aba de respostas (sem coluna 'Timestamp').")


def ler_respostas_form(wb, prazo=None):
    """Lê a planilha de respostas do Forms.

    Retorna {nome: {num_jogo: (gols1, gols2)}}, considerando só a última resposta
    de cada um (e, se `prazo` for dado, ignorando as enviadas após o prazo).
    """
    ws = _aba_respostas(wb)
    header = list(next(ws.iter_rows(min_row=1, max_row=1, values_only=True)))

    col_ts = col_nome = None
    jogo_cols = {}  # num_jogo -> [idx_casa, idx_visitante]
    for idx, h in enumerate(header):
        if h is None:
            continue
        if h == "Timestamp":
            col_ts = idx
        elif "Quem" in str(h):
            col_nome = idx
        else:
            m = _RE_JOGO.search(str(h))
            if m:
                jogo_cols.setdefault(int(m.group(1)), []).append(idx)

    melhor = {}  # nome -> (timestamp, palpites)
    for row in ws.iter_rows(min_row=2, values_only=True):
        nome = row[col_nome] if col_nome is not None else None
        if not nome:
            continue
        ts = row[col_ts] if col_ts is not None else None
        if prazo is not None and ts is not None and ts > prazo:
            continue
        palpites = {
            num: (_para_int(row[cols[0]]) if len(cols) >= 1 else None,
                  _para_int(row[cols[1]]) if len(cols) >= 2 else None)
            for num, cols in jogo_cols.items()
        }
        anterior = melhor.get(nome)
        if anterior is None or anterior[0] is None or (ts is not None and ts >= anterior[0]):
            melhor[nome] = (ts, palpites)

    return {nome: palpites for nome, (_ts, palpites) in melhor.items()}
