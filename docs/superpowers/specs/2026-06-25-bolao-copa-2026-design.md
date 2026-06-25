# Bolão Copa 2026 — Página automática + atualização diária

**Data:** 2026-06-25
**Autor:** Caio Canella (caio@mapacapital.com.br) + Claude Code
**Status:** Aprovado (Fase 1) — Fase 2 em esboço

---

## 1. Problema

Bolão da Copa 2026 da empresa (Mapa Capital), com 13 participantes, controlado na planilha
`TABELA_APOSTAS_-_COPA_2026.xlsx`. Hoje a rotina é manual e diária: preencher os resultados
do dia anterior, reordenar a tabela de classificação, tirar print e mandar no grupo de WhatsApp.

Objetivos:
1. **Eliminar o trabalho manual diário** — preencher resultados e reordenar a classificação automaticamente.
2. **Substituir o print diário por um link único** — uma página web que o usuário manda *uma vez* no
   grupo e que sempre mostra a classificação mais recente.
3. Rodar **100% automático na nuvem**, mesmo com o PC do usuário desligado.

## 2. Como a planilha funciona (descoberto na análise)

- **16 abas:** `Resultados`, 13 abas de participantes (Beda, Pedro, Mauro, Rodrigo, Paulo, Su, Biral,
  Mané, Caio, Camps, Romanelli, AH, Kim), `Total Pontos`, `Regras`.
- **72 jogos** = fase de grupos completa (grupos A–L), de 11/jun a **27/jun**. A planilha cobre **só a
  fase de grupos**.
- Em cada aba: colunas A=jogo, B=grupo, C=time1, D=gols time1, E="X", F=gols time2, G=time2,
  H/I=data, J=hora. Nas abas de participante, **D/F são os palpites (fixos/travados)** e **K é a
  pontuação** do jogo.
- **Os palpites são estáticos.** A única coisa que muda diariamente é a aba `Resultados` (placar oficial).
  Logo, a classificação inteira é 100% derivável da planilha.
- **Pontuação por jogo (máx. 5 pts)**, fórmula da coluna K:
  - `+2` por acertar o resultado (V/E/D) — via `SIGN(D-F) == SIGN(Resultados!D-Resultados!F)`
  - `+1` por acertar os gols do time1 (`D == Resultados!D`)
  - `+1` por acertar os gols do time2 (`F == Resultados!F`)
  - `+1` por acertar o total de gols (`D+F == Resultados!D+Resultados!F`)
  - só pontua se os 4 valores (palpite e resultado) forem números.
- **Total Pontos:** soma `K5:K76` de cada participante. **Bônus de +10** somado a Caio, Camps e Kim
  (preservar exatamente). A tabela de classificação (D11:E24) hoje é **ordenada manualmente**.
- **Regras / prêmio:** R$50 por pessoa (Pix), total R$650. Rateio 50% / 30% / 20% para 1º / 2º / 3º.
  Empate em uma colocação divide o prêmio daquela colocação igualmente.
- **Confronto validado contra a Copa real de 2026:** os 72 jogos batem com o torneio oficial
  (ex.: Grupo C = Brasil/Marrocos/Haiti/Escócia; Escócia 0×3 Brasil em 24/jun). Resultados preenchidos
  até 24/jun (jogo 54).

## 3. Arquitetura (Fase 1)

Tudo mora num **repositório GitHub** (fonte da verdade: planilha mestre + código + página).

**Robô diário (GitHub Actions, cron ~10:00 BRT, + gatilho manual `workflow_dispatch`):**
1. **Buscar resultados** dos jogos já encerrados numa fonte pública de futebol.
   - Fonte primária pretendida: scoreboard público da ESPN (JSON, **sem chave de API**).
   - Validar na 1ª etapa de implementação; fallbacks: football-data.org / API-Football (free tier).
2. **Casar** cada jogo da fonte → linha da aba `Resultados` por (time1, time2, data), usando uma
   **tabela de mapeamento de nomes PT↔fonte**. Escrever D/F só de jogos finalizados.
3. **Calcular em Python** (independente de Excel/LibreOffice) a pontuação de cada participante e a
   classificação, replicando exatamente a fórmula da coluna K + o bônus +10.
4. **Atualizar a planilha** (`openpyxl`): escrever resultados em `Resultados` e **reordenar a tabela de
   classificação** em `Total Pontos`. (As fórmulas K e de soma são preservadas; o Excel recalcula ao
   abrir — a planilha continua correta como registro.)
5. **Gerar a página** (1 arquivo `index.html` autossuficiente — CSS/JS inline, sem dependências externas).
6. **Publicar** no GitHub Pages e **commitar a planilha atualizada** de volta no repositório.

**Hospedagem:** GitHub Pages, **repositório público** (sem conta extra, sem tokens — o Action publica
com o `GITHUB_TOKEN` nativo). Link permanente: `https://<usuario>.github.io/<repo>/`.

> Decisão: GitHub Pages em vez de Netlify, já que o GitHub é usado de qualquer forma para o robô —
> uma conta a menos e zero segredos a configurar. (Netlify continua possível como alternativa, ao
> custo de guardar um token.)

**Privacidade:** a planilha tem dado pessoal em pelo menos uma aba (nome completo, telefone e e-mail
do Beda). Como o repositório será público, a **cópia da planilha versionada no repo terá esse contato
removido** (telefone/e-mail/nome completo zerados em todas as abas). A planilha local do usuário
permanece intacta. A página nunca exibe contato — só nomes/apelidos e pontos (já compartilhados no grupo).

## 4. Conteúdo e visual da página (Fase 1)

- **Cabeçalho:** título "Bolão Copa 2026" + carimbo "atualizado em DD/MM HH:MM".
- **Classificação** (destaque): posição, nome, pontos; 🥇🥈🥉 no topo; indicador de subiu/caiu desde a
  atualização anterior.
- **Resultados de ontem:** lista dos jogos do dia anterior + pontos que cada participante fez na rodada.
- **Prêmio:** R$650 total → 🥇 R$325 · 🥈 R$195 · 🥉 R$130, com os nomes nas posições atuais.
- **Estilo:** mobile-first (abre via link de WhatsApp), tema Copa, leve e rápido.

## 5. Componentes (unidades isoladas)

- `gerar.py` (ou pacote `bolao/`): orquestra o ciclo. Subcomponentes com responsabilidade única:
  - **fetcher**: busca resultados da fonte pública → lista normalizada de partidas finalizadas.
  - **nomes**: tabela de mapeamento PT↔fonte + função de casamento de partidas.
  - **planilha**: lê palpites/jogos, escreve resultados, reordena classificação, salva `.xlsx`.
  - **pontuacao**: dado palpites + resultados, calcula pontos por jogo, totais e ranking (espelha a
    fórmula K + bônus).
  - **render**: dados de ranking + rodada → `index.html`.
- `.github/workflows/atualizar.yml`: o cron + passos do robô + deploy no Pages.
- Cada unidade é testável isoladamente (ex.: `pontuacao` validada contra os totais atuais da planilha:
  Mané 110, AH 107, Romanelli 106, Su 100, Rodrigo 99, Beda 95, Mauro 95, Pedro 90, Caio 89, Biral 87,
  Paulo 85, Camps 74, Kim 58).

## 6. Tratamento de erros

- **Fonte indisponível / jogo sem placar:** não escreve nada para aquele jogo; deixa em branco e
  segue. Nunca sobrescreve um resultado já preenchido com vazio.
- **Nome não mapeado:** falha barulhenta no log do Action (não publica dado errado) e mantém a última
  página válida no ar.
- **Sanidade:** ao final, a soma dos pontos recalculados deve bater com a soma das colunas K; carimbo
  de "última atualização" só avança se a geração foi bem-sucedida.

## 7. Testes

- `pontuacao`: reproduzir exatamente os totais atuais (seção 5) a partir da planilha existente.
- `nomes`: todos os 24 países da planilha têm mapeamento para a fonte.
- `planilha`: round-trip (ler → escrever resultado de teste → reler) sem corromper fórmulas/abas.
- Teste de fumaça do `render`: HTML gerado contém os 13 nomes e a data.

## 8. Entrega incremental

- **Hoje:** publicar a 1ª versão da página (classificação atual de 24/jun) para o usuário já mandar o
  link no grupo. Automação entra a partir da manhã seguinte.

## 9. Fase 2 (mata-mata) — esboço, a detalhar até 27/jun

Fora do escopo desta Fase 1, registrado para planejamento posterior:
- Adicionar à planilha os jogos de cada nova rodada (confrontos dependem da classificação final dos grupos).
- Ciclo de coleta: usuário distribui a planilha → 13 participantes preenchem os palpites dos novos jogos →
  usuário devolve as 13 planilhas → merge dos palpites na planilha mestre.
- **Decisão pendente:** regras de pontuação do mata-mata (ex.: jogo que vai para prorrogação/pênaltis
  conta como empate? placar de 90 min ou final?). A definir com o usuário.
- Implica estender estruturalmente a planilha (novas linhas + ranges de soma além de K5:K76).

## 10. Setup único do usuário (~15 min, guiado)

1. Já tem conta GitHub. Criar um repositório novo (ex.: `bolao-copa-2026`).
2. Autorizar o push local (via Git Credential Manager no 1º push, ou Personal Access Token).
3. Ativar GitHub Pages no repositório (origem: GitHub Actions). Resto é com o Claude.

## 11. Itens em aberto

- Validar a fonte pública de resultados (ESPN vs. football-data.org vs. API-Football).
- ~~Repo público ou privado?~~ **Resolvido:** repo **público** + GitHub Pages; contato pessoal
  removido da cópia versionada da planilha.
- Confirmar nome/identidade visual (logo/empresa) no cabeçalho da página.
