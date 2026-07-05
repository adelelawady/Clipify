# Como preparar o repositório para publicar no seu GitHub

Siga estes passos para limpar segredos, preparar e subir o repositório para o seu GitHub pessoal.

1) Remova o tracking de arquivos de ambiente (não apaga local):

```bash
git rm --cached .env .env.save || true
git add .gitignore .env.example
git commit -m "Stop tracking env files and add example"
```

2) Verifique e revogue chaves expostas
- Revogue a Google API key que foi exposta (vá ao Google Cloud Console -> Credentials).

3) (Opcional, avançado) Remova segredos do histórico
- Use `git-filter-repo` ou `bfg` para remover arquivos do histórico (requer push --force). Veja `scripts/cleanse_secrets.sh`.

4) Crie um repo no GitHub (via UI) e adicione como remoto:

```bash
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:SEU_USUARIO/SEU_REPO.git
git branch -M main
git push -u origin main
```

5) Como usar chaves em outros computadores
- Não compartilhe `.env` no controle de versão. Em outra máquina:
  - clone o repo
  - copie `.env.example` para `.env` e preencha suas chaves
    ```bash
    cp .env.example .env
    nano .env
    ```
  - ou exporte chaves no shell (por exemplo, em `~/.zshrc`)

6) CI / Github Actions
- Armazene secrets em Settings → Secrets and variables → Actions e use-os em workflows com `secrets.YOUR_SECRET`.
