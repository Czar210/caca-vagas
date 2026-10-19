---
name: montar-perfil
description: Monta e mantém o contexto do candidato (habilidades, projetos, experiências, formação, certificações) que o caca-vagas usa para avaliar vagas e adaptar currículo. Use quando a pessoa disser "monta meu perfil a partir do meu currículo", "adiciona este projeto", "lê meus repositórios do GitHub", "entrei na empresa X", "tirei uma certificação", "reconstrói meu contexto" ou quiser conferir as habilidades sugeridas.
argument-hint: "[o que adicionar: caminho de README, PDF, repo do GitHub]"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py onde), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py onde), Bash(gh repo list *), Bash(gh repo view *), Bash(gh api *), Read, Write, Edit, Glob
---

# Montar o perfil do candidato

Método adaptado do [adapt-resume-harness](https://github.com/devdebdeb/adapt-resume-harness),
de devdebdeb: fontes brutas viram contexto estruturado, e as habilidades entram
com nível de evidência explícito.

Rode `python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py onde` para achar a pasta. Tudo
aqui mora em `<pasta>/candidato/` (veja o `LEIA-ME.md` de lá). Se não houver pasta,
use primeiro a skill pesquisar-vagas, que cria.

## Fontes (a pessoa escreve ou você escreve com ela)

- `projetos/<nome>/README.md`, mais outros `.md` da mesma pasta.
- `experiencias/<empresa>/README.md` e `experiencias/<empresa>/<projeto>/README.md`.
- `formacao/<instituicao>/README.md` e `cursos.md`.
- `certificacoes/pdfs/*.pdf`: extraia cada um para `certificacoes/<nome>.md`
  (emissor, data, o que cobre) e não mexa no PDF.

Pastas que começam com `_` são modelos: ignore.

Caminhos rápidos:

- **A partir do currículo atual**: leia o PDF ou DOCX que a pessoa passar e
  crie uma pasta de fonte por experiência, projeto e formação, com o que está no
  documento. Marque `[falta número]` onde não houver métrica e pergunte depois.
- **A partir do GitHub**: com `gh repo list <usuario> --limit 50` e o README de cada
  repo (`gh api repos/<dono>/<repo>/readme --jq .content` em base64), proponha quais
  viram projeto. Pergunte antes de criar, e não traga repo privado de empregador
  sem a pessoa confirmar que pode citar.

## Contexto gerado (você escreve, a pessoa não edita)

Leia todas as fontes de uma vez. Quando um projeto tiver vários `.md`, comece pelo
README (é dele o título), leia os outros em ordem alfabética e trate tudo como uma
fonte só. Se dois arquivos discordarem, fique com o mais específico.

`contexto/projetos.md` e `contexto/experiencias.md`, uma entrada por item:

    ## <Título>  (experiência: ## <Empresa>: <Projeto>)
    Fontes: <arquivos lidos>
    Período / Cargo / Setor: (experiências)
    Stack: ...
    Problema: uma frase.
    O que foi feito: uma frase.
    Resultados:
    - bullet XYZ (veja abaixo)
    Palavras-chave: termos que um filtro de ATS procuraria.

`contexto/habilidades.md`: tabela por categoria (o modelo já tem as categorias),
colunas Habilidade, Nível, Fonte, Tipo.

### Como uma habilidade entra

- `documentada`: aparece escrita em alguma fonte. Entra direto, com o caminho na Fonte.
- `inferida` nível 1: substituta direta da mesma família (tem XGBoost, então LightGBM).
  Entra direto.
- `inferida` nível 2: prática padrão daquela stack (tem XGBoost, então ajuste de
  hiperparâmetros, SHAP). Entra direto.
- Nível 3 ou mais: direção vizinha que exige estudo próprio (tem scikit-learn, então
  redes neurais). Não entra. Vai para uma seção `## Sugeridas` no fim do arquivo,
  com o motivo, e você pergunta à pessoa. Só sobe para a tabela com um sim explícito.
- Comportamentais: infira do texto (liderou time, apresentava para diretoria) e marque `inferida`.

Nível: `Avançado` quando é ferramenta principal, com decisão de arquitetura ou uso
em vários projetos; `Intermediário` quando teve papel relevante com resultado
registrado; `Iniciante` quando só aparece de passagem ou foi inferida no nível 2.
Se uma habilidade da formação também aparece num projeto ou emprego, suba o nível e
liste as duas fontes: a prática valida o acadêmico.

### Bullet XYZ

Todo resultado segue "fiz X, medido por Y, fazendo Z": X é o resultado, Y o número
(%, tempo, R$, volume, usuários, acurácia), Z o como. Uma linha, no máximo duas,
começando pelo resultado. Sem número na fonte, use `~` para aproximação que a fonte
sustenta ou `[falta número]`. Nunca escreva "trabalhei com Python" ou "responsável por".

## Nunca

1. Marcar como `documentada` algo que não está escrito em nenhuma fonte.
2. Subir habilidade de nível 3 sem a pessoa confirmar.
3. Apagar habilidade da tabela sem a pessoa pedir.
4. Editar os PDFs de `certificacoes/pdfs/`.

No fim, diga em poucas linhas: o que entrou, quantas habilidades documentadas e
inferidas, quais sugeridas esperam resposta e quais resultados estão sem número.
