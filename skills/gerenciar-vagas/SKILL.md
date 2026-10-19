---
name: gerenciar-vagas
description: Muda o status e os dados das vagas guardadas no caca-vagas e refaz o painel. Use quando a pessoa disser "marca a vaga X como aplicada", "fui chamado pra entrevista na Y", "descarta a Z", "anota que...", "tira as fechadas", "abre o painel", "exporta pra planilha" ou perguntar como está a lista de vagas.
argument-hint: "[pedido, ex.: marca a1b2c3 como aplicada]"
allowed-tools: Bash(python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py *), Read
---

# Gerenciar vagas

`CACA` = `python ${CLAUDE_PLUGIN_ROOT}/scripts/caca.py` (ou `python3`). Nunca edite
`vagas.json` à mão. Se `CACA onde` responder `sem pasta`, use a skill pesquisar-vagas.

A pessoa se refere à vaga pelo id de seis letras que aparece no painel, ou pelo nome
da empresa ou do cargo. O script aceita os dois. Se ele disser que o trecho bate com
mais de uma vaga, mostre as opções e pergunte qual.

| Pedido | Comando |
|---|---|
| mudar status | `CACA marcar <id ou trecho> <status> [--nota "texto"]` |
| anotar | `CACA marcar <id> <status atual> --nota "texto"` |
| mudar um campo | `CACA editar <id> campo=valor [campo=valor ...]` |
| apagar de vez | `CACA remover <id>` (confirme antes com a pessoa) |
| ver a lista | `CACA listar` (com `--todas` inclui fechadas e descartadas) |
| conferir se fecharam | `CACA conferir [ids]` |
| planilha | `CACA exportar` (CSV com `;`, abre no Excel) |

Status válidos: `nova`, `interesse`, `aplicada`, `entrevista`, `proposta`,
`recusada`, `descartada`. "Tira as fechadas" quer dizer esconder, e o painel já
esconde fechadas e descartadas por padrão; só remova se a pessoa pedir pra apagar.

Depois de qualquer mudança, rode `CACA painel` e diga em uma linha o que mudou.
Para abrir o painel, mostre o caminho de `painel.html` que `CACA onde` devolve.
