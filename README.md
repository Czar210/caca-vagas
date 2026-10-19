# caca-vagas

Plugin do Claude Code para procurar emprego. Você conta o que procura uma vez; depois
pede "atualiza as vagas" e o Claude busca vagas abertas, confere se as antigas
fecharam, avalia a aderência ao seu perfil e refaz um painel que abre no navegador.
Quando uma vaga valer a pena, ele adapta o seu currículo para ela.

Seus dados ficam numa pasta sua, no seu computador. Nada vai para este repositório.

## Instalar

Precisa do [Claude Code](https://code.claude.com/docs) e de Python 3.10 ou mais novo.
Nenhuma biblioteca extra.

Dentro do Claude Code:

```
/plugin marketplace add Czar210/caca-vagas
/plugin install caca-vagas@caca-vagas
```

Ou no terminal:

```bash
claude plugin marketplace add Czar210/caca-vagas
claude plugin install caca-vagas@caca-vagas
```

## Usar

Abra o Claude Code em qualquer pasta e peça:

| Você diz | O que acontece |
|---|---|
| "pesquisa vagas pra mim" | Na primeira vez cria a sua pasta e te entrevista para montar o perfil. Depois busca, avalia e gera o painel. |
| "atualiza as vagas" | Confere as que já existem, busca novas e refaz o painel. |
| "marca a vaga a1b2c3 como aplicada" | Muda o status. O id aparece em cada card do painel. |
| "monta meu perfil a partir do meu currículo" | Lê o seu PDF e organiza projetos, experiências e habilidades. |
| "lê meus repositórios do GitHub" | Propõe quais repos viram projetos no currículo. |
| "adapta meu currículo pra vaga a1b2c3" | Compara a vaga com você, pergunta sobre lacunas, escreve o currículo e gera o PDF. |
| "exporta pra planilha" | Gera um CSV que abre no Excel. |

As skills também podem ser chamadas direto: `/caca-vagas:pesquisar-vagas`,
`/caca-vagas:gerenciar-vagas`, `/caca-vagas:montar-perfil`, `/caca-vagas:adaptar-curriculo`.

## O painel

`painel.html` fica na sua pasta e abre com dois cliques, sem servidor. Ele mostra cada
vaga com aderência, salário, benefícios, o que bate e o que falta, e tem filtro por área,
aderência e status. Os botões de cada card copiam o pedido pronto para colar no Claude.
Quem muda os dados é o Claude; o painel é refeito a cada mudança.

## Onde ficam os seus dados

Na pasta que você escolher na primeira vez (padrão `~/caca-vagas`). O caminho fica
anotado em `~/.caca-vagas.json`.

```
sua-pasta/
  perfil.md        o que você procura e o seu contato
  vagas.json       todas as vagas e o status de cada uma
  painel.html      o painel
  candidato/       matéria prima do currículo (projetos, experiências, formação, certificações)
  curriculos/      currículos gerados, um por vaga
```

## Limites que vale saber

- Quase nenhuma vaga no Brasil informa salário. Quando o Claude estima, o painel marca
  como estimativa e mostra a fonte. Ele não inventa número.
- LinkedIn e Glassdoor exigem login e bloqueiam leitura automática, então não entram na busca.
  As fontes diretas são Gupy, Lever e Greenhouse; o resto vem de busca na web.
- Alguns agregadores bloqueiam robôs. Nesses casos o Claude tenta ler a página por outro
  caminho, mas pode não conseguir confirmar se a vaga segue aberta; ela fica como "não confirmada".
- O plugin não se candidata, não faz login e não preenche formulário por você.

## O script

As skills usam `scripts/caca.py`, que também roda sozinho:

```bash
python scripts/caca.py -h
```

## Créditos

A parte de currículo é adaptada do
[adapt-resume-harness](https://github.com/devdebdeb/adapt-resume-harness), de devdebdeb.
Detalhes em [CREDITOS.md](CREDITOS.md).

## Licença

MIT, ver [LICENSE](LICENSE).
