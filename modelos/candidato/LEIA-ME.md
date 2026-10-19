# Pasta do candidato

Aqui fica a matéria-prima do seu currículo. O Claude lê estas pastas, monta os
arquivos de `contexto/` e usa tudo isso pra adaptar o currículo a cada vaga.
Estrutura e método adaptados do [adapt-resume-harness](https://github.com/devdebdeb/adapt-resume-harness), de devdebdeb.

- `projetos/<nome>/README.md`: um projeto pessoal ou acadêmico. Pode ter outros .md na mesma pasta.
- `experiencias/<empresa>/README.md`: a empresa (setor, tamanho, seu cargo, período).
- `experiencias/<empresa>/<projeto>/README.md`: o que você fez lá, com números.
- `formacao/<instituicao>/README.md` e `cursos.md`: curso, período, TCC, iniciação científica, disciplinas.
- `certificacoes/pdfs/`: PDFs dos certificados. O Claude extrai cada um para um .md ao lado.
- `contexto/`: gerado pelo Claude. Não edite à mão, peça "reconstrói meu contexto".
- `voz.md`: como você escreve. Amostras suas, o que nunca pode aparecer, e como você conta o próprio trabalho. É o que impede o currículo de sair com cara de texto gerado.

Não precisa preencher tudo de uma vez. O jeito mais rápido de começar é pedir
"monta meu perfil a partir do meu currículo atual" e passar o caminho do PDF;
depois, "me entrevista sobre o meu trabalho", para o Claude guardar como você conta
cada experiência, nas suas palavras.

Os modelos em `_exemplo` mostram o formato. Copie, renomeie e preencha.
