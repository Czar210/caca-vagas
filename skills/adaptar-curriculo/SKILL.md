---
name: adaptar-curriculo
description: Gera um currículo sob medida para uma vaga, pensado para passar em filtro de ATS, a partir do contexto do candidato, e exporta em PDF. Use quando a pessoa disser "adapta meu currículo pra vaga <id>", "faz um currículo pra essa vaga" (com link ou descrição colada), ou pedir carta de apresentação, resposta de "por que você quer essa vaga" ou texto de LinkedIn para uma vaga.
argument-hint: "<id da vaga, link ou descrição colada>"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), WebFetch, Read, Write, Edit, Glob
---

# Adaptar currículo para uma vaga

Método adaptado do [adapt-resume-harness](https://github.com/devdebdeb/adapt-resume-harness),
de devdebdeb. `CACA` = `python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py` (ou `python3`).

## 0. Pegar a vaga e o contexto

- Se veio um id: `CACA listar --todas` para achar a vaga e `CACA detalhe <url>` para o
  texto inteiro (se voltar 403, WebFetch). Se veio link, `CACA detalhe <link>`. Se veio
  texto colado, use o texto.
- Leia `<pasta>/perfil.md` (contato e quem é a pessoa) e tudo de `<pasta>/candidato/contexto/`
  e `<pasta>/candidato/formacao/`. Se `contexto/habilidades.md` estiver vazio, pare e
  proponha a skill montar-perfil primeiro: currículo sem contexto vira invenção.

## 1. Ler a vaga

Monte, para você e para mostrar à pessoa em forma curta:

- requisitos técnicos marcados como obrigatório, desejável ou diferencial;
- comportamentais esperados;
- palavras-chave literais que um ATS vai procurar (como estão escritas na vaga);
- nível esperado, setor, tamanho da empresa e o problema que o cargo resolve.

## 2. Comparar com o candidato

Tabela: requisito, tem? (`documentada`, `inferida` ou lacuna), onde está no contexto.
Termine com uma nota de 0 a 10 e uma frase de justificativa. Para cada lacuna, diga se
é vizinha do que a pessoa já sabe (aprende rápido) ou distante.

Lacuna vizinha que aparece como obrigatória ou desejável: pergunte à pessoa se ela
tem, ou se tem contato suficiente pra citar. Passar no ATS importa, então na dúvida
pergunte em vez de omitir em silêncio. Nada entra sem um sim explícito.

Equivalente direto: se a vaga pede uma ferramenta e a pessoa tem a equivalente (pede
AWS, tem Azure), o nome pedido pode aparecer no texto do currículo como
"transferível para AWS" para o ATS achar a palavra. Isso não é afirmar a habilidade e
nunca vai para `habilidades.md`.

## 3. Escrever

Idioma: o da vaga (português do Brasil ou inglês dos EUA). Escolha o que mais serve a
esta vaga, não sempre o mesmo: três a cinco projetos, as experiências relevantes, três a
cinco disciplinas da formação que conversam com a vaga, TCC ou iniciação científica se
somarem. Grave em Markdown simples, que o PDF entende:

    # Nome Completo
    Título igual ao da vaga
    Cidade · telefone · e-mail · [LinkedIn](url) · [GitHub](url) · idiomas

    ## Resumo
    Três ou quatro linhas com o título da vaga e as palavras-chave dela.

    ## Competências
    Três a cinco grupos nomeados como a vaga nomeia, cada um uma lista separada por vírgula.

    ## Experiência
    ### Cargo · Empresa · período
    - bullet XYZ, o mais ligado à vaga primeiro

    ## Projetos
    ### Projeto · link
    - bullet XYZ
    - Stack: ...

    ## Formação
    ### Curso · Instituição · período
    Disciplinas: ...

    ## Certificações
    - Nome · emissor · ano

Bullets XYZ: resultado, número, como; uma linha, no máximo duas, começando pelo
resultado. Se um cargo tem quatro fatos ou mais, fique com os dois números mais fortes.
Bullet sem número: busque na fonte ou marque `[falta número]` e avise.

Nunca coloque CR, nota ou média. Nada de foto, endereço completo ou documento. Datas
no mesmo formato do começo ao fim. Verbo no passado para cargos que acabaram. Tamanho:
até 2 páginas em inglês, até 3 em português (uma é melhor para júnior).

### Texto corrido sem cara de IA

Vale para resumo, carta e qualquer prosa (bullets seguem o XYZ). Cada afirmação de
encaixe aponta para um projeto, número ou habilidade do contexto. Varie o tamanho das
frases. Escreva como alguém contando trabalho real para outro profissional.
Não use: alavancar, desbloquear, robusto sem número, sinergia, holístico, de ponta,
"no cenário atual", "vale ressaltar", "nesse sentido", elogio genérico à empresa,
abertura de enchimento, fecho aspiracional, travessão, e a estrutura em três batidas
("Não é só X. É Y. É Z."). Em inglês, o mesmo: leverage, unlock, seamless,
cutting-edge, game-changer, world-class, synergy, "in today's landscape".

## 4. Conferir antes de salvar

- Toda palavra-chave obrigatória aparece literalmente.
- O título da vaga aparece no resumo.
- A formação pedida aparece como a vaga escreve.
- Nada de tabela ou colunas no corpo (quebra o ATS).
- O mais relevante vem primeiro em cada seção.

## 5. Salvar e ligar à vaga

Grave em `<pasta>/curriculos/<empresa_em_snake_case>/<nome-em-kebab>-<cargo-em-kebab>.md`.
Rode `CACA pdf <arquivo.md>` (gera o PDF com Chrome ou Edge e diz quantas páginas deu;
se passar do limite, corte e gere de novo). Se veio de uma vaga guardada, rode
`CACA editar <id> curriculo=curriculos/<empresa>/<arquivo>.pdf` e `CACA painel`: o
card da vaga ganha o botão do currículo.

Responda com a nota de aderência, as perguntas de lacuna que ficaram, o caminho do PDF
e a oferta de gerar a versão no outro idioma, uma carta ou o texto do LinkedIn.
