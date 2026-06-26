/**
 * GERADOR DO FORMULÁRIO DE APOSTAS — Bolão Copa 2026 (fase mata-mata)
 * ------------------------------------------------------------------
 * Como usar (não precisa ser programador):
 *   1. Abra https://script.google.com  (logado na sua conta Google)
 *   2. "Novo projeto" -> apague o que estiver lá -> cole ESTE arquivo inteiro
 *   3. No topo, EDITE a seção "EDITE AQUI" (título, prazo, jogos e bandeiras)
 *   4. Salve (Ctrl+S) -> escolha a função "criarFormularioBolao" -> Executar (▶)
 *        - na 1ª vez: "O Google não verificou este app" é NORMAL (o código é seu):
 *          "Avançado" -> "Acessar (não seguro)" -> "Permitir".
 *   5. Menu "Execução" -> "Logs": saem 3 links:
 *        - LINK PARA RESPONDER  (manda no grupo)
 *        - LINK PARA EDITAR
 *        - PLANILHA DE RESPOSTAS (é o que eu uso pro merge)
 *   6. (Opcional, deixar bonito) No editor do formulário, clique no ícone de
 *      PALETA (🎨) no topo -> escolha uma cor/tema e uma imagem de cabeçalho.
 *
 * Toda rodada: troque a lista "jogos" (e as bandeiras novas) e rode de novo.
 */
function criarFormularioBolao() {

  // ===================== EDITE AQUI =====================

  var TITULO = 'Bolão Copa 2026 — Apostas do Mata-mata (1ª rodada)';

  var PRAZO = 'PRAZO: até o apito inicial do 1º jogo desta rodada. '
            + 'Quem enviar depois do prazo ZERA os pontos desta rodada. '
            + 'Pode responder de novo se mudar de ideia — vale a sua ÚLTIMA resposta antes do prazo.';

  // Jogos da rodada: [ número, "Time da Casa", "Time Visitante" ]
  // >>> Sábado à noite, quando os confrontos fecharem, é SÓ trocar esta lista. <<<
  var jogos = [
    [1, 'África do Sul', 'Canadá'],          // já definido
    [2, 'EXEMPLO Time A', 'EXEMPLO Time B'],  // troque pelos reais
    [3, 'EXEMPLO Time C', 'EXEMPLO Time D'],  // troque pelos reais
  ];

  // Emoji de bandeira por time (deixa o formulário com cara de Copa).
  // Se um time não estiver aqui, simplesmente aparece sem bandeira (sem erro).
  // Sábado eu te mando o emoji de cada seleção que entrar.
  var BANDEIRAS = {
    'África do Sul': '🇿🇦',
    'Canadá': '🇨🇦',
    'Brasil': '🇧🇷',
    'Argentina': '🇦🇷',
    'França': '🇫🇷',
    'Inglaterra': '🏴',
    'Espanha': '🇪🇸',
    'Portugal': '🇵🇹',
    'Alemanha': '🇩🇪',
    'Estados Unidos': '🇺🇸',
    'México': '🇲🇽',
    'Holanda': '🇳🇱',
  };

  // Maior placar possível no menu (0 a este número).
  var MAX_GOLS = 10;

  // =====================================================
  // (daqui pra baixo não precisa mexer)

  var participantes = ['Beda','Pedro','Mauro','Rodrigo','Paulo','Su','Biral',
                       'Mané','Romanelli','AH','Caio','Camps','Kim'];

  function comBandeira(time) {
    var b = BANDEIRAS[time];
    return (b ? b + ' ' : '') + time;
  }

  // Opções do menu de gols: "0","1",...,"MAX_GOLS"
  var opcoesGols = [];
  for (var g = 0; g <= MAX_GOLS; g++) opcoesGols.push(String(g));

  var form = FormApp.create(TITULO);
  form.setDescription(PRAZO);
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false); // sem conta -> trato duplicado pela última resposta
  form.setAllowResponseEdits(false);
  form.setProgressBar(true);
  form.setShowLinkToRespondAgain(false);

  // Pergunta 1: quem é você? (lista suspensa obrigatória)
  form.addListItem()
      .setTitle('Quem é você?')
      .setHelpText('Escolha o seu nome na lista.')
      .setChoiceValues(participantes)
      .setRequired(true);

  // Para cada jogo: cabeçalho + 2 menus suspensos de gols (0..MAX_GOLS)
  jogos.forEach(function (j) {
    var num = j[0], casa = j[1], visitante = j[2];
    form.addSectionHeaderItem()
        .setTitle('⚽ Jogo ' + num + ':   ' + comBandeira(casa) + '   x   ' + comBandeira(visitante));
    form.addListItem()
        .setTitle('Gols ' + comBandeira(casa) + '  (Jogo ' + num + ')')
        .setChoiceValues(opcoesGols)
        .setRequired(true);
    form.addListItem()
        .setTitle('Gols ' + comBandeira(visitante) + '  (Jogo ' + num + ')')
        .setChoiceValues(opcoesGols)
        .setRequired(true);
  });

  // Planilha de respostas vinculada
  var ss = SpreadsheetApp.create(TITULO + ' (Respostas)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('==================================================');
  Logger.log('LINK PARA RESPONDER (manda esse no grupo):');
  Logger.log(form.getPublishedUrl());
  Logger.log('--------------------------------------------------');
  Logger.log('LINK PARA EDITAR o formulário:');
  Logger.log(form.getEditUrl());
  Logger.log('--------------------------------------------------');
  Logger.log('PLANILHA DE RESPOSTAS (eu uso pro merge):');
  Logger.log(ss.getUrl());
  Logger.log('==================================================');
}
