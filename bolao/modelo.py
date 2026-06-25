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
# "=SUM(...)+10" da aba "Total Pontos".
BONUS = {"Caio": 10, "Camps": 10, "Kim": 10}

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
