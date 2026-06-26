"""Renderização da página (HTML autossuficiente, tema 'placar de estádio').

`render_pagina(...)` recebe os dados já calculados e devolve o HTML completo
(documento pronto para servir no GitHub Pages).
"""
import html as _html

from bolao.modelo import PREMIO

_MEDALHAS = {1: "🥇", 2: "🥈", 3: "🥉"}
_POS_CLASSE = {1: "ouro", 2: "prata", 3: "bronze"}

_CSS = """
:root{
  --bg:#06120c; --bg2:#0a1c12; --surf:#0f241a; --surf2:#122c20;
  --linha:#1d4030; --grama:#1fe07a; --grama-esc:#0fb863;
  --ouro:#f7c948; --prata:#cdd6dd; --bronze:#d98b4a;
  --txt:#eafaf1; --txt2:#8fb6a2; --sobe:#22e07a; --desce:#ff5d6c;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:'Archivo',system-ui,-apple-system,sans-serif;
  background:var(--bg); color:var(--txt); line-height:1.45;
  -webkit-font-smoothing:antialiased;
  background-image:
    radial-gradient(120% 90% at 50% -10%, rgba(31,224,122,.18), transparent 60%),
    repeating-linear-gradient(0deg, transparent 0 38px, rgba(255,255,255,.012) 38px 39px);
  min-height:100vh;
}
.wrap{max-width:600px;margin:0 auto;padding:26px 18px 56px}
.kicker{font-size:12px;letter-spacing:.32em;text-transform:uppercase;color:var(--grama);font-weight:700}
h1{font-family:'Anton',Impact,'Arial Narrow',sans-serif;font-weight:400;
   font-size:clamp(46px,15vw,76px);line-height:.92;letter-spacing:.01em;margin:6px 0 2px;
   text-transform:uppercase;background:linear-gradient(180deg,#fff,#9fe9c2);
   -webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--txt2);font-size:14px;font-weight:600}
.atualizado{display:inline-flex;align-items:center;gap:7px;margin-top:14px;
  background:var(--surf);border:1px solid var(--linha);border-radius:999px;
  padding:7px 14px;font-size:12.5px;color:var(--txt2);font-weight:600}
.dot{width:8px;height:8px;border-radius:50%;background:var(--grama);box-shadow:0 0 10px var(--grama)}
.secao{margin-top:34px}
.secao-tit{font-family:'Anton',sans-serif;font-weight:400;text-transform:uppercase;
  letter-spacing:.04em;font-size:21px;color:var(--txt);margin-bottom:14px;
  display:flex;align-items:center;gap:10px}
.secao-tit::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--linha),transparent)}

/* leaderboard */
.tabela{display:flex;flex-direction:column;gap:8px}
.row{display:grid;grid-template-columns:46px 1fr auto auto;align-items:center;gap:12px;
  background:var(--surf);border:1px solid var(--linha);border-radius:14px;padding:13px 15px;
  opacity:0;transform:translateY(10px);animation:rise .5s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes rise{to{opacity:1;transform:none}}
.row.ouro{background:linear-gradient(100deg,rgba(247,201,72,.16),var(--surf) 60%);
  border-color:rgba(247,201,72,.5);box-shadow:0 0 26px rgba(247,201,72,.12)}
.row.prata{border-color:rgba(205,214,221,.38)}
.row.bronze{border-color:rgba(217,139,74,.4)}
.pos{font-family:'Anton',sans-serif;font-size:26px;text-align:center;color:var(--txt2);line-height:1}
.row.ouro .pos{color:var(--ouro)} .row.prata .pos{color:var(--prata)} .row.bronze .pos{color:var(--bronze)}
.medalha{font-size:20px;line-height:1}
.nome{font-weight:700;font-size:17px;letter-spacing:.01em;display:flex;align-items:center;gap:8px;min-width:0}
.nome .lider{font-size:10px;letter-spacing:.12em;font-weight:800;color:#06120c;background:var(--ouro);
  padding:2px 7px;border-radius:6px;text-transform:uppercase}
.var{font-size:13px;font-weight:800;font-variant-numeric:tabular-nums;min-width:38px;text-align:right}
.var.s{color:var(--sobe)} .var.d{color:var(--desce)} .var.z{color:var(--txt2);opacity:.5}
.pts{font-family:'Anton',sans-serif;font-size:25px;font-variant-numeric:tabular-nums;min-width:52px;text-align:right}
.pts small{font-family:'Archivo';font-size:11px;color:var(--txt2);font-weight:700;display:block;
  margin-top:-3px;letter-spacing:.08em}

/* resultados */
.jogos{display:flex;flex-direction:column;gap:8px}
.jogo{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:10px;
  background:var(--surf);border:1px solid var(--linha);border-radius:12px;padding:11px 14px;font-weight:600}
.jogo .t1{text-align:right} .jogo .t2{text-align:left}
.placar{font-family:'Anton',sans-serif;font-size:19px;background:var(--bg2);border:1px solid var(--linha);
  border-radius:9px;padding:4px 12px;letter-spacing:.06em;white-space:nowrap}
.destaque{margin-top:12px;background:linear-gradient(100deg,rgba(31,224,122,.14),var(--surf));
  border:1px solid rgba(31,224,122,.4);border-radius:12px;padding:12px 15px;font-size:14px;font-weight:600}
.destaque b{color:var(--grama)}

/* premio */
.premios{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.premio{background:var(--surf);border:1px solid var(--linha);border-radius:14px;padding:15px 10px;text-align:center}
.premio.ouro{border-color:rgba(247,201,72,.5)} .premio.prata{border-color:rgba(205,214,221,.35)}
.premio.bronze{border-color:rgba(217,139,74,.4)}
.premio .m{font-size:24px} .premio .v{font-family:'Anton',sans-serif;font-size:24px;margin:5px 0 1px}
.premio.ouro .v{color:var(--ouro)} .premio.prata .v{color:var(--prata)} .premio.bronze .v{color:var(--bronze)}
.premio .q{font-size:14px;font-weight:700} .premio .l{font-size:10px;letter-spacing:.14em;color:var(--txt2);text-transform:uppercase}

.rodape{margin-top:38px;color:var(--txt2);font-size:12px;line-height:1.7;text-align:center}
.rodape b{color:var(--txt)}
.regras{margin-top:10px;display:inline-flex;flex-wrap:wrap;gap:6px;justify-content:center}
.tag{background:var(--surf);border:1px solid var(--linha);border-radius:8px;padding:5px 10px;font-size:11px;font-weight:600;color:var(--txt2)}
@media(max-width:380px){.row{grid-template-columns:38px 1fr auto auto;gap:8px;padding:11px}.nome{font-size:15px}}
"""


def _esc(s):
    return _html.escape(str(s))


def _linha_rank(i, nome, pts, var):
    pos = i + 1
    classe = _POS_CLASSE.get(pos, "")
    medalha = f'<span class="medalha">{_MEDALHAS[pos]}</span>' if pos in _MEDALHAS else ""
    lider = '<span class="lider">Líder</span>' if pos == 1 else ""
    if var is None:
        var_html = '<span class="var z">·</span>'
    elif var > 0:
        var_html = f'<span class="var s">▲{var}</span>'
    elif var < 0:
        var_html = f'<span class="var d">▼{abs(var)}</span>'
    else:
        var_html = '<span class="var z">–</span>'
    return (
        f'<div class="row {classe}" style="animation-delay:{i*45}ms">'
        f'<div class="pos">{pos}</div>'
        f'<div class="nome">{medalha}{_esc(nome)}{lider}</div>'
        f'{var_html}'
        f'<div class="pts">{pts}<small>PTS</small></div>'
        f'</div>'
    )


def _card_jogo(t1, g1, g2, t2):
    return (
        f'<div class="jogo"><span class="t1">{_esc(t1)}</span>'
        f'<span class="placar">{g1} : {g2}</span>'
        f'<span class="t2">{_esc(t2)}</span></div>'
    )


def _card_premio(pos, valor, nome):
    return (
        f'<div class="premio {_POS_CLASSE[pos]}"><div class="m">{_MEDALHAS[pos]}</div>'
        f'<div class="v">R$ {valor}</div>'
        f'<div class="q">{_esc(nome) if nome else "—"}</div>'
        f'<div class="l">{pos}º lugar</div></div>'
    )


def render_pagina(ranking, *, variacao=None, resultados_rodada=None,
                  pontos_rodada=None, premio=None, atualizado_em="",
                  data_rodada="", fase="Fase de Grupos"):
    variacao = variacao or {}
    premio = premio or PREMIO

    linhas = "".join(
        _linha_rank(i, nome, pts, variacao.get(nome))
        for i, (nome, pts) in enumerate(ranking)
    )

    # seção de resultados (opcional)
    sec_result = ""
    if resultados_rodada:
        jogos = "".join(_card_jogo(*j) for j in resultados_rodada)
        destaque = ""
        if pontos_rodada:
            top = max(pontos_rodada.items(), key=lambda kv: kv[1])
            if top[1] > 0:
                nomes = [n for n, p in pontos_rodada.items() if p == top[1]]
                quem = ", ".join(_esc(n) for n in nomes)
                destaque = (f'<div class="destaque">🔥 Destaque da rodada: '
                            f'<b>{quem}</b> — +{top[1]} pts</div>')
        titulo = "Resultados" + (f" · {_esc(data_rodada)}" if data_rodada else "")
        sec_result = (
            f'<div class="secao"><div class="secao-tit">⚽ {titulo}</div>'
            f'<div class="jogos">{jogos}</div>{destaque}</div>'
        )

    # prêmio: nomes atualmente em 1º/2º/3º
    nome_pos = {i + 1: nome for i, (nome, _) in enumerate(ranking)}
    premios = "".join(_card_premio(p, premio[p], nome_pos.get(p)) for p in (1, 2, 3))

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bolão Copa 2026</title>
<meta name="description" content="Classificação ao vivo do Bolão da Copa 2026.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%E2%9A%BD%3C/text%3E%3C/svg%3E">
<meta property="og:title" content="Bolão Copa 2026 — Classificação">
<meta property="og:description" content="Ranking atualizado todo dia automaticamente.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="kicker">⚽ Copa 2026 · {_esc(fase)}</div>
    <h1>Bolão<br>Copa 2026</h1>
    <div class="sub">Classificação geral · {len(ranking)} apostadores</div>
    <div class="atualizado"><span class="dot"></span> Atualizado em {_esc(atualizado_em)}</div>
  </header>

  <div class="secao">
    <div class="secao-tit">🏆 Classificação</div>
    <div class="tabela">{linhas}</div>
  </div>

  {sec_result}

  <div class="secao">
    <div class="secao-tit">💰 Prêmio · R$ 650</div>
    <div class="premios">{premios}</div>
  </div>

  <div class="rodape">
    <b>Atualiza sozinho todo dia.</b> Basta abrir este link.<br>
    Pontos por jogo: <b>+2</b> resultado · <b>+1</b> gols de cada time · <b>+1</b> total de gols
    <div class="regras">
      <span class="tag">Fonte: ESPN (oficial)</span>
      <span class="tag">50% / 30% / 20%</span>
    </div>
  </div>
</div>
</body>
</html>"""
