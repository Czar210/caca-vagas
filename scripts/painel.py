"""Gera painel.html: um arquivo só, com os dados dentro, que abre direto no navegador."""
from __future__ import annotations

import json
from pathlib import Path

MODELO = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de vagas</title>
<style>
:root {
  --bg: #f6f7f9; --card: #ffffff; --ink: #1c2024; --muted: #5d6670; --line: #e1e5ea;
  --accent: #2557a7; --accent-soft: #e6eefb; --chip: #eef1f4;
  --a1: #1f7a4d; --a1s: #e3f3ea; --a2: #4c7a1f; --a2s: #eaf3df; --a3: #8a6d00; --a3s: #fbf3d6;
  --a4: #a5520c; --a4s: #fbeadb; --a5: #a4262c; --a5s: #f9e1e2;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #111418; --card: #1a1e23; --ink: #e6e9ec; --muted: #9aa4ae; --line: #2a3038;
    --accent: #7aa7f0; --accent-soft: #1d2a40; --chip: #232931;
    --a1: #5fd19a; --a1s: #15301f; --a2: #a6d46b; --a2s: #22301a; --a3: #e8c75a; --a3s: #322a10;
    --a4: #f0a56a; --a4s: #36230f; --a5: #f08a8f; --a5s: #3a1a1c;
  }
}
:root[data-theme="dark"] {
  --bg: #111418; --card: #1a1e23; --ink: #e6e9ec; --muted: #9aa4ae; --line: #2a3038;
  --accent: #7aa7f0; --accent-soft: #1d2a40; --chip: #232931;
  --a1: #5fd19a; --a1s: #15301f; --a2: #a6d46b; --a2s: #22301a; --a3: #e8c75a; --a3s: #322a10;
  --a4: #f0a56a; --a4s: #36230f; --a5: #f08a8f; --a5s: #3a1a1c;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
.wrap { max-width: 1100px; margin: 0 auto; padding: 24px 16px 64px; }
header { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: baseline; justify-content: space-between; }
h1 { font-size: 22px; font-weight: 600; margin: 0; letter-spacing: -0.2px; }
.sub { color: var(--muted); font-size: 13px; }
.stats { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
.stat { flex: 1 1 140px; background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 8px 12px; }
.stat b { display: block; font-size: 20px; font-weight: 600; }
.stat span { color: var(--muted); font-size: 12px; }
.filtros { background: var(--bg); padding: 10px 0; border-bottom: 1px solid var(--line);
  display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
input[type=search], select { font: inherit; font-size: 14px; color: var(--ink); background: var(--card);
  border: 1px solid var(--line); border-radius: 8px; padding: 7px 10px; }
input[type=search] { flex: 1 1 220px; min-width: 0; }
label.chk { font-size: 14px; color: var(--muted); display: flex; gap: 6px; align-items: center; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font: inherit; font-size: 13px; border: 1px solid var(--line); background: var(--chip); color: var(--ink);
  border-radius: 999px; padding: 4px 11px; cursor: pointer; }
.chip[aria-pressed=true] { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); }
#tema { margin-left: auto; }
@media (min-width: 760px) { .filtros { position: sticky; top: 0; z-index: 2; } .stat { flex: 0 1 150px; } }
.lista { display: grid; gap: 12px; margin-top: 14px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }
.card.fechada { opacity: .6; }
.topo { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; }
.empresa { font-weight: 600; }
.tag { font-size: 12px; border-radius: 6px; padding: 2px 8px; background: var(--chip); color: var(--muted); }
.ad { font-size: 12px; border-radius: 6px; padding: 2px 8px; font-weight: 600; }
.ad.alta { background: var(--a1s); color: var(--a1); } .ad.media_alta { background: var(--a2s); color: var(--a2); }
.ad.media { background: var(--a3s); color: var(--a3); } .ad.media_baixa { background: var(--a4s); color: var(--a4); }
.ad.baixa { background: var(--a5s); color: var(--a5); }
.cargo { font-size: 17px; margin: 6px 0 4px; font-weight: 500; }
.meta { color: var(--muted); font-size: 13px; }
.sal { margin-top: 8px; font-size: 14px; }
.sal .tipo { font-size: 11px; text-transform: uppercase; letter-spacing: .5px; color: var(--muted); margin-left: 6px; }
.motivo { margin-top: 6px; font-size: 14px; }
.falta { margin-top: 4px; font-size: 13px; color: var(--muted); }
details { margin-top: 6px; font-size: 13px; color: var(--muted); }
summary { cursor: pointer; }
.rodape { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--line); }
.st { font-size: 12px; border-radius: 999px; padding: 2px 10px; border: 1px solid var(--line); }
.st.aplicada, .st.entrevista, .st.proposta { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.id { font: 12px ui-monospace, Menlo, Consolas, monospace; color: var(--muted); }
.acoes { margin-left: auto; display: flex; flex-wrap: wrap; gap: 6px; }
.btn { font: inherit; font-size: 13px; border-radius: 8px; padding: 5px 10px; border: 1px solid var(--line);
  background: var(--card); color: var(--ink); text-decoration: none; cursor: pointer; }
.btn.prim { background: var(--accent); border-color: var(--accent); color: #fff; }
:root[data-theme="dark"] .btn.prim { color: #0b1220; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .btn.prim { color: #0b1220; } }
.vazio { color: var(--muted); padding: 40px 0; text-align: center; }
.toast { position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); background: var(--ink); color: var(--bg);
  padding: 8px 14px; border-radius: 8px; font-size: 14px; opacity: 0; transition: opacity .2s; pointer-events: none; }
.toast.on { opacity: 1; }
.ajuda { color: var(--muted); font-size: 13px; margin-top: 28px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Painel de vagas</h1>
    <div class="sub" id="sub"></div>
  </header>
  <div class="stats" id="stats"></div>
  <div class="filtros">
    <input type="search" id="busca" placeholder="Buscar empresa, cargo, stack" aria-label="Buscar">
    <select id="fAd" aria-label="Aderência"><option value="">Toda aderência</option></select>
    <select id="fSt" aria-label="Status"><option value="">Todo status</option></select>
    <select id="ordem" aria-label="Ordenar">
      <option value="ad">Melhor aderência</option><option value="data">Mais recentes</option><option value="emp">Empresa</option>
    </select>
    <label class="chk"><input type="checkbox" id="fFech"> mostrar fechadas e descartadas</label>
    <button class="btn" id="tema" type="button">Tema</button>
    <div class="chips" id="chips"></div>
  </div>
  <div class="lista" id="lista"></div>
  <p class="ajuda">Para mudar algo, peça ao Claude: "marca a vaga a1b2c3 como aplicada", "atualiza as vagas", "adapta meu currículo pra vaga a1b2c3". O painel é refeito a cada mudança.</p>
</div>
<div class="toast" id="toast"></div>
<script type="application/json" id="dados">__DADOS__</script>
<script>
(function () {
  var D = JSON.parse(document.getElementById('dados').textContent);
  var V = D.vagas || [];
  var AD = { alta: 'Alta', media_alta: 'Média alta', media: 'Média', media_baixa: 'Média baixa', baixa: 'Baixa' };
  var ADO = ['alta', 'media_alta', 'media', 'media_baixa', 'baixa'];
  var ST = { nova: 'Nova', interesse: 'Interesse', aplicada: 'Aplicada', entrevista: 'Entrevista', proposta: 'Proposta', recusada: 'Recusada', descartada: 'Descartada' };
  var SAL = { informado: 'informado na vaga', estimativa: 'estimativa', nao_informado: 'não informado' };
  var $ = function (id) { return document.getElementById(id); };
  var guarda = {};
  try { guarda = JSON.parse(localStorage.getItem('caca-vagas') || '{}'); } catch (e) {}
  function salva() { try { localStorage.setItem('caca-vagas', JSON.stringify(guarda)); } catch (e) {} }

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function dataBr(s) { if (!s) return ''; var p = String(s).slice(0, 10).split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : s; }
  function href(u) { return /^https?:\/\//i.test(u || '') ? u : '#'; }

  ADO.forEach(function (a) { $('fAd').insertAdjacentHTML('beforeend', '<option value="' + a + '">' + AD[a] + '</option>'); });
  Object.keys(ST).forEach(function (s) { $('fSt').insertAdjacentHTML('beforeend', '<option value="' + s + '">' + ST[s] + '</option>'); });
  var areas = []; V.forEach(function (v) { if (v.area && areas.indexOf(v.area) < 0) areas.push(v.area); });
  var areaSel = guarda.area || '';
  areas.sort().forEach(function (a) {
    var b = document.createElement('button'); b.className = 'chip'; b.type = 'button'; b.textContent = a;
    b.setAttribute('aria-pressed', a === areaSel); b.onclick = function () { areaSel = areaSel === a ? '' : a; guarda.area = areaSel; salva(); chips(); render(); };
    $('chips').appendChild(b);
  });
  function chips() { Array.prototype.forEach.call($('chips').children, function (b) { b.setAttribute('aria-pressed', b.textContent === areaSel); }); }

  ['busca', 'fAd', 'fSt', 'ordem'].forEach(function (id) { if (guarda[id]) $(id).value = guarda[id]; $(id).addEventListener('input', function () { guarda[id] = $(id).value; salva(); render(); }); });
  $('fFech').checked = !!guarda.fech; $('fFech').addEventListener('change', function () { guarda.fech = $('fFech').checked; salva(); render(); });

  function tema(t) { if (t) document.documentElement.setAttribute('data-theme', t); else document.documentElement.removeAttribute('data-theme'); }
  tema(guarda.tema);
  $('tema').onclick = function () {
    var escuro = guarda.tema ? guarda.tema === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    guarda.tema = escuro ? 'light' : 'dark'; salva(); tema(guarda.tema);
  };

  function toast(m) { var t = $('toast'); t.textContent = m; t.classList.add('on'); setTimeout(function () { t.classList.remove('on'); }, 1600); }
  function copia(txt) {
    function ok() { toast('Copiado: ' + txt); }
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(txt).then(ok, velho); } else velho();
    function velho() { var a = document.createElement('textarea'); a.value = txt; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); ok(); } catch (e) { toast(txt); } a.remove(); }
  }
  $('lista').addEventListener('click', function (e) { var b = e.target.closest('[data-copia]'); if (b) copia(b.getAttribute('data-copia')); });

  function stats() {
    var abertas = V.filter(function (v) { return v.situacao !== 'fechada'; }).length;
    var andando = V.filter(function (v) { return ['aplicada', 'entrevista', 'proposta'].indexOf(v.status) >= 0; }).length;
    var altas = V.filter(function (v) { return v.aderencia === 'alta' && v.situacao !== 'fechada'; }).length;
    $('stats').innerHTML = [[V.length, 'vagas no total'], [abertas, 'não fechadas'], [altas, 'aderência alta'], [andando, 'em andamento']]
      .map(function (s) { return '<div class="stat"><b>' + s[0] + '</b><span>' + s[1] + '</span></div>'; }).join('');
    $('sub').textContent = 'Atualizado em ' + (D.atualizado_em || '');
  }

  function render() {
    var q = $('busca').value.trim().toLowerCase(), fa = $('fAd').value, fs = $('fSt').value, fech = $('fFech').checked, ord = $('ordem').value;
    var vs = V.filter(function (v) {
      if (!fech && (v.situacao === 'fechada' || v.status === 'descartada')) return false;
      if (fa && v.aderencia !== fa) return false;
      if (fs && v.status !== fs) return false;
      if (areaSel && v.area !== areaSel) return false;
      if (q) { var t = [v.empresa, v.cargo, v.motivo, v.falta, v.modalidade, v.local, v.regime, v.beneficios, v.id].join(' ').toLowerCase(); if (t.indexOf(q) < 0) return false; }
      return true;
    });
    vs.sort(function (a, b) {
      if (ord === 'data') return String(b.publicada || '').localeCompare(String(a.publicada || ''));
      if (ord === 'emp') return String(a.empresa || '').localeCompare(String(b.empresa || ''));
      var x = ADO.indexOf(a.aderencia), y = ADO.indexOf(b.aderencia); x = x < 0 ? 9 : x; y = y < 0 ? 9 : y;
      return x - y || String(b.publicada || '').localeCompare(String(a.publicada || ''));
    });
    if (!vs.length) { $('lista').innerHTML = '<div class="vazio">' + (V.length ? 'Nenhuma vaga com esses filtros.' : 'Nenhuma vaga ainda. Peça ao Claude: "pesquisa vagas pra mim".') + '</div>'; return; }
    $('lista').innerHTML = vs.map(function (v) {
      var meta = [v.modalidade, v.local, v.regime, v.nivel, v.publicada ? 'publicada ' + dataBr(v.publicada) : '', v.prazo ? 'prazo ' + dataBr(v.prazo) : ''].filter(Boolean).map(esc).join(' · ');
      var sit = v.situacao === 'fechada' ? 'fechada' : v.situacao === 'aberta' ? 'aberta' : 'não confirmada';
      return '<article class="card' + (v.situacao === 'fechada' ? ' fechada' : '') + '">' +
        '<div class="topo"><span class="empresa">' + esc(v.empresa) + '</span>' +
        (v.area ? '<span class="tag">' + esc(v.area) + '</span>' : '') +
        (v.aderencia ? '<span class="ad ' + esc(v.aderencia) + '">' + (AD[v.aderencia] || esc(v.aderencia)) + '</span>' : '') +
        '<span class="tag">' + sit + (v.conferida_em ? ' em ' + dataBr(v.conferida_em) : '') + '</span></div>' +
        '<div class="cargo">' + esc(v.cargo) + '</div>' +
        (meta ? '<div class="meta">' + meta + '</div>' : '') +
        '<div class="sal">' + esc(v.salario || 'Salário não informado') + (v.salario_tipo ? '<span class="tipo">' + (SAL[v.salario_tipo] || esc(v.salario_tipo)) + '</span>' : '') +
        (v.salario_fonte ? '<div class="meta">fonte: ' + esc(v.salario_fonte) + '</div>' : '') + '</div>' +
        (v.motivo ? '<div class="motivo">' + esc(v.motivo) + '</div>' : '') +
        (v.falta ? '<div class="falta">Falta: ' + esc(v.falta) + '</div>' : '') +
        (v.beneficios ? '<details><summary>Benefícios</summary>' + esc(v.beneficios) + '</details>' : '') +
        (v.notas ? '<details><summary>Notas</summary>' + esc(v.notas).replace(/\n/g, '<br>') + '</details>' : '') +
        '<div class="rodape"><span class="st ' + esc(v.status) + '">' + (ST[v.status] || esc(v.status)) + '</span><span class="id">' + esc(v.id) + '</span>' +
        '<div class="acoes">' +
        (v.curriculo ? '<a class="btn" href="' + esc(v.curriculo) + '">Currículo desta vaga</a>' : '<button class="btn" type="button" data-copia="adapta meu currículo pra vaga ' + esc(v.id) + '">Pedir currículo</button>') +
        '<button class="btn" type="button" data-copia="marca a vaga ' + esc(v.id) + ' como aplicada">Pedir status</button>' +
        '<a class="btn prim" href="' + esc(href(v.url)) + '" target="_blank" rel="noopener">Abrir vaga</a></div></div></article>';
    }).join('');
  }
  stats(); render();
})();
</script>
</body>
</html>
"""


def gerar(dados: dict, pasta: Path) -> Path:
    vagas = []
    for v in dados.get("vagas", []):
        v = dict(v)
        cv = v.get("curriculo")
        if cv:
            p = Path(cv)
            if not p.is_absolute():
                p = (pasta / p).resolve()
            v["curriculo"] = p.as_uri()
        vagas.append(v)
    bruto = json.dumps({"atualizado_em": dados.get("atualizado_em"), "vagas": vagas}, ensure_ascii=False)
    bruto = bruto.replace("</", "<\\/")
    destino = pasta / "painel.html"
    destino.write_text(MODELO.replace("__DADOS__", bruto), encoding="utf-8")
    return destino
