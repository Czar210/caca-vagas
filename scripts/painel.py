"""Gera painel.html: um arquivo só, com os dados dentro, que abre direto no navegador.

Visual inspirado no Metis (metis-eta.vercel.app): escuro por padrão, claro por escolha,
cor de destaque trocável, Space Grotesk nos títulos, grade sutil no fundo.
"""
from __future__ import annotations

import json
from pathlib import Path

MODELO = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de vagas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>
  try {
    var g = JSON.parse(localStorage.getItem('caca-vagas') || '{}');
    if (g.tema) document.documentElement.setAttribute('data-theme', g.tema);
    if (g.cor) document.documentElement.setAttribute('data-color', g.cor);
  } catch (e) {}
</script>
<style>
:root, [data-color="azul"] { --acc: #3B82F6; --acc-2: #2563EB; }
[data-color="roxo"] { --acc: #8B5CF6; --acc-2: #7C3AED; }
[data-color="verde"] { --acc: #10B981; --acc-2: #059669; }
[data-color="vermelho"] { --acc: #EF4444; --acc-2: #DC2626; }
[data-color="dourado"] { --acc: #D4AF37; --acc-2: #B49423; }

:root {
  --bg: #0D0F14; --surface: rgba(20, 24, 38, .6); --surface-solid: #141826; --surface-2: #1B2030;
  --line: #222838; --line-2: #2B3246;
  --ink: #E5E9F2; --ink-2: #C3CAD7; --muted: #8A93A6; --faint: #5A6378;
  --on-acc: #0D0F14;
  --acc-soft: color-mix(in srgb, var(--acc) 10%, transparent);
  --acc-line: color-mix(in srgb, var(--acc) 25%, transparent);
  --acc-ink: color-mix(in srgb, var(--acc) 70%, #fff);
  --grid: rgba(245, 200, 66, .04);
  --glow-1: rgba(245, 200, 66, .16); --glow-2: rgba(91, 227, 212, .10);
  --topo: color-mix(in srgb, #141826 82%, transparent);
  --g: #4ADE80; --g-s: color-mix(in srgb, #4ADE80 12%, transparent);
  --lg: #A3E635; --lg-s: color-mix(in srgb, #A3E635 11%, transparent);
  --y: #FBBF24; --y-s: color-mix(in srgb, #FBBF24 12%, transparent);
  --o: #FB923C; --o-s: color-mix(in srgb, #FB923C 12%, transparent);
  --r: #F87171; --r-s: color-mix(in srgb, #F87171 13%, transparent);
  --cyan: #5BE3D4;
  --shadow: 0 12px 32px rgba(0, 0, 0, .35);
  --display: "Space Grotesk", Inter, system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
  color-scheme: dark;
}
[data-theme="light"] {
  --bg: #F4F6FA; --surface: rgba(255, 255, 255, .85); --surface-solid: #FFFFFF; --surface-2: #ECEFF5;
  --line: #E2E6EE; --line-2: #D5DAE4;
  --ink: #141826; --ink-2: #353C4C; --muted: #657085; --faint: #8D96A9;
  --on-acc: #FFFFFF;
  --acc-soft: color-mix(in srgb, var(--acc) 9%, #fff);
  --acc-line: color-mix(in srgb, var(--acc) 30%, #fff);
  --acc-ink: color-mix(in srgb, var(--acc-2) 82%, #000);
  --grid: rgba(20, 24, 38, .035);
  --glow-1: rgba(245, 200, 66, .18); --glow-2: rgba(14, 159, 144, .10);
  --topo: color-mix(in srgb, #FFFFFF 86%, transparent);
  --g: #18834D; --g-s: #DCF5E6; --lg: #4D7C0F; --lg-s: #ECF7D5; --y: #A96E10; --y-s: #FBEDD0;
  --o: #C2560F; --o-s: #FCE6D4; --r: #BD2C2C; --r-s: #FBE1E0; --cyan: #0E9F90;
  --shadow: 0 8px 24px rgba(16, 21, 34, .08);
  color-scheme: light;
}

* { box-sizing: border-box; }
html { background: var(--bg); overflow-x: clip; }
body { overflow-x: clip; }
body {
  margin: 0; min-height: 100vh; color: var(--ink); background: var(--bg);
  font: 15px/1.5 Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
  background-image: linear-gradient(90deg, var(--grid) 1px, transparent 0), linear-gradient(var(--grid) 1px, transparent 0);
  background-size: 32px 32px;
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; }
button, input, select { font: inherit; color: inherit; }

.topo { position: sticky; top: 0; z-index: 5; background: var(--topo); backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid var(--line); }
.topo .in { max-width: 1120px; margin: 0 auto; padding: 0 16px; height: 56px; display: flex; align-items: center; gap: 14px; }
.marca { display: flex; align-items: center; gap: 10px; font-family: var(--display); font-weight: 700; font-size: 16px; letter-spacing: -.02em; }
.marca .dot { width: 10px; height: 10px; border-radius: 3px; background: var(--acc);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--acc) 22%, transparent), 0 0 14px color-mix(in srgb, var(--acc) 55%, transparent); }
.aparencia { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.cor { width: 13px; height: 13px; border-radius: 50%; border: 0; padding: 0; background: var(--c); cursor: pointer; transition: transform .12s ease; }
.cor:hover { transform: scale(1.15); }
.cor[aria-pressed="true"] { box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--c); }
.icone { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 9px; border: 1px solid var(--line);
  background: var(--surface); cursor: pointer; margin-left: 6px; }
.icone:hover { border-color: var(--acc-line); }
.icone svg { width: 16px; height: 16px; }

.wrap { max-width: 1120px; margin: 0 auto; padding: 0 16px 72px; position: relative; }
.hero { position: relative; isolation: isolate; padding: 44px 0 26px; }
.glow { position: absolute; border-radius: 50%; filter: blur(40px); pointer-events: none; z-index: -1; }
.glow.a { width: 420px; height: 420px; right: -60px; top: -120px; background: radial-gradient(circle, var(--glow-1), transparent 70%); }
.glow.b { width: 340px; height: 340px; left: -140px; top: 120px; background: radial-gradient(circle, var(--glow-2), transparent 70%); }
.pilula { display: inline-flex; align-items: center; gap: 8px; padding: 5px 12px; border-radius: 999px;
  border: 1px solid var(--acc-line); background: var(--acc-soft); color: var(--acc);
  font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
.pilula .pulso { width: 6px; height: 6px; border-radius: 50%; background: var(--acc); box-shadow: 0 0 8px var(--acc); }
h1 { font-family: var(--display); font-size: clamp(32px, 6vw, 52px); line-height: 1.05; font-weight: 700;
  letter-spacing: -.03em; margin: 18px 0 12px; text-wrap: balance; }
h1 em { font-style: normal; color: var(--acc); }
.lead { color: var(--muted); font-size: 16px; max-width: 640px; margin: 0; }

.busca { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 26px; }
.campo { flex: 1 1 300px; display: flex; align-items: center; gap: 10px; min-width: 0; height: 48px; padding: 0 14px;
  border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
.campo:focus-within { border-color: var(--acc); box-shadow: 0 0 0 3px var(--acc-soft); }
.campo svg { width: 16px; height: 16px; color: var(--muted); flex: none; }
.campo input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; font-size: 14px; }
.campo input::placeholder { color: var(--faint); }
.campo kbd { font: 11px var(--mono); color: var(--faint); border: 1px solid var(--line); border-radius: 5px; padding: 1px 5px; }
select { height: 48px; padding: 0 12px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface-solid);
  font-size: 14px; cursor: pointer; }
select:focus { outline: 0; border-color: var(--acc); }
.linha { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 14px; font-size: 12px; color: var(--faint); }
.chip { border: 1px solid var(--line); background: transparent; color: var(--muted); border-radius: 999px; padding: 4px 11px;
  font-size: 12px; cursor: pointer; transition: border-color .15s, color .15s, background .15s; }
.chip:hover { border-color: var(--acc-line); color: var(--ink); }
.chip[aria-pressed="true"] { border-color: var(--acc-line); background: var(--acc-soft); color: var(--acc); }
.chk { display: inline-flex; align-items: center; gap: 7px; margin-left: auto; color: var(--muted); font-size: 13px; cursor: pointer; }
.chk input { accent-color: var(--acc); }

.painel { margin-top: 26px; border: 1px solid var(--line); border-radius: 16px; background: var(--surface);
  display: grid; grid-template-columns: repeat(4, 1fr); }
.painel > div { padding: 18px 20px; }
.painel > div + div { border-left: 1px solid var(--line); }
.rot { font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.val { font-family: var(--display); font-size: 30px; font-weight: 600; letter-spacing: -.02em; line-height: 1.15; margin-top: 4px;
  font-variant-numeric: tabular-nums; }
.val.acc { color: var(--acc); } .val.cy { color: var(--cyan); }

.secao { display: flex; align-items: baseline; justify-content: space-between; margin: 34px 0 12px; }
.secao h2 { font-family: var(--display); font-size: 20px; font-weight: 600; letter-spacing: -.02em; margin: 0; }
.secao span { color: var(--muted); font-size: 13px; }
.lista { display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr)); }
.card { position: relative; display: flex; flex-direction: column; gap: 6px; padding: 18px 18px 14px; border: 1px solid var(--line);
  border-radius: 16px; background: var(--surface); transition: border-color .15s, transform .15s, box-shadow .15s; }
.card:hover { border-color: var(--acc-line); box-shadow: var(--shadow); transform: translateY(-1px); }
.card.alta::before { content: ""; position: absolute; left: 18px; right: 18px; top: -1px; height: 2px; border-radius: 2px;
  background: linear-gradient(90deg, var(--acc), transparent); }
.card.fechada { opacity: .55; }
.topo-card { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.empresa { font-weight: 600; font-size: 14px; color: var(--ink-2); }
.badge { font-size: 10.5px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; border-radius: 999px; padding: 3px 9px; }
.badge.alta { color: var(--g); background: var(--g-s); } .badge.media_alta { color: var(--lg); background: var(--lg-s); }
.badge.media { color: var(--y); background: var(--y-s); } .badge.media_baixa { color: var(--o); background: var(--o-s); }
.badge.baixa { color: var(--r); background: var(--r-s); }
.area { margin-left: auto; font-size: 11px; color: var(--faint); text-transform: uppercase; letter-spacing: .06em; }
.cargo { font-family: var(--display); font-size: 18px; font-weight: 600; letter-spacing: -.015em; line-height: 1.25; margin: 2px 0 0; }
.meta { color: var(--muted); font-size: 13px; }
.sal { margin-top: 6px; padding: 10px 12px; border-radius: 10px; background: var(--surface-2); border: 1px solid var(--line); }
.sal .v { font-family: var(--display); font-weight: 600; font-size: 15px; }
.sal .t { font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--faint); margin-left: 6px; }
.sal .f { font-size: 12px; color: var(--faint); margin-top: 2px; }
.motivo { font-size: 14px; color: var(--ink-2); margin-top: 4px; }
.falta { font-size: 13px; color: var(--muted); }
.falta b { font-weight: 600; color: var(--o); }
details { font-size: 13px; color: var(--muted); }
summary { cursor: pointer; color: var(--faint); list-style: none; }
summary::-webkit-details-marker { display: none; }
summary::before { content: "+ "; color: var(--acc); }
details[open] summary::before { content: "− "; }
details p { margin: 4px 0 0; }
.rodape { margin-top: auto; padding-top: 12px; border-top: 1px solid var(--line); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.st { font-size: 11px; font-weight: 600; border-radius: 999px; padding: 2px 9px; border: 1px solid var(--line-2); color: var(--muted); }
.st.ativo { border-color: var(--acc-line); color: var(--acc); background: var(--acc-soft); }
.sit { font-size: 11px; color: var(--faint); display: inline-flex; align-items: center; gap: 5px; }
.sit::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--faint); }
.sit.aberta::before { background: var(--g); box-shadow: 0 0 6px var(--g); }
.sit.fechada::before { background: var(--r); }
.id { font: 11px var(--mono); color: var(--faint); }
.acoes { margin-left: auto; display: flex; gap: 6px; }
.btn { font-size: 12.5px; font-weight: 500; border-radius: 9px; padding: 6px 10px; border: 1px solid var(--line); background: transparent;
  color: var(--ink-2); cursor: pointer; text-decoration: none; transition: border-color .15s, color .15s; white-space: nowrap; }
.btn:hover { border-color: var(--acc-line); color: var(--ink); }
.btn.prim { background: var(--acc); border-color: var(--acc); color: var(--on-acc); font-weight: 600; }
.btn.prim:hover { background: var(--acc-2); border-color: var(--acc-2); }
.vazio { grid-column: 1 / -1; text-align: center; color: var(--muted); padding: 48px 0; border: 1px dashed var(--line-2); border-radius: 16px; }
.ajuda { margin-top: 32px; color: var(--faint); font-size: 13px; }
.ajuda code { font: 12px var(--mono); color: var(--muted); background: var(--surface-2); border: 1px solid var(--line); border-radius: 6px; padding: 1px 6px; }
.toast { position: fixed; bottom: 20px; left: 50%; transform: translate(-50%, 8px); opacity: 0; pointer-events: none;
  background: var(--surface-solid); color: var(--ink); border: 1px solid var(--acc-line); border-radius: 10px; padding: 9px 14px;
  font-size: 13px; box-shadow: var(--shadow); transition: opacity .2s, transform .2s; max-width: calc(100% - 32px); }
.toast.on { opacity: 1; transform: translate(-50%, 0); }

@media (max-width: 720px) {
  .painel { grid-template-columns: 1fr 1fr; }
  .painel > div:nth-child(3) { border-left: 0; }
  .painel > div:nth-child(n+3) { border-top: 1px solid var(--line); }
  .hero { padding-top: 30px; }
  .chk { margin-left: 0; }
  .aparencia .cor { width: 12px; height: 12px; }
  select { flex: 1 1 140px; }
}
</style>
</head>
<body>
<header class="topo"><div class="in">
  <div class="marca"><span class="dot"></span>caca-vagas</div>
  <div class="aparencia" id="cores" aria-label="Cor de destaque"></div>
  <button class="icone" id="tema" type="button" aria-label="Trocar tema"></button>
</div></header>
<main class="wrap">
  <section class="hero">
    <div class="glow a"></div><div class="glow b"></div>
    <span class="pilula"><span class="pulso"></span><span id="carimbo"></span></span>
    <h1 id="titulo"></h1>
    <p class="lead">Cada vaga com o que bate com você, o que falta, salário e benefícios. Para mudar algo, peça ao Claude e o painel é refeito.</p>
    <div class="busca">
      <label class="campo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input type="search" id="busca" placeholder="Empresa, cargo ou stack" aria-label="Buscar"><kbd>/</kbd></label>
      <select id="fAd" aria-label="Aderência"><option value="">Toda aderência</option></select>
      <select id="fSt" aria-label="Status"><option value="">Todo status</option></select>
      <select id="ordem" aria-label="Ordenar"><option value="ad">Melhor aderência</option><option value="data">Mais recentes</option><option value="emp">Empresa</option></select>
    </div>
    <div class="linha"><span>Áreas:</span><span id="chips" style="display:contents"></span>
      <label class="chk"><input type="checkbox" id="fFech"> mostrar fechadas e descartadas</label></div>
    <div class="painel" id="stats"></div>
  </section>
  <div class="secao"><h2>Vagas</h2><span id="contagem"></span></div>
  <div class="lista" id="lista"></div>
  <p class="ajuda">Peça ao Claude: <code>marca a vaga a1b2c3 como aplicada</code> · <code>atualiza as vagas</code> · <code>adapta meu currículo pra vaga a1b2c3</code></p>
</main>
<div class="toast" id="toast" role="status"></div>
<script type="application/json" id="dados">__DADOS__</script>
<script>
(function () {
  var D = JSON.parse(document.getElementById('dados').textContent);
  var V = D.vagas || [];
  var AD = { alta: 'Alta', media_alta: 'Média alta', media: 'Média', media_baixa: 'Média baixa', baixa: 'Baixa' };
  var ADO = ['alta', 'media_alta', 'media', 'media_baixa', 'baixa'];
  var ST = { nova: 'Nova', interesse: 'Interesse', aplicada: 'Aplicada', entrevista: 'Entrevista', proposta: 'Proposta', recusada: 'Recusada', descartada: 'Descartada' };
  var SAL = { informado: 'informado', estimativa: 'estimativa', nao_informado: 'não informado' };
  var CORES = { azul: '#3B82F6', roxo: '#8B5CF6', verde: '#10B981', vermelho: '#EF4444', dourado: '#D4AF37' };
  var SOL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var LUA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  var $ = function (id) { return document.getElementById(id); };
  var guarda = {};
  try { guarda = JSON.parse(localStorage.getItem('caca-vagas') || '{}'); } catch (e) {}
  function salva() { try { localStorage.setItem('caca-vagas', JSON.stringify(guarda)); } catch (e) {} }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function dataBr(s) { if (!s) return ''; var p = String(s).slice(0, 10).split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : s; }
  function curta(s) { if (!s) return ''; var p = String(s).slice(0, 10).split('-'); return p.length === 3 ? p[2] + '/' + p[1] : s; }
  function href(u) { return /^(https?|file):\/\//i.test(u || '') ? u : '#'; }

  // aparência
  var root = document.documentElement;
  function escuro() { return root.getAttribute('data-theme') !== 'light'; }
  function pintaTema() { $('tema').innerHTML = escuro() ? SOL : LUA; }
  $('tema').onclick = function () { guarda.tema = escuro() ? 'light' : 'dark'; root.setAttribute('data-theme', guarda.tema); salva(); pintaTema(); };
  pintaTema();
  Object.keys(CORES).forEach(function (k) {
    var b = document.createElement('button'); b.className = 'cor'; b.type = 'button'; b.style.setProperty('--c', CORES[k]);
    b.setAttribute('aria-label', 'Destaque ' + k); b.title = k;
    b.onclick = function () { guarda.cor = k; root.setAttribute('data-color', k); salva(); pintaCores(); };
    $('cores').appendChild(b);
  });
  function pintaCores() { var atual = guarda.cor || 'azul'; Array.prototype.forEach.call($('cores').children, function (b) { b.setAttribute('aria-pressed', b.title === atual); }); }
  pintaCores();

  // filtros
  ADO.forEach(function (a) { $('fAd').insertAdjacentHTML('beforeend', '<option value="' + a + '">' + AD[a] + '</option>'); });
  Object.keys(ST).forEach(function (s) { $('fSt').insertAdjacentHTML('beforeend', '<option value="' + s + '">' + ST[s] + '</option>'); });
  var areas = []; V.forEach(function (v) { if (v.area && areas.indexOf(v.area) < 0) areas.push(v.area); });
  var areaSel = guarda.area || '';
  areas.sort().forEach(function (a) {
    var b = document.createElement('button'); b.className = 'chip'; b.type = 'button'; b.textContent = a;
    b.onclick = function () { areaSel = areaSel === a ? '' : a; guarda.area = areaSel; salva(); chips(); render(); };
    $('chips').appendChild(b);
  });
  function chips() { Array.prototype.forEach.call($('chips').children, function (b) { b.setAttribute('aria-pressed', b.textContent === areaSel); }); }
  chips();
  ['busca', 'fAd', 'fSt', 'ordem'].forEach(function (id) { if (guarda[id]) $(id).value = guarda[id]; $(id).addEventListener('input', function () { guarda[id] = $(id).value; salva(); render(); }); });
  $('fFech').checked = !!guarda.fech; $('fFech').addEventListener('change', function () { guarda.fech = $('fFech').checked; salva(); render(); });
  document.addEventListener('keydown', function (e) { if (e.key === '/' && document.activeElement !== $('busca')) { e.preventDefault(); $('busca').focus(); } });

  // copiar pedido
  function toast(m) { var t = $('toast'); t.textContent = m; t.classList.add('on'); clearTimeout(toast.t); toast.t = setTimeout(function () { t.classList.remove('on'); }, 1800); }
  function copia(txt) {
    function ok() { toast('Copiado: ' + txt); }
    function velho() { var a = document.createElement('textarea'); a.value = txt; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); ok(); } catch (e) { toast(txt); } a.remove(); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(txt).then(ok, velho); else velho();
  }
  $('lista').addEventListener('click', function (e) { var b = e.target.closest('[data-copia]'); if (b) copia(b.getAttribute('data-copia')); });

  // topo e números
  var vivas = V.filter(function (v) { return v.situacao !== 'fechada' && v.status !== 'descartada'; });
  var altas = vivas.filter(function (v) { return v.aderencia === 'alta'; }).length;
  var andando = V.filter(function (v) { return ['aplicada', 'entrevista', 'proposta'].indexOf(v.status) >= 0; }).length;
  var confirmadas = V.filter(function (v) { return v.situacao === 'aberta'; }).length;
  var comSal = V.filter(function (v) { return v.salario_tipo === 'informado'; }).length;
  $('carimbo').textContent = 'Painel · atualizado ' + (D.atualizado_em ? dataBr(D.atualizado_em.slice(0, 10)) + ' ' + D.atualizado_em.slice(11, 16) : '');
  $('titulo').innerHTML = vivas.length + ' vagas na mesa, <em>' + altas + ' com aderência alta</em>.';
  $('stats').innerHTML = [
    ['Abertas confirmadas', confirmadas, ''], ['Aderência alta', altas, 'acc'], ['Em andamento', andando, 'cy'], ['Salário informado', comSal + ' de ' + V.length, '']
  ].map(function (s) { return '<div><div class="rot">' + s[0] + '</div><div class="val ' + s[2] + '">' + s[1] + '</div></div>'; }).join('');

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
    $('contagem').textContent = vs.length + (vs.length === 1 ? ' vaga' : ' vagas');
    if (!vs.length) { $('lista').innerHTML = '<div class="vazio">' + (V.length ? 'Nenhuma vaga com esses filtros.' : 'Nenhuma vaga ainda. Peça ao Claude: pesquisa vagas pra mim.') + '</div>'; return; }
    $('lista').innerHTML = vs.map(function (v) {
      var meta = [v.modalidade, v.local && v.local !== v.modalidade ? v.local : '', v.regime, v.nivel,
        v.publicada ? 'publicada ' + curta(v.publicada) : '', v.prazo ? 'até ' + curta(v.prazo) : ''].filter(Boolean).map(esc).join(' · ');
      var sit = v.situacao === 'fechada' ? 'fechada' : v.situacao === 'aberta' ? 'aberta' : 'não confirmada';
      var ativo = ['interesse', 'aplicada', 'entrevista', 'proposta'].indexOf(v.status) >= 0;
      return '<article class="card ' + esc(v.aderencia) + (v.situacao === 'fechada' ? ' fechada' : '') + '">' +
        '<div class="topo-card"><span class="empresa">' + esc(v.empresa) + '</span>' +
        (v.aderencia ? '<span class="badge ' + esc(v.aderencia) + '">' + (AD[v.aderencia] || esc(v.aderencia)) + '</span>' : '') +
        (v.area ? '<span class="area">' + esc(v.area) + '</span>' : '') + '</div>' +
        '<h3 class="cargo">' + esc(v.cargo) + '</h3>' +
        (meta ? '<div class="meta">' + meta + '</div>' : '') +
        '<div class="sal"><span class="v">' + esc(v.salario || 'Salário não informado') + '</span>' +
        (v.salario && v.salario_tipo ? '<span class="t">' + (SAL[v.salario_tipo] || esc(v.salario_tipo)) + '</span>' : '') +
        (v.salario_fonte ? '<div class="f">fonte: ' + esc(v.salario_fonte) + '</div>' : '') + '</div>' +
        (v.motivo ? '<div class="motivo">' + esc(v.motivo) + '</div>' : '') +
        (v.falta ? '<div class="falta"><b>Falta</b> ' + esc(v.falta) + '</div>' : '') +
        (v.beneficios ? '<details><summary>Benefícios</summary><p>' + esc(v.beneficios) + '</p></details>' : '') +
        (v.notas ? '<details><summary>Notas</summary><p>' + esc(v.notas).replace(/\n/g, '<br>') + '</p></details>' : '') +
        '<div class="rodape"><span class="st' + (ativo ? ' ativo' : '') + '">' + (ST[v.status] || esc(v.status)) + '</span>' +
        '<span class="sit ' + (v.situacao || '') + '">' + sit + '</span><span class="id">' + esc(v.id) + '</span>' +
        '<div class="acoes">' +
        (v.curriculo ? '<a class="btn" href="' + esc(href(v.curriculo)) + '">Currículo</a>' : '<button class="btn" type="button" data-copia="adapta meu currículo pra vaga ' + esc(v.id) + '">Pedir currículo</button>') +
        '<a class="btn prim" href="' + esc(href(v.url)) + '" target="_blank" rel="noopener">Abrir</a></div></div></article>';
    }).join('');
  }
  render();
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
