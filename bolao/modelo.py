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

# Jogos 1..72 ficam nas linhas 5..76 de cada aba.
PRIMEIRA_LINHA = 5
ULTIMA_LINHA = 76

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
