---
name: pesquisar-vagas
description: Pesquisa vagas de emprego abertas que batem com o perfil da pessoa, confere se as vagas já guardadas continuam abertas, avalia aderência, salário e benefícios, e atualiza o painel HTML. Use quando a pessoa pedir para procurar, pesquisar, buscar ou atualizar vagas, "acha vaga pra mim", "tem vaga nova?", ou na primeira vez que ela usa o caca-vagas.
argument-hint: "[foco opcional, ex.: só remoto, só IA]"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), WebSearch, WebFetch, Read, Write, Edit
---

# Pesquisar vagas

Todo o estado fica numa pasta da pessoa, fora do plugin. O script
`${CLAUDE_PLUGIN_ROOT}/scripts/caca.py` lê e grava essa pasta; você nunca edita
`vagas.json` à mão. Nos comandos abaixo, `CACA` quer dizer
`python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py` (use `python3` se `python` não existir).

## 1. Achar a pasta

Rode `CACA onde`.

- Se responder `sem pasta`: pergunte onde guardar (sugira `~/caca-vagas`) e rode
  `CACA init <caminho>`. Depois vá para o passo 2.
- Se `perfil_preenchido` for `false`: passo 2. Senão, passo 3.

## 2. Preencher o perfil (só na primeira vez)

Leia `<pasta>/perfil.md`. Ele tem campos `PREENCHER`. Entreviste a pessoa com
AskUserQuestion, poucas perguntas por vez, até ter: cargos, nível, onde (remoto,
cidade, exterior, relocação), regime, piso salarial, stack forte, o que evitar e as
áreas do painel. Contato e "quem eu sou" podem vir do currículo atual se ela passar o
caminho. Proponha os termos de busca da Gupy a partir dos cargos (dois a quatro
termos, em português e em inglês quando fizer sentido). Grave o perfil com Edit,
sem deixar nenhum `PREENCHER`.

## 3. Conferir as vagas que já existem

Rode `CACA conferir`. Ele marca como `fechada` o que sumiu ou expirou. Para cada
vaga que voltou `incerta` e tem status `interesse`, `aplicada` ou `entrevista`, abra o
link com WebFetch e decida: se a página diz que encerrou, `CACA editar <id> situacao=fechada`;
se mostra a vaga ativa, `situacao=aberta`.

## 4. Coletar candidatas

Leia o perfil inteiro antes. Rode, gravando em arquivos temporários dentro da pasta:

- `CACA coletar gupy "<termo 1>" "<termo 2>" --saida <pasta>/_gupy.json`
- Se o perfil lista slugs: `CACA coletar lever <slugs> --saida <pasta>/_lever.json`
  e `CACA coletar greenhouse <slugs> --saida <pasta>/_gh.json`. Use `--filtro` com uma
  regex dos cargos para cortar ruído (ex.: `"dados|data|machine learning|\bai\b|\bia\b"`).

Depois complete com WebSearch: sites de carreira de empresas que fazem sentido para
o perfil, e, se o perfil aceita exterior, agregadores de remoto (Himalayas, Remote OK,
We Work Remotely, Wellfound). LinkedIn e Glassdoor pedem login: não conte com eles.
Descarte vaga publicada há mais de 60 dias ou já encerrada.

Leia a lista dos coletores pelo título e pelo resumo e escolha as que valem
olhar de perto. Corte cedo o que o perfil diz para evitar (nível, cidade, regime).

## 5. Ler e avaliar cada vaga escolhida

Para cada uma, rode `CACA detalhe <url>`. Ele devolve o texto inteiro, se está aberta,
regime, modalidade e datas. Se voltar `incerta` com HTTP 403, use WebFetch na URL.
Com o texto em mãos, preencha:

- `aderencia`: `alta`, `media_alta`, `media`, `media_baixa` ou `baixa`, comparando o que
  a vaga pede com a stack forte, o nível e as notas do perfil. Se existir
  `<pasta>/candidato/contexto/habilidades.md`, use também.
- `motivo`: uma frase com o que bate. `falta`: o que a vaga exige e a pessoa não tem.
  Seja honesto: requisito obrigatório que falta pesa mais que diferencial.
- `salario`, `salario_tipo`, `salario_fonte`: se a vaga informa, copie e use
  `informado`. Se não, você pode estimar com fonte pública (pesquisa salarial,
  Levels.fyi, Glassdoor que abriu) e usar `estimativa` com a fonte. Sem fonte, use
  `nao_informado`. Nunca invente número.
- `beneficios`: o que a vaga ou a página de carreira lista. Vazio se não achou.
- `area`: uma das áreas do perfil. `nivel`, `modalidade`, `local`, `regime`, `publicada`
  (AAAA-MM-DD), `prazo`, `empresa`, `cargo`, `fonte`, `situacao`.

Descarte vaga abaixo do piso quando o salário for informado. Quando for estimativa
e estiver perto do piso, mantenha e diga isso em `falta`.

## 6. Gravar e mostrar

Escreva as avaliadas num JSON (lista de objetos com os campos acima e `url`) em
`<pasta>/_entrada.json` e rode `CACA mesclar <pasta>/_entrada.json`. A mesclagem não
duplica (a chave é a URL) e não mexe no status que a pessoa já deu. Apague os
arquivos `_*.json` e rode `CACA painel`.

Responda curto: quantas novas, quantas fecharam, as três ou quatro melhores em
uma linha cada (empresa, cargo, por que), e o caminho do `painel.html` para abrir.
Se nenhuma vaga informou salário, diga isso. Para adaptar o currículo a uma vaga,
a pessoa pede "adapta meu currículo pra vaga <id>" (skill adaptar-curriculo).

## Regras

- Não se candidate, não faça login e não preencha formulário em site de vaga.
- Número, data e status vêm de página aberta ou do script, nunca de memória.
- Vaga vista só no resultado de busca, sem abrir, fica com `situacao=incerta`.
