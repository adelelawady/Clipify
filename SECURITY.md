# Segurança e gerenciamento de credenciais (resumo rápido)

Este repositório não deve conter chaves de API ou credenciais em texto claro. Siga os passos abaixo para trabalhar de forma segura.

1) Não comitar arquivos de ambiente
- Mantenha suas chaves em `.env` local (já ignorado pelo `.gitignore`).

2) Use um template para compartilhar configurações
- Preencha `.env.example` com nomes de chaves (sem valores reais). Ao clonar, copie para `.env`.

3) Revogue quaisquer chaves que já tenham sido publicadas
- Se você acidentalmente commitou chaves, revogue/regenere imediatamente (ex.: Google Cloud Console).

4) Remova segredos do histórico do Git se já foram comitados
- Use `git filter-repo` ou `bfg` para remover arquivos sensíveis do histórico. Isto reescreve o histórico remoto e requer `git push --force`.

5) Para CI e deploys
- Use GitHub Secrets ou outro gerenciador (Vault, AWS Parameter Store) e injete no runtime.

6) Boas práticas locais
- Use `direnv` ou export de variáveis no shell para evitar criar `.env` com chaves.
