"""Gera painel.html: um arquivo só, com os dados dentro, que abre direto no navegador.

Duas telas: Vagas (lista densa com painel de detalhe) e Você (o que está em candidato/).
Visual inspirado no Linear: quase preto, bordas finas, acento índigo, teclado primeiro.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------- leitura de candidato/

META_RE = re.compile(r"^[-*]\s+([A-Za-zÀ-ÿ0-9 /().]{1,32}):\s+(.+)$")


def ler_md(caminho: Path, base: Path) -> dict:
    """Markdown simples em blocos: título, metadados (- Chave: valor) e seções ## com
    citações, listas, listas numeradas, tabelas, rótulos ### e parágrafos."""
    doc = {"caminho": caminho.relative_to(base).as_posix(), "titulo": "", "meta": [], "secoes": []}
    secao = {"titulo": "", "blocos": []}
    doc["secoes"].append(secao)
    para: list[str] = []
    cit: list[str] = []
    tabela: list[list[str]] = []

    def fecha():
        if para:
            secao["blocos"].append({"tipo": "texto", "texto": " ".join(para)})
            para.clear()
        if cit:
            secao["blocos"].append({"tipo": "citacao", "texto": " ".join(cit)})
            cit.clear()
        if tabela:
            secao["blocos"].append({"tipo": "tabela", "cab": tabela[0], "linhas": tabela[1:]})
            tabela.clear()

    def item(tipo, texto):
        b = secao["blocos"]
        if b and b[-1]["tipo"] == tipo:
            b[-1]["itens"].append(texto)
        else:
            b.append({"tipo": tipo, "itens": [texto]})

    for bruta in caminho.read_text(encoding="utf-8").splitlines():
        s = bruta.strip()
        if not s:
            fecha()
            continue
        if s.startswith("# ") and not doc["titulo"]:
            fecha()
            doc["titulo"] = s[2:].strip()
            continue
        if s.startswith("## "):
            fecha()
            secao = {"titulo": s[3:].strip(), "blocos": []}
            doc["secoes"].append(secao)
            continue
        if s.startswith("### "):
            fecha()
            secao["blocos"].append({"tipo": "rotulo", "texto": s[4:].strip()})
            continue
        if s.startswith(">"):
            if para or tabela:
                fecha()
            t = s[1:].strip()
            if t:
                cit.append(t)
            continue
        if s.startswith("|"):
            if para or cit:
                fecha()
            celulas = [c.strip() for c in s.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in celulas):
                tabela.append(celulas)
            continue
        m = META_RE.match(s)
        if m and not secao["titulo"]:
            fecha()
            doc["meta"].append([m.group(1), m.group(2)])
            continue
        if re.match(r"^[-*•]\s+", s):
            fecha()
            item("lista", re.sub(r"^[-*•]\s+", "", s))
            continue
        if re.match(r"^\d+\.\s+", s):
            fecha()
            t = re.sub(r"^\d+\.\s+", "", s)
            if t:
                item("numerada", t)
            continue
        if cit or tabela:
            fecha()
        para.append(s)
    fecha()
    doc["secoes"] = [x for x in doc["secoes"] if x["titulo"] or x["blocos"]]
    return doc


def ler_candidato(pasta: Path) -> dict | None:
    c = pasta / "candidato"
    if not c.exists():
        return None

    def recencia(doc: dict) -> int:
        texto = " ".join(v for _, v in doc["meta"]).lower()
        if "até hoje" in texto or "atual" in texto:
            return 9999
        anos = [int(a) for a in re.findall(r"\b(19\d\d|20\d\d)\b", texto)]
        return max(anos) if anos else 0

    def docs(sub: str) -> list[dict]:
        """Mais recente primeiro; dentro de uma pasta (ex.: empresa), o README dela vem antes dos filhos."""
        d = c / sub
        if not d.exists():
            return []
        arquivos = [p for p in d.rglob("*.md") if not any(x.startswith("_") for x in p.relative_to(d).parts)]
        lidos = [(p.relative_to(d).parts, ler_md(p, c)) for p in arquivos]
        grupos: dict[str, list] = {}
        for partes, doc in lidos:
            grupos.setdefault(partes[0] if len(partes) > 1 else partes[0], []).append((partes, doc))
        def chave_item(item):
            partes, doc = item
            return (0 if partes[-1].lower() == "readme.md" and len(partes) <= 2 else 1, -recencia(doc), doc["titulo"])
        ordem = sorted(grupos.values(), key=lambda g: (-max(recencia(doc) for _, doc in g), g[0][1]["titulo"]))
        return [doc for g in ordem for _, doc in sorted(g, key=chave_item)]

    def um(rel: str):
        p = c / rel
        return ler_md(p, c) if p.exists() else None

    return {
        "experiencias": docs("experiencias"),
        "projetos": docs("projetos"),
        "formacao": docs("formacao"),
        "certificacoes": docs("certificacoes"),
        "habilidades": um("contexto/habilidades.md"),
        "voz": um("voz.md"),
    }


def ler_contato(pasta: Path) -> dict:
    p = pasta / "perfil.md"
    if not p.exists():
        return {}
    d = ler_md(p, pasta)
    out = {}
    for s in d["secoes"]:
        if s["titulo"].lower().startswith("contato"):
            for b in s["blocos"]:
                for it in b.get("itens", []):
                    if ":" in it:
                        k, v = it.split(":", 1)
                        out[k.strip().lower()] = v.strip()
        if s["titulo"].lower().startswith("quem eu sou"):
            out["quem"] = " ".join(b.get("texto", "") for b in s["blocos"] if b["tipo"] == "texto")
    return out


# ---------------------------------------------------------------- página

MODELO = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de vagas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>
  try { var g = JSON.parse(localStorage.getItem('caca-vagas') || '{}'); if (g.tema) document.documentElement.setAttribute('data-theme', g.tema); } catch (e) {}
</script>
<style>
:root {
  --bg: #08090A; --side: #0E0F11; --panel: #0F1012; --row-h: #16171A; --row-s: #1B1C21; --raised: #17181B;
  --line: #1F2023; --line-2: #2A2B30; --ink: #F7F8F8; --ink-2: #D0D6E0; --ink-3: #8A8F98; --ink-4: #62666D;
  --acc: #5E6AD2; --acc-2: #7C85E5; --acc-soft: rgba(94, 106, 210, .14); --acc-ink: #A4ABF0;
  --g: #4CB782; --y: #F2C94C; --o: #F2994A; --r: #EB5757; --b: #4EA7FC; --v: #8F7EE7;
  --mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
  --shadow: 0 16px 48px rgba(0, 0, 0, .5), 0 0 0 1px var(--line-2);
  color-scheme: dark;
}
[data-theme="light"] {
  --bg: #FFFFFF; --side: #F7F7F8; --panel: #FFFFFF; --row-h: #F4F4F6; --row-s: #EEEFFC; --raised: #FAFAFB;
  --line: #EBEBEE; --line-2: #DEDEE3; --ink: #1B1B1F; --ink-2: #3C3C43; --ink-3: #6B6F76; --ink-4: #9A9DA3;
  --acc: #5E6AD2; --acc-2: #4D59C2; --acc-soft: rgba(94, 106, 210, .10); --acc-ink: #4D59C2;
  --g: #1F9D60; --y: #B88A00; --o: #D9730D; --r: #D63B3B; --b: #2D7FD6; --v: #6E5BD6;
  --shadow: 0 16px 48px rgba(20, 20, 40, .14), 0 0 0 1px var(--line-2);
  color-scheme: light;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
html, body { height: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 13px/1.5 Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased; letter-spacing: -.005em; overflow: hidden; }
button, input, select { font: inherit; color: inherit; }
a { color: inherit; text-decoration: none; }
::selection { background: var(--acc-soft); }

.app { display: grid; grid-template-columns: 224px 1fr; height: 100vh; }
.side { background: var(--side); border-right: 1px solid var(--line); display: flex; flex-direction: column; padding: 10px 8px; gap: 2px; min-width: 0; }
.ws { display: flex; align-items: center; gap: 8px; padding: 6px 8px 12px; font-weight: 600; font-size: 13px; }
.ws .logo { width: 20px; height: 20px; border-radius: 5px; background: linear-gradient(135deg, var(--acc), #8B5CF6); display: grid; place-items: center; color: #fff; font-size: 11px; font-weight: 600; }
.nav { display: flex; align-items: center; gap: 9px; padding: 5px 8px; border-radius: 6px; color: var(--ink-2); cursor: pointer; border: 0; background: none; width: 100%; text-align: left; }
.nav:hover { background: var(--row-h); }
.nav[aria-current="true"] { background: var(--row-s); color: var(--ink); }
.nav svg { width: 15px; height: 15px; color: var(--ink-3); flex: none; }
.nav .n { margin-left: auto; color: var(--ink-4); font-size: 12px; font-variant-numeric: tabular-nums; }
.grupo { color: var(--ink-4); font-size: 11.5px; font-weight: 500; padding: 14px 8px 4px; }
.side .fim { margin-top: auto; display: flex; gap: 6px; padding: 8px; align-items: center; color: var(--ink-4); font-size: 11.5px; }
.kbd { font: 11px var(--mono); color: var(--ink-3); border: 1px solid var(--line-2); border-radius: 4px; padding: 0 4px; background: var(--raised); }

.main { display: flex; flex-direction: column; min-width: 0; height: 100vh; }
.barra { height: 46px; flex: none; display: flex; align-items: center; gap: 10px; padding: 0 16px; border-bottom: 1px solid var(--line); }
.barra h1 { font-size: 13px; font-weight: 500; margin: 0; white-space: nowrap; }
.barra .sub { color: var(--ink-4); white-space: nowrap; }
.busca { margin-left: auto; display: flex; align-items: center; gap: 6px; height: 28px; padding: 0 8px; border: 1px solid var(--line-2); border-radius: 6px; background: var(--raised); width: 240px; min-width: 0; }
.busca svg { width: 13px; height: 13px; color: var(--ink-4); flex: none; }
.busca input { border: 0; outline: 0; background: none; flex: 1; min-width: 0; }
.busca input::placeholder { color: var(--ink-4); }
.icone { width: 28px; height: 28px; display: grid; place-items: center; border-radius: 6px; border: 1px solid transparent; background: none; color: var(--ink-3); cursor: pointer; flex: none; }
.icone:hover { background: var(--row-h); color: var(--ink); }
.icone svg { width: 15px; height: 15px; }
.filtros { flex: none; display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-bottom: 1px solid var(--line); overflow-x: auto; scrollbar-width: none; }
.filtros::-webkit-scrollbar { display: none; }
.f { display: inline-flex; align-items: center; gap: 6px; height: 24px; padding: 0 9px; border-radius: 6px; border: 1px dashed var(--line-2); background: none; color: var(--ink-3); cursor: pointer; white-space: nowrap; font-size: 12px; }
.f:hover { color: var(--ink); border-color: var(--ink-4); }
.f[aria-pressed="true"] { border-style: solid; border-color: transparent; background: var(--acc-soft); color: var(--acc-ink); }
.f select { background: none; border: 0; outline: 0; color: inherit; cursor: pointer; }
.f select option { background: var(--panel); color: var(--ink); }

.corpo { flex: 1; display: flex; min-height: 0; }
.lista { flex: 1; overflow-y: auto; min-width: 0; }
.grp { position: sticky; top: 0; z-index: 1; display: flex; align-items: center; gap: 8px; height: 34px; padding: 0 16px; background: var(--side); border-bottom: 1px solid var(--line); font-weight: 500; font-size: 12.5px; }
.grp .n { color: var(--ink-4); font-weight: 400; }
.linha { display: grid; grid-template-columns: 16px 58px minmax(80px, 150px) minmax(180px, 1fr) minmax(0, max-content) 48px; align-items: center; gap: 12px; height: 38px; padding: 0 16px; border-bottom: 1px solid var(--line); cursor: pointer; }
.linha:hover { background: var(--row-h); }
.linha[aria-selected="true"] { background: var(--row-s); box-shadow: inset 2px 0 0 var(--acc); }
.linha.fechada { opacity: .5; }
.linha .id { font: 11.5px var(--mono); color: var(--ink-4); }
.linha .emp { color: var(--ink-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.linha .cargo { color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.linha .tags { display: flex; gap: 6px; align-items: center; min-width: 0; overflow: hidden; justify-content: flex-end; }
.linha .tags .chip { max-width: 170px; overflow: hidden; text-overflow: ellipsis; flex-shrink: 1; }
.corpo.com-det .linha { grid-template-columns: 16px 52px minmax(70px, 120px) minmax(0, 1fr) 44px; }
.corpo.com-det .linha .tags { display: none; }
.linha .data { color: var(--ink-4); text-align: right; font-size: 12px; white-space: nowrap; font-variant-numeric: tabular-nums; }
.chip { display: inline-flex; align-items: center; gap: 5px; height: 20px; padding: 0 7px; border: 1px solid var(--line-2); border-radius: 999px; color: var(--ink-3); font-size: 11.5px; white-space: nowrap; }
.chip i { width: 7px; height: 7px; border-radius: 50%; background: var(--ink-4); }
.chip.sal { font-variant-numeric: tabular-nums; }
.st svg { width: 14px; height: 14px; display: block; }
.vazio { color: var(--ink-3); text-align: center; padding: 64px 16px; }

.det { width: min(560px, 46%); flex: none; border-left: 1px solid var(--line); background: var(--panel); overflow-y: auto; display: none; }
.det.on { display: block; }
.det .topo { position: sticky; top: 0; display: flex; align-items: center; gap: 8px; height: 46px; padding: 0 16px; border-bottom: 1px solid var(--line); background: var(--panel); z-index: 1; }
.det .topo .id { font: 12px var(--mono); color: var(--ink-3); }
.det .topo .acoes { margin-left: auto; display: flex; gap: 6px; }
.det .conteudo { padding: 20px 24px 48px; }
.det h2 { font-size: 20px; font-weight: 600; letter-spacing: -.02em; margin: 0 0 4px; line-height: 1.3; }
.det .empresa { color: var(--ink-3); font-size: 13.5px; margin-bottom: 18px; }
.props { display: grid; grid-template-columns: 110px 1fr; gap: 7px 12px; padding: 14px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); margin-bottom: 20px; }
.props dt { color: var(--ink-4); }
.props dd { margin: 0; color: var(--ink-2); display: flex; align-items: center; gap: 6px; min-width: 0; }
.bloco { margin: 0 0 20px; }
.bloco h3 { font-size: 12px; font-weight: 500; color: var(--ink-3); margin: 0 0 8px; }
.bloco p { margin: 0; color: var(--ink-2); line-height: 1.6; }
.coment { display: grid; grid-template-columns: 22px 1fr; gap: 10px; padding: 12px 0; border-top: 1px solid var(--line); }
.coment:first-of-type { border-top: 0; padding-top: 0; }
.coment .av { width: 22px; height: 22px; border-radius: 50%; background: #D97757; color: #fff; display: grid; place-items: center; font-size: 11px; font-weight: 600; }
.coment .quem { font-size: 12px; color: var(--ink-3); margin-bottom: 2px; }
.coment .quem b { color: var(--ink); font-weight: 500; }
.coment p { margin: 0; color: var(--ink-2); line-height: 1.6; }
.semcoment { color: var(--ink-4); font-style: italic; }
.btn { height: 28px; display: inline-flex; align-items: center; gap: 6px; padding: 0 10px; border-radius: 6px; border: 1px solid var(--line-2); background: var(--raised); color: var(--ink-2); cursor: pointer; font-size: 12.5px; white-space: nowrap; }
.btn:hover { color: var(--ink); border-color: var(--ink-4); }
.btn.prim { background: var(--acc); border-color: var(--acc); color: #fff; }
.btn.prim:hover { background: var(--acc-2); border-color: var(--acc-2); }

/* Você */
.voce { flex: 1; overflow-y: auto; }
.voce .wrap { max-width: 860px; margin: 0 auto; padding: 32px 24px 80px; }
.voce .cab h2 { font-size: 22px; font-weight: 600; letter-spacing: -.02em; margin: 0; }
.voce .cab p { color: var(--ink-3); margin: 6px 0 0; max-width: 680px; line-height: 1.6; }
.voce .cab .contato { color: var(--ink-4); margin-top: 8px; font-size: 12.5px; }
.tabs { display: flex; gap: 2px; margin: 24px 0 18px; border-bottom: 1px solid var(--line); overflow-x: auto; scrollbar-width: none; }
.tab { border: 0; background: none; padding: 8px 10px; color: var(--ink-3); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; white-space: nowrap; }
.tab:hover { color: var(--ink); }
.tab[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--acc); }
.tab .n { color: var(--ink-4); margin-left: 4px; }
.doc { border: 1px solid var(--line); border-radius: 10px; background: var(--panel); margin-bottom: 12px; overflow: hidden; }
.doc > summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 10px; padding: 12px 16px; }
.doc > summary::-webkit-details-marker { display: none; }
.doc > summary .t { font-weight: 500; font-size: 13.5px; }
.doc > summary .m { color: var(--ink-4); margin-left: auto; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 45%; }
.doc > summary .seta { color: var(--ink-4); transition: transform .15s; }
.doc[open] > summary .seta { transform: rotate(90deg); }
.doc .in { padding: 4px 16px 16px; border-top: 1px solid var(--line); }
.doc .meta { display: grid; grid-template-columns: 130px 1fr; gap: 4px 12px; padding: 12px 0; color: var(--ink-2); }
.doc .meta dt { color: var(--ink-4); }
.doc .meta dd { margin: 0; }
.sec { margin-top: 14px; }
.sec h4 { margin: 0 0 8px; font-size: 12px; font-weight: 500; color: var(--ink-3); }
.sec.minhas h4 { color: var(--acc-ink); }
.sec.rasc { border: 1px dashed var(--o); border-radius: 8px; padding: 10px 12px; }
.sec.rasc h4 { color: var(--o); }
.cit { margin: 0 0 8px; padding: 2px 0 2px 12px; border-left: 2px solid var(--acc); color: var(--ink); line-height: 1.6; }
.sec ul, .sec ol { margin: 0; padding-left: 18px; color: var(--ink-2); line-height: 1.6; }
.sec li { margin: 2px 0; }
.sec p { margin: 0 0 6px; color: var(--ink-2); line-height: 1.6; }
.sec .rot { font-weight: 500; color: var(--ink-2); margin: 10px 0 4px; }
table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
th { text-align: left; font-weight: 500; color: var(--ink-4); padding: 6px 8px; border-bottom: 1px solid var(--line); white-space: nowrap; }
td { padding: 6px 8px; border-bottom: 1px solid var(--line); color: var(--ink-2); vertical-align: top; }
tr:last-child td { border-bottom: 0; }
.tipo { font-size: 11px; padding: 1px 6px; border-radius: 4px; background: var(--row-s); color: var(--ink-3); white-space: nowrap; }
.tipo.doc-u { background: rgba(76, 183, 130, .14); color: var(--g); }
.tipo.inf { background: rgba(242, 201, 76, .14); color: var(--y); }
.curso { display: grid; grid-template-columns: 1fr auto; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--line); }
.curso:last-child { border-bottom: 0; }
.curso .q { color: var(--ink-4); font: 11.5px var(--mono); white-space: nowrap; }
.notas-off .curso .nota { display: none; }
.aviso { color: var(--ink-4); font-size: 12px; margin: 0 0 14px; }
.toggle { display: inline-flex; align-items: center; gap: 6px; color: var(--ink-3); cursor: pointer; font-size: 12px; }
.toggle input { accent-color: var(--acc); }

.toast { position: fixed; bottom: 18px; left: 50%; transform: translate(-50%, 8px); opacity: 0; pointer-events: none; background: var(--raised); color: var(--ink);
  border-radius: 8px; padding: 8px 12px; box-shadow: var(--shadow); transition: opacity .15s, transform .15s; max-width: calc(100% - 32px); z-index: 20; }
.toast.on { opacity: 1; transform: translate(-50%, 0); }

@media (max-width: 860px) {
  body { overflow: auto; }
  .app { grid-template-columns: 1fr; grid-template-rows: auto 1fr; height: auto; min-height: 100vh; }
  .side { flex-direction: row; align-items: center; padding: 6px 8px; border-right: 0; border-bottom: 1px solid var(--line); overflow-x: auto; }
  .ws { padding: 0 8px 0 4px; }
  .grupo, .side .vistas, .side .fim { display: none; }
  .nav { width: auto; white-space: nowrap; }
  .main { height: auto; }
  .corpo, .lista, .voce { overflow: visible; }
  .busca { width: auto; flex: 1; }
  .barra .sub { display: none; }
  .linha { grid-template-columns: 16px minmax(0, 1fr) auto; height: auto; padding: 9px 16px; row-gap: 2px; }
  .linha .id, .linha .tags { display: none; }
  .linha .emp { grid-column: 2; grid-row: 1; font-size: 12px; color: var(--ink-3); }
  .linha .cargo { grid-column: 2; grid-row: 2; white-space: normal; }
  .linha .data { grid-column: 3; grid-row: 1; }
  .linha .st { grid-row: 1 / span 2; }
  .det { position: fixed; inset: 0; width: 100%; z-index: 10; border: 0; }
  .props { grid-template-columns: 96px 1fr; }
  .voce .wrap { padding: 20px 16px 64px; }
  .doc .meta { grid-template-columns: 1fr; }
  .doc .meta dt { margin-top: 6px; }
}
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="ws"><span class="logo">c</span><span id="wsnome">caca-vagas</span></div>
    <button class="nav" data-tela="vagas" type="button"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="12" height="10" rx="2"/><path d="M2 6.5h12"/></svg>Vagas<span class="n" id="nVagas"></span></button>
    <button class="nav" data-tela="voce" type="button"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="5.5" r="2.5"/><path d="M3 13.5c.8-2.4 2.7-3.5 5-3.5s4.2 1.1 5 3.5"/></svg>Você</button>
    <div class="grupo">Vistas</div>
    <div class="vistas" id="vistas"></div>
    <div class="fim"><span class="kbd">j</span><span class="kbd">k</span> navegar <span class="kbd">/</span> buscar</div>
  </aside>
  <section class="main">
    <header class="barra">
      <h1 id="titulo">Vagas</h1><span class="sub" id="sub"></span>
      <label class="busca" id="buscaWrap"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="7" cy="7" r="4.5"/><path d="m13.5 13.5-3-3"/></svg><input id="busca" type="search" placeholder="Buscar" aria-label="Buscar"><span class="kbd">/</span></label>
      <button class="icone" id="tema" type="button" aria-label="Trocar tema"></button>
    </header>
    <div id="telaVagas" class="corpo" style="flex-direction:column">
      <div class="filtros" id="filtros"></div>
      <div class="corpo">
        <div class="lista" id="lista" role="listbox" aria-label="Vagas"></div>
        <aside class="det" id="det" aria-label="Detalhe da vaga"></aside>
      </div>
    </div>
    <div id="telaVoce" class="voce" hidden></div>
  </section>
</div>
<div class="toast" id="toast" role="status"></div>
<script type="application/json" id="dados">__DADOS__</script>
<script>
(function () {
  var D = JSON.parse(document.getElementById('dados').textContent);
  var V = D.vagas || [], CAND = D.candidato, CONT = D.contato || {};
  var AD = { alta: 'Alta', media_alta: 'Média alta', media: 'Média', media_baixa: 'Média baixa', baixa: 'Baixa' };
  var ADO = ['alta', 'media_alta', 'media', 'media_baixa', 'baixa'];
  var ADC = { alta: 'var(--g)', media_alta: '#8BC34A', media: 'var(--y)', media_baixa: 'var(--o)', baixa: 'var(--r)' };
  var ST = { nova: 'Nova', interesse: 'Interesse', aplicada: 'Aplicada', entrevista: 'Entrevista', proposta: 'Proposta', recusada: 'Recusada', descartada: 'Descartada' };
  var SAL = { informado: 'informado na vaga', estimativa: 'estimativa', nao_informado: 'não informado' };
  var $ = function (id) { return document.getElementById(id); };
  var guarda = {}; try { guarda = JSON.parse(localStorage.getItem('caca-vagas') || '{}'); } catch (e) {}
  function salva() { try { localStorage.setItem('caca-vagas', JSON.stringify(guarda)); } catch (e) {} }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function inl(s) { return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*(.+?)\*\*/g, '$1').replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener" style="color:var(--acc-ink)">$1</a>'); }
  function curta(s) { if (!s) return ''; var p = String(s).slice(0, 10).split('-'); return p.length === 3 ? p[2] + '/' + p[1] : s; }
  function longa(s) { if (!s) return ''; var p = String(s).slice(0, 10).split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : s; }
  function href(u) { return /^(https?|file):\/\//i.test(u || '') ? u : '#'; }

  function icone(st) {
    var c = { nova: 'var(--ink-4)', interesse: 'var(--y)', aplicada: 'var(--acc)', entrevista: 'var(--b)', proposta: 'var(--g)', recusada: 'var(--ink-4)', descartada: 'var(--ink-4)' }[st] || 'var(--ink-4)';
    if (st === 'nova') return '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="' + c + '" stroke-width="1.5" stroke-dasharray="2 2"/></svg>';
    if (st === 'interesse') return '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="' + c + '" stroke-width="1.5"/></svg>';
    if (st === 'aplicada') return '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="' + c + '" stroke-width="1.5"/><path d="M7 7V3.2A3.8 3.8 0 0 1 10.8 7Z" fill="' + c + '"/></svg>';
    if (st === 'entrevista') return '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="5.5" fill="none" stroke="' + c + '" stroke-width="1.5"/><path d="M7 7V3.2A3.8 3.8 0 1 1 3.2 7Z" fill="' + c + '"/></svg>';
    if (st === 'proposta') return '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="6" fill="' + c + '"/><path d="m4.5 7.2 1.7 1.7 3.4-3.6" fill="none" stroke="#fff" stroke-width="1.5"/></svg>';
    return '<svg viewBox="0 0 14 14"><circle cx="7" cy="7" r="6" fill="' + c + '"/><path d="m5 5 4 4m0-4-4 4" stroke="var(--bg)" stroke-width="1.5"/></svg>';
  }
  function adChip(a) { return a ? '<span class="chip"><i style="background:' + (ADC[a] || 'var(--ink-4)') + '"></i>' + (AD[a] || esc(a)) + '</span>' : ''; }

  // tema
  var root = document.documentElement;
  function escuro() { return root.getAttribute('data-theme') !== 'light'; }
  var SOL = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1 1M11.6 11.6l1 1M3.4 12.6l1-1M11.6 4.4l1-1"/></svg>';
  var LUA = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13.5 9.5A5.5 5.5 0 1 1 6.5 2.5a4.5 4.5 0 0 0 7 7z"/></svg>';
  function pintaTema() { $('tema').innerHTML = escuro() ? SOL : LUA; }
  $('tema').onclick = function () { guarda.tema = escuro() ? 'light' : 'dark'; root.setAttribute('data-theme', guarda.tema); salva(); pintaTema(); };
  pintaTema();

  function toast(m) { var t = $('toast'); t.textContent = m; t.classList.add('on'); clearTimeout(toast.t); toast.t = setTimeout(function () { t.classList.remove('on'); }, 1800); }
  function copia(txt) {
    function ok() { toast('Copiado: ' + txt); }
    function velho() { var a = document.createElement('textarea'); a.value = txt; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); ok(); } catch (e) { toast(txt); } a.remove(); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(txt).then(ok, velho); else velho();
  }
  document.addEventListener('click', function (e) { var b = e.target.closest('[data-copia]'); if (b) copia(b.getAttribute('data-copia')); });

  // ---------------------------------------------------------- vagas
  var VISTAS = [
    ['abertas', 'Abertas', function (v) { return v.situacao !== 'fechada' && v.status !== 'descartada'; }],
    ['alta', 'Aderência alta', function (v) { return v.aderencia === 'alta' && v.situacao !== 'fechada' && v.status !== 'descartada'; }],
    ['andamento', 'Em andamento', function (v) { return ['interesse', 'aplicada', 'entrevista', 'proposta'].indexOf(v.status) >= 0; }],
    ['fechadas', 'Fechadas e descartadas', function (v) { return v.situacao === 'fechada' || v.status === 'descartada' || v.status === 'recusada'; }],
    ['todas', 'Todas', function () { return true; }]
  ];
  var vista = guarda.vista || 'abertas', areaSel = guarda.area || '', agrupar = guarda.agrupar || 'aderencia', sel = null, tela = guarda.tela || 'vagas';
  $('nVagas').textContent = V.filter(VISTAS[0][2]).length;
  $('vistas').innerHTML = VISTAS.map(function (x) { return '<button class="nav" type="button" data-vista="' + x[0] + '">' + x[1] + '<span class="n">' + V.filter(x[2]).length + '</span></button>'; }).join('');
  $('vistas').addEventListener('click', function (e) { var b = e.target.closest('[data-vista]'); if (!b) return; vista = b.getAttribute('data-vista'); guarda.vista = vista; salva(); irPara('vagas'); render(); });

  var areas = []; V.forEach(function (v) { if (v.area && areas.indexOf(v.area) < 0) areas.push(v.area); }); areas.sort();
  function pintaFiltros() {
    $('filtros').innerHTML = areas.map(function (a) { return '<button class="f" type="button" data-area="' + esc(a) + '" aria-pressed="' + (a === areaSel) + '">' + esc(a) + '</button>'; }).join('') +
      '<span class="f" style="margin-left:auto;border-style:solid">Agrupar por <select id="agrupar"><option value="aderencia">aderência</option><option value="status">status</option><option value="area">área</option><option value="nada">nada</option></select></span>';
    $('agrupar').value = agrupar;
    $('agrupar').onchange = function () { agrupar = this.value; guarda.agrupar = agrupar; salva(); render(); };
  }
  $('filtros').addEventListener('click', function (e) { var b = e.target.closest('[data-area]'); if (!b) return; var a = b.getAttribute('data-area'); areaSel = areaSel === a ? '' : a; guarda.area = areaSel; salva(); pintaFiltros(); render(); });
  pintaFiltros();
  $('busca').addEventListener('input', function () { if (tela === 'vagas') render(); else renderVoce(); });

  var visiveis = [];
  function render() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-vista]'), function (b) { b.setAttribute('aria-current', tela === 'vagas' && b.getAttribute('data-vista') === vista); });
    var nomeVista = VISTAS.filter(function (x) { return x[0] === vista; })[0] || VISTAS[0];
    $('titulo').textContent = 'Vagas'; $('sub').textContent = nomeVista[1] + (D.atualizado_em ? ' · atualizado ' + longa(D.atualizado_em) + ' ' + String(D.atualizado_em).slice(11, 16) : '');
    var q = $('busca').value.trim().toLowerCase();
    var vs = V.filter(nomeVista[2]).filter(function (v) {
      if (areaSel && v.area !== areaSel) return false;
      if (q) { var t = [v.id, v.empresa, v.cargo, v.motivo, v.falta, v.modalidade, v.local, v.regime, v.comentario_vaga, v.comentario_voce, v.comentario_encaixe].join(' ').toLowerCase(); if (t.indexOf(q) < 0) return false; }
      return true;
    });
    vs.sort(function (a, b) {
      var x = ADO.indexOf(a.aderencia), y = ADO.indexOf(b.aderencia); x = x < 0 ? 9 : x; y = y < 0 ? 9 : y;
      return x - y || String(b.publicada || '').localeCompare(String(a.publicada || ''));
    });
    var grupos = [];
    if (agrupar === 'nada') grupos = [['', vs]];
    else {
      var ordem = agrupar === 'aderencia' ? ADO : agrupar === 'status' ? Object.keys(ST) : areas;
      var nome = agrupar === 'aderencia' ? AD : agrupar === 'status' ? ST : null;
      ordem.concat(['']).forEach(function (k) {
        var g = vs.filter(function (v) { return (v[agrupar] || '') === k; });
        if (g.length) grupos.push([k ? (nome ? nome[k] : k) : 'Sem ' + (agrupar === 'area' ? 'área' : agrupar), g, k]);
      });
    }
    visiveis = [];
    if (!vs.length) { $('lista').innerHTML = '<div class="vazio">' + (V.length ? 'Nenhuma vaga nesta vista.' : 'Nenhuma vaga ainda. Peça ao Claude: pesquisa vagas pra mim.') + '</div>'; fechaDet(); return; }
    $('lista').innerHTML = grupos.map(function (g) {
      var cab = g[0] ? '<div class="grp">' + (agrupar === 'aderencia' ? '<span class="chip" style="border:0;padding:0"><i style="background:' + (ADC[g[2]] || 'var(--ink-4)') + '"></i></span>' : agrupar === 'status' ? '<span class="st">' + icone(g[2]) + '</span>' : '') + esc(g[0]) + '<span class="n">' + g[1].length + '</span></div>' : '';
      return cab + g[1].map(function (v) {
        visiveis.push(v.id);
        var sal = v.salario ? '<span class="chip sal" title="' + esc(SAL[v.salario_tipo] || '') + '">' + esc(v.salario.replace(/ (CLT|PJ)( pleno| júnior)?$/i, ' $1')) + '</span>' : '';
        return '<div class="linha' + (v.situacao === 'fechada' ? ' fechada' : '') + '" role="option" data-id="' + esc(v.id) + '" aria-selected="' + (v.id === sel) + '">' +
          '<span class="st" title="' + esc(ST[v.status] || v.status) + '">' + icone(v.status) + '</span>' +
          '<span class="id">' + esc(v.id) + '</span><span class="emp">' + esc(v.empresa) + '</span><span class="cargo">' + esc(v.cargo) + '</span>' +
          '<span class="tags">' + (agrupar !== 'aderencia' ? adChip(v.aderencia) : '') + (v.modalidade ? '<span class="chip">' + esc(v.modalidade) + '</span>' : '') + sal + '</span>' +
          '<span class="data">' + curta(v.publicada) + '</span></div>';
      }).join('');
    }).join('');
    if (sel && visiveis.indexOf(sel) < 0) fechaDet(); else if (sel) abreDet(sel, true);
  }
  $('lista').addEventListener('click', function (e) { var l = e.target.closest('.linha'); if (l) abreDet(l.getAttribute('data-id')); });

  function prop(rot, val) { return val ? '<dt>' + rot + '</dt><dd>' + val + '</dd>' : ''; }
  function coment(rot, txt) { return '<div class="coment"><span class="av">C</span><div><div class="quem"><b>Claude</b> sobre ' + rot + '</div>' + (txt ? '<p>' + esc(txt) + '</p>' : '<p class="semcoment">Sem comentário ainda. Peça ao Claude para atualizar as vagas.</p>') + '</div></div>'; }
  function abreDet(id, quieto) {
    var v = V.filter(function (x) { return x.id === id; })[0]; if (!v) return;
    sel = id;
    Array.prototype.forEach.call(document.querySelectorAll('.linha'), function (l) { l.setAttribute('aria-selected', l.getAttribute('data-id') === id); });
    var sit = v.situacao === 'fechada' ? 'Fechada' : v.situacao === 'aberta' ? 'Aberta, conferida ' + longa(v.conferida_em) : 'Não confirmada';
    $('det').innerHTML = '<div class="topo"><button class="icone" type="button" id="fechar" aria-label="Fechar"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m4 4 8 8m0-8-8 8"/></svg></button><span class="id">' + esc(v.id) + '</span>' +
      '<div class="acoes">' + (v.curriculo ? '<a class="btn" href="' + esc(href(v.curriculo)) + '">Currículo</a>' : '<button class="btn" type="button" data-copia="adapta meu currículo pra vaga ' + esc(v.id) + '">Pedir currículo</button>') +
      '<a class="btn prim" href="' + esc(href(v.url)) + '" target="_blank" rel="noopener">Abrir vaga</a></div></div>' +
      '<div class="conteudo"><h2>' + esc(v.cargo) + '</h2><div class="empresa">' + esc(v.empresa) + '</div>' +
      '<dl class="props">' + prop('Status', '<span class="st">' + icone(v.status) + '</span>' + esc(ST[v.status] || v.status) + ' <button class="btn" style="height:22px;padding:0 7px;margin-left:4px" type="button" data-copia="marca a vaga ' + esc(v.id) + ' como aplicada">mudar</button>') +
      prop('Aderência', adChip(v.aderencia)) + prop('Área', esc(v.area)) + prop('Modalidade', esc([v.modalidade, v.local && v.local !== v.modalidade ? v.local : ''].filter(Boolean).join(' · '))) +
      prop('Regime', esc(v.regime)) + prop('Salário', esc(v.salario || 'Não informado') + (v.salario_tipo ? ' <span style="color:var(--ink-4)">' + (SAL[v.salario_tipo] || '') + '</span>' : '')) +
      prop('Publicada', longa(v.publicada)) + prop('Prazo', longa(v.prazo)) + prop('Situação', esc(sit)) + '</dl>' +
      '<div class="bloco"><h3>Comentários</h3>' + coment('a vaga', v.comentario_vaga) + coment('você', v.comentario_voce) + coment('o encaixe', v.comentario_encaixe) + '</div>' +
      (v.motivo ? '<div class="bloco"><h3>O que bate</h3><p>' + esc(v.motivo) + '</p></div>' : '') +
      (v.falta ? '<div class="bloco"><h3>O que falta</h3><p>' + esc(v.falta) + '</p></div>' : '') +
      (v.salario_fonte ? '<div class="bloco"><h3>Fonte do salário</h3><p>' + esc(v.salario_fonte) + '</p></div>' : '') +
      (v.beneficios ? '<div class="bloco"><h3>Benefícios</h3><p>' + esc(v.beneficios) + '</p></div>' : '') +
      (v.notas ? '<div class="bloco"><h3>Notas</h3><p>' + esc(v.notas).replace(/\n/g, '<br>') + '</p></div>' : '') + '</div>';
    $('det').classList.add('on'); $('det').parentNode.classList.add('com-det');
    $('fechar').onclick = fechaDet;
    if (!quieto) { var l = document.querySelector('.linha[data-id="' + id + '"]'); if (l && l.scrollIntoViewIfNeeded) l.scrollIntoViewIfNeeded(); }
  }
  function fechaDet() { sel = null; $('det').classList.remove('on'); $('det').parentNode.classList.remove('com-det'); Array.prototype.forEach.call(document.querySelectorAll('.linha'), function (l) { l.setAttribute('aria-selected', 'false'); }); }

  document.addEventListener('keydown', function (e) {
    var digitando = /INPUT|SELECT|TEXTAREA/.test((document.activeElement || {}).tagName || '');
    if (e.key === '/' && !digitando) { e.preventDefault(); $('busca').focus(); return; }
    if (e.key === 'Escape') { if (digitando) document.activeElement.blur(); else fechaDet(); return; }
    if (digitando || tela !== 'vagas') return;
    if (e.key === 'j' || e.key === 'k' || e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault(); if (!visiveis.length) return;
      var i = visiveis.indexOf(sel), d = (e.key === 'j' || e.key === 'ArrowDown') ? 1 : -1;
      i = i < 0 ? 0 : Math.max(0, Math.min(visiveis.length - 1, i + d));
      abreDet(visiveis[i]);
      var l = document.querySelector('.linha[data-id="' + visiveis[i] + '"]'); if (l) l.scrollIntoView({ block: 'nearest' });
    }
    if (e.key === 'o' && sel) { var v = V.filter(function (x) { return x.id === sel; })[0]; if (v) window.open(href(v.url), '_blank', 'noopener'); }
  });

  // ---------------------------------------------------------- você
  var abaVoce = guarda.abaVoce || 'experiencias';
  function doc2html(d, aberto) {
    var meta = d.meta.length ? '<dl class="meta">' + d.meta.map(function (m) { return '<dt>' + esc(m[0]) + '</dt><dd>' + inl(m[1]) + '</dd>'; }).join('') + '</dl>' : '';
    var secs = d.secoes.map(function (s) {
      var t = s.titulo || '', low = t.toLowerCase();
      var cls = low.indexOf('nas minhas palavras') === 0 ? 'sec minhas' : low.indexOf('rascunho do claude') === 0 ? 'sec rasc' : 'sec';
      var nome = cls === 'sec minhas' ? 'Nas suas palavras' : t;
      return '<div class="' + cls + '">' + (nome ? '<h4>' + esc(nome) + '</h4>' : '') + s.blocos.map(bloco).join('') + '</div>';
    }).join('');
    var resumo = d.meta.slice(0, 2).map(function (m) { return m[1]; }).join(' · ');
    return '<details class="doc"' + (aberto ? ' open' : '') + '><summary><svg class="seta" width="10" height="10" viewBox="0 0 10 10"><path d="m3 2 4 3-4 3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg><span class="t">' + esc(d.titulo || d.caminho) + '</span><span class="m">' + esc(resumo) + '</span></summary><div class="in">' + meta + secs + '<p class="aviso" style="margin:12px 0 0">' + esc('candidato/' + d.caminho) + '</p></div></details>';
  }
  function bloco(b) {
    if (b.tipo === 'citacao') return '<p class="cit">' + inl(b.texto) + '</p>';
    if (b.tipo === 'lista') return '<ul>' + b.itens.map(function (x) { return '<li>' + inl(x) + '</li>'; }).join('') + '</ul>';
    if (b.tipo === 'numerada') return '<ol>' + b.itens.map(function (x) { return '<li>' + inl(x) + '</li>'; }).join('') + '</ol>';
    if (b.tipo === 'rotulo') return '<div class="rot">' + inl(b.texto) + '</div>';
    if (b.tipo === 'tabela') return tabela(b);
    return '<p>' + inl(b.texto) + '</p>';
  }
  function tabela(b) {
    var it = b.cab.map(function (c) { return c.toLowerCase(); }).indexOf('tipo');
    return '<div style="overflow-x:auto"><table><thead><tr>' + b.cab.map(function (c) { return '<th>' + esc(c) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      b.linhas.map(function (l) { return '<tr>' + l.map(function (c, i) { if (i === it) { var k = /^documentada/i.test(c) ? 'tipo doc-u' : /^inferida/i.test(c) ? 'tipo inf' : 'tipo'; return '<td><span class="' + k + '">' + esc(c) + '</span></td>'; } return '<td>' + inl(c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }
  function cursos(d) {
    var intro = d.secoes.filter(function (s) { return !s.titulo; }).map(function (s) { return s.blocos.map(bloco).join(''); }).join('');
    return '<div class="doc" style="padding:4px 16px 16px"><div style="display:flex;align-items:center;gap:12px;margin:12px 0 4px"><span class="t" style="font-weight:500;font-size:13.5px">' + esc(d.titulo) + '</span><label class="toggle" style="margin-left:auto"><input type="checkbox" id="verNotas"' + (guarda.notas ? ' checked' : '') + '> mostrar notas</label></div>' +
      '<div class="aviso">' + intro.replace(/<\/?p>/g, ' ') + '</div><div id="listaCursos" class="' + (guarda.notas ? '' : 'notas-off') + '">' +
      d.secoes.filter(function (s) { return s.titulo; }).map(function (s) {
        return '<div class="sec"><h4>' + esc(s.titulo) + '</h4>' + s.blocos.map(function (b) {
          return (b.itens || []).map(function (x) {
            var m = x.match(/^(.*)\(([^()]*)\)\s*$/), nome = m ? m[1] : x, q = m ? m[2].split(',').map(function (p) { return p.trim(); }) : [];
            var nota = q.length > 2 ? q.slice(2).join(',') : '';
            return '<div class="curso"><span>' + esc(nome.trim()) + '</span><span class="q">' + esc(q.slice(0, 2).join(' · ')) + (nota ? '<span class="nota"> · ' + esc(nota) + '</span>' : '') + '</span></div>';
          }).join('');
        }).join('') + '</div>';
      }).join('') + '</div></div>';
  }
  function renderVoce() {
    $('titulo').textContent = 'Você'; $('sub').textContent = CAND ? 'o que está em candidato/' : '';
    if (!CAND) { $('telaVoce').innerHTML = '<div class="wrap"><div class="vazio">Ainda não há pasta candidato/. Peça ao Claude: monta meu perfil.</div></div>'; return; }
    var q = $('busca').value.trim().toLowerCase();
    function filtra(lista) { return !q ? lista : lista.filter(function (d) { return JSON.stringify(d).toLowerCase().indexOf(q) >= 0; }); }
    var form = CAND.formacao || [], curs = form.filter(function (d) { return /cursos\.md$/.test(d.caminho); }), formR = form.filter(function (d) { return !/cursos\.md$/.test(d.caminho); });
    var nCursos = curs.reduce(function (n, d) { return n + d.secoes.reduce(function (m, s) { return m + (s.titulo ? s.blocos.reduce(function (k, b) { return k + (b.itens || []).length; }, 0) : 0); }, 0); }, 0);
    var hab = CAND.habilidades, nHab = hab ? hab.secoes.reduce(function (n, s) { return n + (s.titulo !== 'Sugeridas' ? s.blocos.reduce(function (k, b) { return k + (b.linhas || []).length; }, 0) : 0); }, 0) : 0;
    var ABAS = [
      ['experiencias', 'Experiências', CAND.experiencias.length],
      ['projetos', 'Projetos', CAND.projetos.length],
      ['formacao', 'Formação', nCursos ? nCursos + ' disciplinas' : formR.length],
      ['certificacoes', 'Certificações', CAND.certificacoes.length],
      ['habilidades', 'Habilidades', nHab],
      ['voz', 'Voz', CAND.voz ? '' : 0]
    ];
    var corpo = '';
    if (abaVoce === 'experiencias') corpo = filtra(CAND.experiencias).map(function (d, i) { return doc2html(d, i < 2 || !!q); }).join('');
    if (abaVoce === 'projetos') corpo = filtra(CAND.projetos).map(function (d) { return doc2html(d, true); }).join('');
    if (abaVoce === 'formacao') corpo = filtra(formR).map(function (d) { return doc2html(d, true); }).join('') + curs.map(cursos).join('');
    if (abaVoce === 'certificacoes') corpo = '<div class="doc" style="padding:4px 16px"><table><thead><tr><th>Certificação</th><th>Emissor</th><th>Data</th><th>Fonte</th></tr></thead><tbody>' +
      filtra(CAND.certificacoes).map(function (d) { var m = {}; d.meta.forEach(function (x) { m[x[0].toLowerCase()] = x[1]; }); return '<tr><td style="color:var(--ink)">' + esc(d.titulo) + '</td><td>' + esc(m.emissor) + '</td><td style="white-space:nowrap">' + esc(m.data) + '</td><td style="color:var(--ink-4)">' + esc(m.fonte) + '</td></tr>'; }).join('') + '</tbody></table></div>';
    if (abaVoce === 'habilidades') corpo = hab ? hab.secoes.map(function (s) { return s.titulo ? '<div class="doc" style="padding:4px 16px 12px"><div class="sec"><h4 style="font-size:13px;color:var(--ink)">' + esc(s.titulo) + '</h4>' + s.blocos.map(bloco).join('') + '</div></div>' : '<p class="aviso">' + s.blocos.map(function (b) { return inl(b.texto || ''); }).join(' ') + '</p>'; }).join('') : '';
    if (abaVoce === 'voz') corpo = CAND.voz ? '<div class="doc"><div class="in" style="border:0">' + CAND.voz.secoes.map(function (s) { var low = (s.titulo || '').toLowerCase(); return '<div class="sec' + (low === 'amostras' ? ' minhas' : '') + '">' + (s.titulo ? '<h4>' + esc(s.titulo) + '</h4>' : '') + s.blocos.map(bloco).join('') + '</div>'; }).join('') + '</div></div>' : '<div class="vazio">Sem voz.md ainda. Peça ao Claude: me entrevista sobre o meu trabalho.</div>';
    var contato = [CONT['cidade'], CONT['e-mail'] || CONT['email'], CONT['linkedin'], CONT['github']].filter(Boolean).map(esc).join(' · ');
    $('telaVoce').innerHTML = '<div class="wrap"><div class="cab"><h2>' + esc(CONT.nome || 'Você') + '</h2>' + (CONT.quem ? '<p>' + esc(CONT.quem) + '</p>' : '') + (contato ? '<div class="contato">' + contato + '</div>' : '') + '</div>' +
      '<div class="tabs" role="tablist">' + ABAS.map(function (a) { return '<button class="tab" role="tab" type="button" data-aba="' + a[0] + '" aria-selected="' + (a[0] === abaVoce) + '">' + a[1] + (a[2] !== '' ? '<span class="n">' + a[2] + '</span>' : '') + '</button>'; }).join('') + '</div>' +
      (corpo || '<div class="vazio">Nada aqui ainda.</div>') + '</div>';
    var vn = $('verNotas'); if (vn) vn.onchange = function () { guarda.notas = vn.checked; salva(); $('listaCursos').className = vn.checked ? '' : 'notas-off'; };
  }
  $('telaVoce').addEventListener('click', function (e) { var b = e.target.closest('[data-aba]'); if (!b) return; abaVoce = b.getAttribute('data-aba'); guarda.abaVoce = abaVoce; salva(); renderVoce(); });

  // ---------------------------------------------------------- telas
  function irPara(t) {
    tela = t; guarda.tela = t; salva();
    $('telaVagas').hidden = t !== 'vagas'; $('telaVoce').hidden = t !== 'voce';
    Array.prototype.forEach.call(document.querySelectorAll('[data-tela]'), function (b) { b.setAttribute('aria-current', b.getAttribute('data-tela') === t); });
    if (t === 'vagas') render(); else { renderVoce(); Array.prototype.forEach.call(document.querySelectorAll('[data-vista]'), function (b) { b.setAttribute('aria-current', 'false'); }); }
  }
  document.querySelectorAll('[data-tela]').forEach(function (b) { b.onclick = function () { irPara(b.getAttribute('data-tela')); }; });
  if (CONT.nome) $('wsnome').textContent = CONT.nome.split(' ')[0];
  // link direto: #vaga=<id>, #voce ou #voce/<aba>
  var h = decodeURIComponent(location.hash.slice(1));
  if (/^vaga=/.test(h)) { vista = 'todas'; irPara('vagas'); abreDet(h.slice(5)); }
  else if (/^voce/.test(h)) { if (h.split('/')[1]) abaVoce = h.split('/')[1]; irPara('voce'); }
  else irPara(tela === 'voce' ? 'voce' : 'vagas');
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
    pacote = {
        "atualizado_em": dados.get("atualizado_em"),
        "vagas": vagas,
        "candidato": ler_candidato(pasta),
        "contato": ler_contato(pasta),
    }
    bruto = json.dumps(pacote, ensure_ascii=False).replace("</", "<\\/")
    destino = pasta / "painel.html"
    destino.write_text(MODELO.replace("__DADOS__", bruto), encoding="utf-8")
    return destino
