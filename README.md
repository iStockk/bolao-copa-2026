# Bolão Copa 2026 ⚽

Página automática da classificação do bolão da Copa 2026 (fase de grupos).

**Página ao vivo:** https://istockk.github.io/bolao-copa-2026/

## Como funciona

Um robô (GitHub Actions) roda todo dia de manhã e, sozinho:

1. Busca os placares oficiais do dia anterior no endpoint público da ESPN (sem chave de API).
2. Preenche a aba `Resultados` da planilha `TABELA_APOSTAS_-_COPA_2026.xlsx`.
3. Calcula a pontuação de cada participante e monta a classificação (em Python).
4. Reordena a tabela de classificação na planilha.
5. Gera a página (`site/index.html`) e publica no GitHub Pages.

A planilha é a fonte da verdade: os palpites de cada um (travados) e os resultados.

## Pontuação (por jogo, máx. 5 pts)

- **+2** acertar o resultado (vitória/empate/derrota)
- **+1** acertar os gols do 1º time · **+1** os gols do 2º time · **+1** o total de gols

## Rodar localmente

```bash
pip install -r requirements.txt
python gerar.py          # gera site/index.html a partir da planilha + placares
python -m pytest -q      # roda os testes
```
