# Clipify — Guia de Execução

Referência rápida para rodar o projeto Clipify (UI Gradio) em qualquer máquina.

---

## ✅ Pré-requisitos

- Python 3.11
- `git`
- `ffmpeg`
- ImageMagick (`magick`)
- Chave de API do Google Gemini ou OpenAI

### Instalar ffmpeg (macOS)
```bash
brew install ffmpeg
```

### Instalar ImageMagick (macOS via Miniforge)
```bash
curl -L -o miniforge.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh
bash miniforge.sh -b -p $HOME/miniforge3
$HOME/miniforge3/bin/conda install -y -c conda-forge imagemagick
```

---

## 🚀 Primeira vez no computador

### 1. Clonar o repositório
```bash
cd ~/Projects
git clone https://github.com/diegomcolucci/Clipify.git
cd Clipify
```

### 2. Criar ambiente virtual e instalar dependências
```bash
python3.11 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

### 3. Configurar chaves de API
```bash
cp .env.example .env
```
Edite o arquivo `.env` e adicione sua chave:
```bash
GOOGLE_API_KEY=sua_chave_aqui
```

Ou para OpenAI:
```bash
OPENAI_API_KEY=sua_chave_aqui
```

---

## ▶️ Rodar a UI

```bash
cd /Users/diegomcolucci/Projects/Clipify
./scripts/run_gradio.sh
```

Acesse no navegador:
```
http://127.0.0.1:7860
```

---

## 🧪 Verificar se está tudo funcionando

### Verificação rápida de sintaxe
```bash
./venv/bin/python -m py_compile ui/app_gradio.py clipify/pipelines/ui_helpers.py clipify/video/processor.py clipify/pipelines/gemini_pipeline.py
```

### Rodar testes unitários
```bash
./venv/bin/python -m pytest tests/test_providers.py -v
```

### Teste completo
1. Rode `./scripts/run_gradio.sh`
2. Faça upload de um vídeo curto
3. Clique em **Auto-suggest params** (opcional)
4. Clique em **Generate**
5. Verifique se os clips gerados têm áudio e legenda corretos

---

## 🛠️ Comandos úteis

### Ver status do Git
```bash
git status --short
git log --oneline -5
```

### Atualizar o projeto
```bash
git pull origin develop
```

### Reinstalar dependências
```bash
./venv/bin/pip install -r requirements.txt --force-reinstall
```

---

## ⚠️ Problemas comuns

### `magick` não encontrado
O script `run_gradio.sh` tenta adicionar `$HOME/miniforge3/bin` ao PATH automaticamente. Se ainda falhar:
```bash
export PATH="$HOME/miniforge3/bin:$PATH"
./scripts/run_gradio.sh
```

### Erro de API key
Verifique se o arquivo `.env` existe e tem a chave correta:
```bash
cat .env
```

### Transcrição lenta na primeira vez
O Whisper baixa o modelo `base` na primeira execução. Isso é normal.

---

## 📁 Arquivos importantes

- `ui/app_gradio.py` — interface Gradio
- `clipify/pipelines/gemini_pipeline.py` — highlights e alinhamento
- `clipify/pipelines/ui_helpers.py` — ffmpeg + transcrição Whisper
- `clipify/video/processor.py` — queima de legendas
- `scripts/run_gradio.sh` — launcher
