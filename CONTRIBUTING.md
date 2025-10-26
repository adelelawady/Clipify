# Contributing

Thanks for wanting to contribute to Clipify! A few simple guidelines to get you started.

1. Fork the repository and create a feature branch (prefix with `feature/` or `fix/`).
2. Keep changes small and focused; open a PR when ready for review.
3. Run tests locally before opening a PR:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
pytest
```

4. Do not commit secrets. Use `.env.example` as a template and add your keys to a local `.env` (which is gitignored).
5. Be descriptive in your PR title and include a short summary of changes.

Maintainers may request changes or ask you to split large PRs.
