"""Mapeamento dos nomes dos times: variações da fonte (ESPN, em inglês) -> nome
PT exatamente como aparece na planilha.

`casar_time(nome)` normaliza (sem acento, minúsculas, só a-z0-9) e consulta o MAPA.
Retorna o nome PT da planilha, ou None se não reconhecido.
"""
import unicodedata


def normalizar(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s.lower() if c.isalnum())


# nome PT da planilha -> apelidos aceitos (inclui o próprio PT).
_ALIASES = {
    "México": ["Mexico"],
    "África do Sul": ["South Africa"],
    "Coreia do Sul": ["South Korea", "Korea Republic", "Korea South", "Republic of Korea"],
    "Tchéquia": ["Czechia", "Czech Republic"],
    "Canadá": ["Canada"],
    "Bósnia": ["Bosnia", "Bosnia-Herzegovina", "Bosnia and Herzegovina", "Bosnia & Herzegovina"],
    "Catar": ["Qatar"],
    "Suíça": ["Switzerland"],
    "Brasil": ["Brazil"],
    "Marrocos": ["Morocco"],
    "Haiti": ["Haiti"],
    "Escócia": ["Scotland"],
    "EUA": ["USA", "United States", "United States of America", "US"],
    "Paraguai": ["Paraguay"],
    "Austrália": ["Australia"],
    "Turquia": ["Turkey", "Turkiye", "Türkiye"],
    "Alemanha": ["Germany"],
    "Curaçau": ["Curacao", "Curaçao"],
    "Costa do Marfim": ["Ivory Coast", "Cote d'Ivoire", "Côte d'Ivoire", "Cote dIvoire"],
    "Equador": ["Ecuador"],
    "Holanda": ["Netherlands", "Holland"],
    "Japão": ["Japan"],
    "Suécia": ["Sweden"],
    "Tunísia": ["Tunisia"],
    "Bélgica": ["Belgium"],
    "Egito": ["Egypt"],
    "Irã": ["Iran", "IR Iran"],
    "Nova Zelândia": ["New Zealand"],
    "Espanha": ["Spain"],
    "Cabo Verde": ["Cape Verde", "Cabo Verde"],
    "Arábia Saudita": ["Saudi Arabia"],
    "Uruguai": ["Uruguay"],
    "França": ["France"],
    "Senegal": ["Senegal"],
    "Iraque": ["Iraq"],
    "Noruega": ["Norway"],
    "Argentina": ["Argentina"],
    "Argélia": ["Algeria"],
    "Áustria": ["Austria"],
    "Jordânia": ["Jordan"],
    "Portugal": ["Portugal"],
    "RD Congo": ["DR Congo", "Congo DR", "Democratic Republic of the Congo",
                 "Congo Democratic Republic", "DR Congo (Kinshasa)"],
    "Uzbequistão": ["Uzbekistan"],
    "Colômbia": ["Colombia"],
    "Inglaterra": ["England"],
    "Croácia": ["Croatia"],
    "Gana": ["Ghana"],
    "Panamá": ["Panama"],
}

# normalizado -> nome PT
MAPA = {}
for _pt, _als in _ALIASES.items():
    for _a in [_pt, *_als]:
        MAPA[normalizar(_a)] = _pt


def casar_time(nome):
    """Nome PT da planilha para um nome vindo da fonte, ou None se não mapeado."""
    return MAPA.get(normalizar(nome))
