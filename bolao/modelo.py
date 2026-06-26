"""Constantes e estruturas de dados do bolão."""
from dataclasses import dataclass

# (nome de exibição, nome da aba na planilha). A aba "Camps " tem espaço no fim.
PARTICIPANTES = [
    ("Beda", "Beda"),
    ("Pedro", "Pedro"),
    ("Mauro", "Mauro"),
    ("Rodrigo", "Rodrigo"),
    ("Paulo", "Paulo"),
    ("Su", "Su"),
    ("Biral", "Biral"),
    ("Mané", "Mané"),
    ("Romanelli", "Romanelli"),
    ("AH", "AH"),
    ("Caio", "Caio"),
    ("Camps", "Camps "),
    ("Kim", "Kim"),
]

# Bônus fixo (+10) somado ao total destes participantes — replica as fórmulas
# "=SUM(...)+10" da aba "Total Pontos". Razão (decisão do time): Caio, Camps e Kim
# entraram atrasados no bolão; o último colocado na época tinha 12 pontos, então
# decidiu-se que eles começariam com 10.
BONUS = {"Caio": 10, "Camps": 10, "Kim": 10}

# Jogos que o bolão NÃO considera. Decisão do time: como o bolão começou atrasado,
# os 4 primeiros jogos (11-12/jun) não entram na contagem (mesma lógica do bônus +10).
# O robô NUNCA preenche nem pontua estes jogos, mesmo na auto-recuperação.
JOGOS_IGNORADOS = frozenset({1, 2, 3, 4})

# Jogos começam na linha 5 (jogo 1). `ULTIMA_LINHA` é o CAP de leitura/soma: cobre
# o torneio inteiro — 72 da fase de grupos + 32 do mata-mata (16 oitavas-de-32 +
# 8 + 4 + 2 + 1 3º lugar + 1 final) = 104 jogos -> linha 5+104-1 = 108. Linhas
# vazias acima do que já existe somam 0 e são ignoradas na leitura, então deixar
# o cap largo desde já é seguro e evita reescrever faixas a cada rodada.
PRIMEIRA_LINHA = 5
ULTIMA_LINHA = 108
ULTIMA_LINHA_GRUPOS = 76  # última linha da fase de grupos (jogo 72) — referência

# Último jogo da fase de grupos. Jogos com número acima disto são do mata-mata
# (Fase 2). Constante separada do cap de linhas: serve para rotular a fase no
# site sem depender de quantas linhas a planilha lê.
ULTIMO_JOGO_GRUPOS = 72

# Rateio do prêmio (R$50 x 13 = R$650).
PREMIO = {1: 325, 2: 195, 3: 130}


@dataclass(frozen=True)
class Jogo:
    numero: int
    grupo: str
    time1: str
    time2: str
    data: str   # ISO 'YYYY-MM-DD'
    hora: str    # 'HH:MM'
