---
name: montar-perfil
description: Monta e mantém o contexto do candidato (experiências, projetos, formação, certificações, habilidades) e a voz da pessoa, que o caca-vagas usa para avaliar vagas e adaptar currículo. Use quando a pessoa disser "monta meu perfil", "me entrevista sobre meu trabalho", "adiciona este projeto", "lê meus repositórios", "entrei na empresa X", "tirei uma certificação", "aqui meu histórico", "reconstrói meu contexto", ou corrigir o jeito como um texto foi escrito por ela.
argument-hint: "[o que adicionar: currículo, histórico, README, PDF, repo]"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py onde), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py onde), Bash(gh repo list *), Bash(gh repo view *), Bash(gh api *), Read, Write, Edit, Glob, AskUserQuestion
---

# Montar o perfil do candidato

Estrutura e níveis de habilidade adaptados do
[adapt-resume-harness](https://github.com/devdebdeb/adapt-resume-harness), de devdebdeb.

A regra que manda em tudo aqui: **a voz é da pessoa.** Currículo que sai de "cola a
vaga e o currículo antigo num LLM" é o que este plugin existe para evitar. Você coleta
as palavras dela e organiza; não escreve por ela.

Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py onde` para achar a pasta. Tudo mora
em `<pasta>/candidato/` (veja o `LEIA-ME.md`). Pastas que começam com `_` são modelos.

## 1. Fontes: o que a pessoa já escreveu

- `experiencias/<empresa>/README.md` e `experiencias/<empresa>/<projeto>/README.md`
- `projetos/<nome>/README.md` (mais outros .md da pasta)
- `formacao/<instituicao>/README.md` e `cursos.md`
- `certificacoes/<nome>.md` (uma por certificado; o PDF original fica onde está ou em `certificacoes/pdfs/`)

Cada README de experiência ou projeto tem uma seção `## Nas minhas palavras` com
citações literais (`> ...`) da pessoa. Só entra ali texto que ela escreveu ou falou e
aprovou: bullets de um currículo que ela já usou, resposta dela na entrevista, post,
mensagem de commit. Texto seu, por melhor que seja, vai numa seção separada
`## Rascunho do Claude (data), falta você reescrever`, com aviso. Nunca misture.

Caminhos rápidos:

- **Currículo atual (PDF/DOCX)**: cada bullet vira citação em "Nas minhas palavras" da
  experiência certa, sem mexer em uma vírgula.
- **Histórico ou boletim**: disciplinas em `formacao/<inst>/cursos.md` agrupadas por
  área, com período e carga horária. Nota pode ficar registrada para consulta, mas nunca
  vai para currículo.
- **Certificados (PDF)**: leia cada um e grave emissor, data e de onde veio. Se o
  certificado contradiz o currículo (data, carga horária), registre os dois e avise.
- **GitHub**: `gh repo list <usuario> --limit 50` e o README de cada repo. Proponha quais
  viram projeto e pergunte antes. Repo privado de empregador só no nível de detalhe que
  a pessoa já usa no currículo, salvo ela dizer outra coisa.

## 2. Entrevista: quando falta a fala da pessoa

Se uma experiência ou projeto não tem "Nas minhas palavras", entreviste. Uma pergunta
por vez, curta, e guarde a resposta literal (corrija só erro de digitação óbvio):

1. "Me conta em duas ou três frases o que você fez em X, como contaria para um amigo da área."
2. "Qual o número que mostra que funcionou? Se não tem, o que mudou depois?"
3. "Teve algo que deu errado ou que você mudou de ideia no meio?"
4. "Qual foi a sua parte, separando da do time?"

Áudio transcrito vale. Se a resposta vier longa, guarde inteira e marque com a pessoa
quais trechos viram bullet. Não resuma, não "melhore".

## 3. A voz: `candidato/voz.md`

- **Amostras**: copie para lá os trechos que a pessoa aprovou como representativos.
- **Como eu conto o que fiz**: descreva padrões que você observou nas amostras (primeira
  pessoa? conta o próprio erro? número seco?), citando a amostra. Nada de padrão inventado.
- **Nunca**: toda vez que a pessoa corrigir forma ("não gosto disso", "eu não falaria
  assim"), acrescente uma regra negativa e verificável na hora, com a data. Se ela já
  mantém uma lista dessas em outro lugar, copie e diga de onde veio.

## 4. Contexto gerado (`candidato/contexto/`)

Você escreve, a pessoa não edita. Leia todas as fontes de uma vez.

- `experiencias.md` e `projetos.md`: índice, uma entrada por item, com período, fontes,
  stack, números (só os que estão escritos) e palavras chave. Não reescreva a fala dela
  aqui; aponte para a fonte.
- `habilidades.md`: tabela por categoria com Habilidade, Nível, Fonte, Tipo.

Como uma habilidade entra:

- `documentada`: aparece escrita numa fonte. Entra direto, com o caminho na Fonte.
- `inferida` nível 1: substituta direta da mesma família. Entra direto.
- `inferida` nível 2: prática padrão daquela stack. Entra direto.
- Nível 3 ou mais: direção vizinha que exige estudo próprio. Vai para `## Sugeridas` com
  o motivo e só sobe com um sim explícito.

Nível: `Avançado` quando é ferramenta principal ou com decisão de arquitetura;
`Intermediário` com papel relevante e resultado registrado; `Iniciante` quando aparece
de passagem, foi inferida no nível 2 ou a própria pessoa diz que é fraca nela.

## Nunca

1. Pôr texto seu em "Nas minhas palavras".
2. Marcar como `documentada` algo que não está escrito em fonte.
3. Subir habilidade de nível 3 sem confirmação, ou apagar uma sem pedido.
4. Corrigir estilo da pessoa. Ortografia só com aprovação item a item.

No fim, diga em poucas linhas: o que entrou, quais itens ainda não têm fala da pessoa
(e ofereça a entrevista), quais habilidades sugeridas esperam resposta, e qualquer
contradição entre fontes.
