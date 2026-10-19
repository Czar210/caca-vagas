"""caca-vagas: guarda, confere e mostra as vagas de uma pessoa.

So biblioteca padrao do Python 3.10+. Os dados ficam numa pasta da pessoa (fora do
plugin), apontada por ~/.caca-vagas.json. Rode `python caca.py -h` para ver os comandos.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "modelos"
PONTEIRO = Path.home() / ".caca-vagas.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"

STATUS = ["nova", "interesse", "aplicada", "entrevista", "proposta", "recusada", "descartada"]
SITUACAO = ["aberta", "fechada", "incerta"]
ADERENCIA = ["alta", "media_alta", "media", "media_baixa", "baixa"]
SALARIO_TIPO = ["informado", "estimativa", "nao_informado"]
CAMPOS = [
    "url", "empresa", "cargo", "area", "nivel", "modalidade", "local", "regime",
    "salario", "salario_tipo", "salario_fonte", "beneficios", "aderencia", "motivo",
    "falta", "publicada", "prazo", "fonte", "situacao", "conferida_em", "status",
    "notas", "curriculo", "comentario_vaga", "comentario_voce", "comentario_encaixe",
]

GUPY_TIPO = {
    "vacancy_type_effective": "CLT",
    "vacancy_legal_entity": "PJ",
    "vacancy_type_internship": "Estágio",
    "vacancy_type_temporary": "Temporário",
    "vacancy_type_apprentice": "Aprendiz",
    "vacancy_type_trainee": "Trainee",
    "vacancy_type_autonomous": "Autônomo",
    "vacancy_type_associate": "Associado",
    "vacancy_type_talent_pool": "Banco de talentos",
    "vacancy_type_freelancer": "Freelancer",
    "vacancy_type_lecturer": "Docente",
    "vacancy_type_volunteer": "Voluntário",
}
GUPY_LOCAL = {"remote": "Remoto", "hybrid": "Híbrido", "on-site": "Presencial"}

FECHADA_RE = re.compile(
    r"no longer accepting applications|job not found|this job is no longer available|"
    r"position has been filled|this position is closed|job has expired|vaga encerrada|"
    r"vaga n[aã]o est[aá] mais dispon[ií]vel|n[aã]o est[aá] mais recebendo candidaturas|"
    r"processo seletivo encerrado|vaga expirada",
    re.I,
)


# ---------------------------------------------------------------- pasta e dados

def pasta_atual(arg: str | None = None) -> Path | None:
    if arg:
        return Path(arg).expanduser().resolve()
    if PONTEIRO.exists():
        try:
            p = json.loads(PONTEIRO.read_text(encoding="utf-8")).get("pasta")
            if p:
                return Path(p)
        except Exception:
            pass
    return None


def exigir_pasta(args) -> Path:
    p = pasta_atual(getattr(args, "pasta", None))
    if not p or not (p / "vagas.json").exists():
        sys.exit("Nenhuma pasta configurada. Rode: caca.py init [caminho]")
    return p


def ler(p: Path) -> dict:
    return json.loads((p / "vagas.json").read_text(encoding="utf-8"))


def gravar(p: Path, dados: dict) -> None:
    dados["atualizado_em"] = agora()
    tmp = p / "vagas.json.tmp"
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p / "vagas.json")


def agora() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def hoje() -> str:
    return dt.date.today().isoformat()


def normalizar_url(url: str) -> str:
    u = urllib.parse.urlsplit(url.strip())
    q = urllib.parse.parse_qsl(u.query)
    q = [(k, v) for k, v in q if not k.lower().startswith(("utm_", "ref", "source", "gh_src"))]
    caminho = u.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((u.scheme.lower() or "https", u.netloc.lower(), caminho, urllib.parse.urlencode(q), ""))


def vid(url: str) -> str:
    return hashlib.sha1(normalizar_url(url).encode()).hexdigest()[:6]


def achar(dados: dict, alvo: str) -> list[dict]:
    alvo_l = alvo.lower().strip()
    exato = [v for v in dados["vagas"] if v["id"] == alvo_l]
    if exato:
        return exato
    return [v for v in dados["vagas"]
            if alvo_l in f"{v.get('empresa','')} {v.get('cargo','')}".lower()]


# ---------------------------------------------------------------- rede

def baixar(url: str, timeout: int = 40) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            corpo = e.read().decode("utf-8", "replace")
        except Exception:
            corpo = ""
        return e.code, corpo
    except Exception as e:  # rede fora, DNS, timeout
        return 0, str(e)


def next_data(pagina: str) -> dict | None:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', pagina, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def texto_limpo(h: str) -> str:
    h = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", h or "", flags=re.S | re.I)
    h = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>|</div>", "\n", h, flags=re.I)
    h = re.sub(r"<li[^>]*>", "\n• ", h, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def data_iso(s) -> str:
    if not s:
        return ""
    if isinstance(s, (int, float)):
        return dt.datetime.fromtimestamp(s / 1000, dt.timezone.utc).date().isoformat()
    return str(s)[:10]


# ---------------------------------------------------------------- coletores

def coletar_gupy(termos: list[str], desde: str, paginas: int = 5) -> list[dict]:
    """Busca no portal da Gupy. A página traz 12 vagas por vez; `&page=N` pagina."""
    vistos: dict[str, dict] = {}
    for termo in termos:
        for n in range(1, paginas + 1):
            url = "https://portal.gupy.io/job-search/term=" + urllib.parse.quote(termo) + (f"&page={n}" if n > 1 else "")
            st, pagina = baixar(url)
            d = next_data(pagina) if st == 200 else None
            lista = (((d or {}).get("props") or {}).get("pageProps") or {}).get("initialJobList") or {}
            if not lista.get("data"):
                if n == 1:
                    print(f"[gupy] sem resultado legível para '{termo}' (HTTP {st})", file=sys.stderr)
                break
            for j in lista["data"]:
                if j.get("jobUrl"):
                    vistos[str(j.get("id"))] = j
            pag = lista.get("pagination") or {}
            if pag.get("offset", 0) + pag.get("limit", 12) >= pag.get("total", 0):
                break
    saida = []
    for j in vistos.values():
        pub = data_iso(j.get("publishedDate"))
        if desde and pub and pub < desde:
            continue
        local = ", ".join(x for x in [j.get("city"), j.get("state")] if x)
        saida.append({
            "url": j["jobUrl"].split("?")[0],
            "empresa": j.get("careerPageName", ""),
            "cargo": j.get("name", ""),
            "modalidade": GUPY_LOCAL.get(j.get("workplaceType"), j.get("workplaceType") or ""),
            "local": local,
            "regime": GUPY_TIPO.get(j.get("type"), j.get("type") or ""),
            "publicada": pub,
            "prazo": data_iso(j.get("applicationDeadline")),
            "fonte": "gupy",
            "resumo": texto_limpo(j.get("description", ""))[:300],
        })
    return sorted(saida, key=lambda v: v["publicada"], reverse=True)


def coletar_lever(empresas: list[str], desde: str, filtro: re.Pattern | None) -> list[dict]:
    saida = []
    for emp in empresas:
        st, corpo = baixar(f"https://api.lever.co/v0/postings/{emp}?mode=json")
        try:
            lista = json.loads(corpo)
            assert isinstance(lista, list)
        except Exception:
            print(f"[lever] '{emp}' não respondeu uma lista (HTTP {st})", file=sys.stderr)
            continue
        for j in lista:
            pub = data_iso(j.get("createdAt"))
            if desde and pub < desde:
                continue
            if filtro and not filtro.search(j.get("text", "")):
                continue
            c = j.get("categories") or {}
            sal = j.get("salaryRange") or {}
            saida.append({
                "url": j["hostedUrl"],
                "empresa": emp,
                "cargo": j.get("text", ""),
                "modalidade": j.get("workplaceType", "") or "",
                "local": c.get("location", "") or "",
                "regime": c.get("commitment", "") or "",
                "publicada": pub,
                "fonte": "lever",
                "salario": (f"{sal.get('currency','')} {sal.get('min','')} a {sal.get('max','')} {sal.get('interval','')}".strip() if sal else ""),
            })
    return saida


def coletar_greenhouse(empresas: list[str], desde: str, filtro: re.Pattern | None) -> list[dict]:
    saida = []
    for emp in empresas:
        st, corpo = baixar(f"https://boards-api.greenhouse.io/v1/boards/{emp}/jobs")
        try:
            lista = json.loads(corpo)["jobs"]
        except Exception:
            print(f"[greenhouse] '{emp}' não respondeu (HTTP {st})", file=sys.stderr)
            continue
        for j in lista:
            pub = data_iso(j.get("first_published") or j.get("updated_at"))
            if desde and pub < desde:
                continue
            if filtro and not filtro.search(j.get("title", "")):
                continue
            saida.append({
                "url": j["absolute_url"],
                "empresa": emp,
                "cargo": j.get("title", ""),
                "local": (j.get("location") or {}).get("name", ""),
                "publicada": pub,
                "fonte": "greenhouse",
            })
    return saida


# ---------------------------------------------------------------- detalhe e conferencia

def _lever_partes(url: str):
    m = re.match(r"https?://jobs\.(?:eu\.)?lever\.co/([^/]+)/([0-9a-f-]{36})", url)
    return m.groups() if m else None


def _greenhouse_partes(url: str):
    m = re.match(r"https?://(?:job-)?boards(?:\.eu)?\.greenhouse\.io/([^/]+)/jobs/(\d+)", url)
    return m.groups() if m else None


def detalhe(url: str) -> dict:
    """Devolve o que der pra ler da vaga: metadados e o texto inteiro."""
    lv = _lever_partes(url)
    if lv:
        st, corpo = baixar(f"https://api.lever.co/v0/postings/{lv[0]}/{lv[1]}")
        if st == 404:
            return {"situacao": "fechada", "http": st}
        try:
            j = json.loads(corpo)
        except Exception:
            return {"situacao": "incerta", "http": st}
        partes = [j.get("descriptionPlain", "")]
        for bloco in j.get("lists", []):
            partes.append(bloco.get("text", "") + "\n" + texto_limpo(bloco.get("content", "")))
        partes.append(j.get("additionalPlain", ""))
        c = j.get("categories") or {}
        return {"situacao": "aberta", "http": st, "cargo": j.get("text"), "local": c.get("location"),
                "regime": c.get("commitment"), "modalidade": j.get("workplaceType"),
                "publicada": data_iso(j.get("createdAt")), "salario": j.get("salaryRange"),
                "texto": "\n".join(p for p in partes if p)}
    gh = _greenhouse_partes(url)
    if gh:
        st, corpo = baixar(f"https://boards-api.greenhouse.io/v1/boards/{gh[0]}/jobs/{gh[1]}?pay_transparency=true")
        if st == 404:
            return {"situacao": "fechada", "http": st}
        try:
            j = json.loads(corpo)
        except Exception:
            return {"situacao": "incerta", "http": st}
        return {"situacao": "aberta", "http": st, "cargo": j.get("title"),
                "local": (j.get("location") or {}).get("name"),
                "publicada": data_iso(j.get("first_published")),
                "salario": j.get("pay_input_ranges") or None,
                "texto": texto_limpo(html.unescape(j.get("content", "")))}

    st, pagina = baixar(url)
    if st in (404, 410):
        return {"situacao": "fechada", "http": st}
    if st == 0 or st >= 400:
        return {"situacao": "incerta", "http": st, "erro": pagina[:200]}

    nd = next_data(pagina)
    job = (((nd or {}).get("props") or {}).get("pageProps") or {}).get("job") if nd else None
    if "gupy.io" in url and job:
        aberta = job.get("status") == "published" and (not job.get("expiresAt") or job["expiresAt"] >= hoje())
        texto = "\n\n".join(texto_limpo(job.get(k, "")) for k in
                            ["description", "responsibilities", "prerequisites", "relevantExperiences"] if job.get(k))
        local = ", ".join(x for x in [job.get("addressCity"), job.get("addressState")] if x)
        return {"situacao": "aberta" if aberta else "fechada", "http": st, "cargo": job.get("name"),
                "empresa": (job.get("careerPage") or {}).get("name"),
                "regime": GUPY_TIPO.get(job.get("jobType"), job.get("jobType")),
                "modalidade": GUPY_LOCAL.get(job.get("workplaceType"), job.get("workplaceType")),
                "local": local, "publicada": data_iso(job.get("publishedAt")),
                "prazo": job.get("expiresAt") or "", "texto": texto}

    info: dict = {"http": st}
    for bloco in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', pagina, re.S | re.I):
        try:
            ld = json.loads(bloco.strip())
        except Exception:
            continue
        for item in (ld if isinstance(ld, list) else ld.get("@graph", [ld])):
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                org = item.get("hiringOrganization") or {}
                info.update({
                    "cargo": item.get("title"),
                    "empresa": org.get("name") if isinstance(org, dict) else None,
                    "publicada": data_iso(item.get("datePosted")),
                    "prazo": data_iso(item.get("validThrough")),
                    "regime": item.get("employmentType"),
                    "salario": item.get("baseSalary"),
                    "texto": texto_limpo(item.get("description", "")),
                })
                if info["prazo"] and info["prazo"] < hoje():
                    info["situacao"] = "fechada"
    texto_pagina = texto_limpo(pagina)
    if "situacao" not in info:
        info["situacao"] = "fechada" if FECHADA_RE.search(texto_pagina[:20000]) else "incerta"
    info.setdefault("texto", texto_pagina)
    return info


# ---------------------------------------------------------------- comandos

def cmd_init(args):
    p = Path(args.caminho or (Path.home() / "caca-vagas")).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    if not (p / "perfil.md").exists():
        shutil.copy(MODELOS / "perfil.md", p / "perfil.md")
    if not (p / "vagas.json").exists():
        (p / "vagas.json").write_text(json.dumps({"atualizado_em": agora(), "vagas": []}, indent=2), encoding="utf-8")
    cand = p / "candidato"
    if not cand.exists():
        shutil.copytree(MODELOS / "candidato", cand)
    else:  # pasta de versão antiga: completa o que faltar, sem sobrescrever nada
        for origem in (MODELOS / "candidato").rglob("*"):
            destino = cand / origem.relative_to(MODELOS / "candidato")
            if origem.is_dir():
                destino.mkdir(parents=True, exist_ok=True)
            elif not destino.exists():
                shutil.copy(origem, destino)
    (p / "curriculos").mkdir(exist_ok=True)
    PONTEIRO.write_text(json.dumps({"pasta": str(p)}, ensure_ascii=False), encoding="utf-8")
    print(f"Pasta pronta: {p}")


def cmd_onde(args):
    p = pasta_atual(args.pasta)
    if not p or not (p / "vagas.json").exists():
        print("sem pasta")
        return
    d = ler(p)
    perfil = (p / "perfil.md").read_text(encoding="utf-8") if (p / "perfil.md").exists() else ""
    preenchido = "PREENCHER" not in perfil
    print(json.dumps({"pasta": str(p), "vagas": len(d["vagas"]), "atualizado_em": d.get("atualizado_em"),
                      "perfil_preenchido": preenchido, "painel": str(p / "painel.html")}, ensure_ascii=False))


def cmd_coletar(args):
    filtro = re.compile(args.filtro, re.I) if args.filtro else None
    desde = args.desde or (dt.date.today() - dt.timedelta(days=60)).isoformat()
    if args.fonte == "gupy":
        r = coletar_gupy(args.itens, desde, args.paginas)
    elif args.fonte == "lever":
        r = coletar_lever(args.itens, desde, filtro)
    else:
        r = coletar_greenhouse(args.itens, desde, filtro)
    if filtro and args.fonte == "gupy":
        r = [v for v in r if filtro.search(v["cargo"])]
    sair = json.dumps(r, ensure_ascii=False, indent=1)
    if args.saida:
        Path(args.saida).write_text(sair, encoding="utf-8")
        print(f"{len(r)} vagas em {args.saida}")
    else:
        print(sair)


def cmd_detalhe(args):
    info = detalhe(args.url)
    t = info.get("texto") or ""
    if len(t) > args.max:
        info["texto"] = t[: args.max] + f"\n[... cortado, {len(t)} caracteres no total]"
    print(json.dumps(info, ensure_ascii=False, indent=1, default=str))


def cmd_mesclar(args):
    p = exigir_pasta(args)
    d = ler(p)
    entrada = json.loads(Path(args.arquivo).read_text(encoding="utf-8"))
    if isinstance(entrada, dict):
        entrada = entrada.get("vagas", [entrada])
    por_id = {v["id"]: v for v in d["vagas"]}
    novas = atualizadas = 0
    erros = []
    for e in entrada:
        if not e.get("url"):
            erros.append(f"sem url: {e.get('empresa')} {e.get('cargo')}")
            continue
        for campo, validos in [("status", STATUS), ("situacao", SITUACAO), ("aderencia", ADERENCIA), ("salario_tipo", SALARIO_TIPO)]:
            if e.get(campo) and e[campo] not in validos:
                erros.append(f"{e.get('empresa')}: {campo}='{e[campo]}' fora de {validos}")
                e.pop(campo)
        i = vid(e["url"])
        limpo = {k: v for k, v in e.items() if k in CAMPOS and v not in (None, "")}
        if i in por_id:
            por_id[i].update(limpo)
            por_id[i]["atualizada_em"] = hoje()
            atualizadas += 1
        else:
            nova = {"id": i, "status": "nova", "situacao": "incerta", "adicionada_em": hoje(), **limpo}
            nova["url"] = e["url"]
            d["vagas"].append(nova)
            por_id[i] = nova
            novas += 1
    gravar(p, d)
    print(f"{novas} novas, {atualizadas} atualizadas, {len(d['vagas'])} no total")
    for x in erros:
        print("aviso:", x)


def cmd_listar(args):
    p = exigir_pasta(args)
    d = ler(p)
    ordem = {a: i for i, a in enumerate(ADERENCIA)}
    vs = d["vagas"] if args.todas else [v for v in d["vagas"] if v.get("situacao") != "fechada" and v.get("status") != "descartada"]
    vs = sorted(vs, key=lambda v: (ordem.get(v.get("aderencia"), 9), v.get("publicada", "")))
    for v in vs:
        print(" | ".join([v["id"], v.get("aderencia", "?"), v.get("status", ""), v.get("situacao", ""),
                          v.get("empresa", ""), v.get("cargo", ""), v.get("modalidade") or v.get("local", ""),
                          v.get("publicada", "")]))
    print(f"-- {len(vs)} de {len(d['vagas'])}")


def _uma(d, alvo):
    achadas = achar(d, alvo)
    if len(achadas) != 1:
        print(f"'{alvo}' bate com {len(achadas)} vagas:")
        for v in achadas:
            print(f"  {v['id']} | {v.get('empresa')} | {v.get('cargo')}")
        sys.exit(1)
    return achadas[0]


def cmd_marcar(args):
    if args.status not in STATUS:
        sys.exit(f"status inválido. Use um de: {', '.join(STATUS)}")
    p = exigir_pasta(args)
    d = ler(p)
    v = _uma(d, args.alvo)
    v["status"] = args.status
    v.setdefault("historico", []).append({"em": agora(), "status": args.status, **({"nota": args.nota} if args.nota else {})})
    if args.nota:
        v["notas"] = (v.get("notas", "") + f"\n{hoje()}: {args.nota}").strip()
    gravar(p, d)
    print(f"{v['id']} {v.get('empresa')} / {v.get('cargo')}: {args.status}")


def cmd_editar(args):
    p = exigir_pasta(args)
    d = ler(p)
    v = _uma(d, args.alvo)
    for par in args.pares:
        if "=" not in par:
            sys.exit(f"use campo=valor, recebi '{par}'")
        k, val = par.split("=", 1)
        if k not in CAMPOS or k == "url":
            sys.exit(f"campo '{k}' não editável. Campos: {', '.join(c for c in CAMPOS if c != 'url')}")
        v[k] = val
    gravar(p, d)
    print(f"{v['id']} atualizada")


def cmd_remover(args):
    p = exigir_pasta(args)
    d = ler(p)
    v = _uma(d, args.alvo)
    d["vagas"] = [x for x in d["vagas"] if x["id"] != v["id"]]
    gravar(p, d)
    print(f"{v['id']} removida ({v.get('empresa')} / {v.get('cargo')})")


def cmd_conferir(args):
    p = exigir_pasta(args)
    d = ler(p)
    alvo = [v for v in d["vagas"] if (not args.ids or v["id"] in args.ids)
            and (args.ids or v.get("situacao") != "fechada")]
    mudou = []
    for v in alvo:
        info = detalhe(v["url"])
        antes = v.get("situacao")
        v["situacao"] = info.get("situacao", "incerta")
        v["conferida_em"] = hoje()
        for k in ("prazo",):
            if info.get(k) and not v.get(k):
                v[k] = info[k]
        if antes != v["situacao"]:
            mudou.append(f"{v['id']} {v.get('empresa')}: {antes} -> {v['situacao']} (HTTP {info.get('http')})")
    gravar(p, d)
    cont = {s: sum(1 for v in alvo if v.get("situacao") == s) for s in SITUACAO}
    print(f"conferidas {len(alvo)}: {cont}")
    for m in mudou:
        print(" ", m)


def cmd_painel(args):
    p = exigir_pasta(args)
    sys.path.insert(0, str(Path(__file__).parent))
    from painel import gerar
    destino = gerar(ler(p), p)
    print(destino)


def cmd_exportar(args):
    import csv
    p = exigir_pasta(args)
    d = ler(p)
    destino = Path(args.saida) if args.saida else p / "vagas.csv"
    with open(destino, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id"] + CAMPOS)
        for v in d["vagas"]:
            w.writerow([v["id"]] + [v.get(c, "") for c in CAMPOS])
    print(destino)


# ---------------------------------------------------------------- curriculo em PDF

NAVEGADORES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def achar_navegador() -> str | None:
    for n in NAVEGADORES:
        if Path(n).exists():
            return n
    for nome in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "chrome", "msedge"):
        w = shutil.which(nome)
        if w:
            return w
    return None


def _inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_para_html(md: str) -> str:
    """Markdown simples de currículo: #, ##, ###, listas com -, parágrafos, **, *, links."""
    out, lista, para = [], False, []

    def fecha_para():
        if para:
            out.append("<p>" + "<br>".join(_inline(x) for x in para) + "</p>")
            para.clear()

    for linha in md.splitlines():
        s = linha.strip()
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        item = re.match(r"^[-*•]\s+(.*)", s)
        if not s:
            fecha_para()
            if lista:
                out.append("</ul>")
                lista = False
            continue
        if m or item:
            fecha_para()
        if m:
            if lista:
                out.append("</ul>")
                lista = False
            n = len(m.group(1))
            out.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
        elif item:
            if not lista:
                out.append("<ul>")
                lista = True
            out.append(f"<li>{_inline(item.group(1))}</li>")
        elif s in ("---", "***"):
            fecha_para()
            out.append("<hr>")
        else:
            if lista:
                out.append("</ul>")
                lista = False
            para.append(s)
    fecha_para()
    if lista:
        out.append("</ul>")
    return "\n".join(out)


CSS_CV = """
@page { size: A4; margin: 12mm 14mm; }
body { font-family: "Segoe UI", Calibri, Arial, sans-serif; font-size: 9.6pt; line-height: 1.32; color: #1f2328; margin: 0; }
h1 { font-size: 18pt; font-weight: 600; margin: 0; }
h1 + p { margin: 2pt 0 0; color: #3d4450; }
h2 { font-size: 9pt; font-weight: 600; letter-spacing: 1pt; text-transform: uppercase; color: #1f4e8c;
     border-bottom: 0.6pt solid #b9c3d0; padding-bottom: 1.5pt; margin: 9pt 0 3pt; }
h3 { font-size: 9.8pt; font-weight: 600; margin: 5pt 0 1pt; }
p { margin: 2pt 0; }
ul { margin: 1pt 0 3pt; padding-left: 13pt; }
li { margin: 0.6pt 0; }
a { color: #1f4e8c; text-decoration: none; }
hr { border: 0; border-top: 0.6pt solid #d0d7de; margin: 5pt 0; }
"""


def cmd_pdf(args):
    md = Path(args.arquivo).resolve()
    corpo = md_para_html(md.read_text(encoding="utf-8"))
    pagina = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS_CV}</style></head><body>{corpo}</body></html>"
    html_p = md.with_suffix(".html")
    html_p.write_text(pagina, encoding="utf-8")
    nav = achar_navegador()
    if not nav:
        print(f"Nenhum Chrome/Edge achado. Abra {html_p} no navegador e salve como PDF (Ctrl+P).")
        return
    pdf = md.with_suffix(".pdf")
    with tempfile.TemporaryDirectory() as perfil_tmp:
        subprocess.run([nav, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={perfil_tmp}",
                        f"--print-to-pdf={pdf}", html_p.as_uri()], capture_output=True, timeout=180)
    if pdf.exists():
        paginas = len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))
        print(f"{pdf} ({paginas} página{'s' if paginas != 1 else ''})")
    else:
        print(f"O navegador não gerou o PDF. O HTML está em {html_p}.")


# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(prog="caca.py", description="Guarda, confere e mostra vagas.")
    ap.add_argument("--pasta", help="usa esta pasta de dados em vez da configurada")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="cria a pasta de dados e aponta para ela")
    s.add_argument("caminho", nargs="?")
    s.set_defaults(f=cmd_init)

    s = sub.add_parser("onde", help="mostra a pasta configurada e o estado")
    s.set_defaults(f=cmd_onde)

    s = sub.add_parser("coletar", help="busca vagas numa fonte e devolve JSON")
    s.add_argument("fonte", choices=["gupy", "lever", "greenhouse"])
    s.add_argument("itens", nargs="+", help="gupy: termos de busca. lever/greenhouse: slugs das empresas")
    s.add_argument("--desde", help="AAAA-MM-DD (padrão: 60 dias atrás)")
    s.add_argument("--filtro", help="regex aplicada ao título")
    s.add_argument("--paginas", type=int, default=5, help="gupy: páginas de 12 vagas por termo (padrão 5)")
    s.add_argument("--saida", help="grava o JSON neste arquivo")
    s.set_defaults(f=cmd_coletar)

    s = sub.add_parser("detalhe", help="lê a página de uma vaga e diz se está aberta")
    s.add_argument("url")
    s.add_argument("--max", type=int, default=6000)
    s.set_defaults(f=cmd_detalhe)

    s = sub.add_parser("mesclar", help="junta um JSON de vagas ao vagas.json, sem duplicar")
    s.add_argument("arquivo")
    s.set_defaults(f=cmd_mesclar)

    s = sub.add_parser("listar", help="lista as vagas (sem fechadas e descartadas)")
    s.add_argument("--todas", action="store_true")
    s.set_defaults(f=cmd_listar)

    s = sub.add_parser("marcar", help="muda o status de uma vaga (id ou trecho do nome)")
    s.add_argument("alvo")
    s.add_argument("status", help=", ".join(STATUS))
    s.add_argument("--nota")
    s.set_defaults(f=cmd_marcar)

    s = sub.add_parser("editar", help="muda campos de uma vaga: campo=valor")
    s.add_argument("alvo")
    s.add_argument("pares", nargs="+")
    s.set_defaults(f=cmd_editar)

    s = sub.add_parser("remover", help="apaga uma vaga do vagas.json")
    s.add_argument("alvo")
    s.set_defaults(f=cmd_remover)

    s = sub.add_parser("conferir", help="confere se as vagas continuam abertas")
    s.add_argument("ids", nargs="*")
    s.set_defaults(f=cmd_conferir)

    s = sub.add_parser("painel", help="gera o painel.html")
    s.set_defaults(f=cmd_painel)

    s = sub.add_parser("exportar", help="exporta as vagas em CSV (abre no Excel)")
    s.add_argument("--saida")
    s.set_defaults(f=cmd_exportar)

    s = sub.add_parser("pdf", help="converte um currículo .md em PDF")
    s.add_argument("arquivo")
    s.set_defaults(f=cmd_pdf)

    args = ap.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
