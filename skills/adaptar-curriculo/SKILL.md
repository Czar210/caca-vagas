---
name: adaptar-curriculo
description: Monta um currículo para uma vaga específica escolhendo, cortando e reordenando as frases que a própria pessoa escreveu, com rastro de cada mudança, e exporta em PDF. Use quando a pessoa disser "adapta meu currículo pra vaga <id>", "faz um currículo pra essa vaga" (com link ou descrição colada), ou pedir carta de apresentação ou resposta de entrevista para uma vaga.
argument-hint: "<id da vaga, link ou descrição colada>"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), WebFetch, Read, Write, Edit, Glob, AskUserQuestion
---

# Adaptar currículo para uma vaga

Leitura da vaga e checklist de ATS adaptados do
[adapt-resume-harness](https://github.com/devdebdeb/adapt-resume-harness), de devdebdeb.
`CACA` = `python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py` (ou `python3`).

**Você é editor, não autor.** O material são as frases da pessoa em
`candidato/**/README.md` (seções "Nas minhas palavras") e em `candidato/voz.md`. Seu
trabalho é escolher quais entram para esta vaga, em que ordem, e cortar o que não serve.
Um currículo que soa como "LLM personalizou o meu currículo" é falha deste skill.

## 0. Material

- Vaga: id → `CACA listar --todas` e `CACA detalhe <url>` (403 → WebFetch); link →
  `CACA detalhe <link>`; texto colado → o texto.
- Pessoa: `<pasta>/perfil.md` (contato), `candidato/voz.md` inteiro, e tudo de
  `candidato/experiencias/`, `projetos/`, `formacao/`, `certificacoes/`, `contexto/`.
- Se uma experiência relevante para a vaga não tem "Nas minhas palavras", pare e ofereça
  a entrevista da skill montar-perfil para ela. Não preencha com texto seu.

## 1. Ler a vaga

Mostre curto: requisitos obrigatórios, desejáveis e diferenciais; palavras chave literais
que um ATS vai procurar; nível real (o título e o requisito às vezes discordam: diga).

## 2. Comparar

Tabela: requisito, tem? (`documentada`, `inferida` ou lacuna), onde. Nota de 0 a 10 com
uma frase. Lacuna vizinha que a vaga marca como obrigatória ou desejável: pergunte se a
pessoa tem. Nada entra sem sim explícito.

Equivalente direto (pede AWS, tem Azure): o nome pedido pode aparecer só como
"transferível para AWS" numa linha de competências, nunca como habilidade afirmada.

## 3. Montar, com rastro

Para cada seção (resumo, experiência, projetos, formação, certificações), selecione as
frases da pessoa que mais servem à vaga e ordene pela relevância. Edições permitidas,
nesta ordem de preferência:

1. **Manter** a frase como está.
2. **Cortar** trecho (oração, lista longa) que não serve a esta vaga.
3. **Trocar um termo** pelo da vaga só quando é sinônimo exato do mesmo fato
   (ex.: "carga diária" → "pipeline batch diário" se a vaga usa esse termo). Nunca para
   inflar ("participei" não vira "liderei").
4. **Juntar** duas frases da pessoa numa, se couber sem acrescentar ideia.

Proibido: acrescentar adjetivo, resultado, número, escopo ou palavra que a pessoa não
usou; e qualquer coisa listada em "Nunca" no `voz.md`. O resumo do topo também sai das
frases dela (o perfil do currículo, a fala da entrevista); se não houver, monte com
frases dela e marque como rascunho.

Antes de salvar, mostre a tabela de rastro e peça aprovação:

| # | Seção | Frase original (fonte) | Nesta versão | Edição |
|---|---|---|---|---|
| 1 | Experiência | "..." (experiencias/x/README.md) | "..." | manteve / cortou "..." / trocou "a" por "b" |

Se a pessoa reescrever alguma linha, use a versão dela e ofereça guardar em "Nas minhas
palavras". Se ela corrigir forma, acrescente a regra em "Nunca" do `voz.md`.

Bullets: confira, não reescreva. Se um bullet relevante não tem número nem resultado,
pergunte "tem um número pra isso?" em vez de inventar.

## 4. Formato e conferência

Markdown simples, que o PDF entende:

    # Nome Completo
    Título igual ao da vaga
    Cidade · telefone · email · [LinkedIn](url) · [GitHub](url) · idiomas

    ## Resumo
    ## Competências
    ## Experiência
    ### Cargo · Empresa · período
    - frase da pessoa
    ## Projetos
    ## Formação
    ## Certificações

Confira: palavras chave obrigatórias aparecem literalmente (se faltar uma que a pessoa
tem, a frase dela que prova vai para cima; se ela não tem, a palavra não entra); título
da vaga no resumo; sem tabela ou coluna no corpo; sem nota, CR, foto, endereço
completo, documento; datas no mesmo formato; até 1 página para júnior, 2 em inglês,
3 em português.

## 5. Salvar e ligar à vaga

Grave em `<pasta>/curriculos/<empresa_snake>/<nome-kebab>-<cargo-kebab>.md`, junto com
`<mesmo-nome>.rastro.md` (a tabela aprovada). `CACA pdf <arquivo.md>` gera o PDF e diz
quantas páginas deu. Se veio de vaga guardada: `CACA editar <id> curriculo=<caminho do
pdf relativo à pasta>` e `CACA painel`.

Carta, "por que esta vaga" ou resposta de entrevista: mesmo princípio. Comece pedindo
duas ou três frases dela sobre por que quer a vaga; você organiza e corta.
