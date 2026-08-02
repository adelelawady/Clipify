

<p align="center"> <img src="https://github.com/user-attachments/assets/876170d2-523c-4045-b4c9-67ac957e46c1" alt="Clipify Logo" width="150"> </p>

# Clipify

> Un kit de herramientas de procesamiento de video impulsado por IA para crear contenido optimizado para redes sociales con transcripción automatizada, subtítulos y segmentación temática.

[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/adelelawady/clipify)
[![PyPI version](https://img.shields.io/pypi/v/clipify.svg)](https://pypi.org/project/clipify/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://github.com/adelelawady/clipify)
[![License](https://img.shields.io/pypi/l/clipify.svg)](https://github.com/adelelawady/clipify/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/clipify.svg)](https://pypi.org/project/clipify/)
[![GitHub stars](https://img.shields.io/github/stars/adelelawady/Clipify.svg)](https://github.com/adelelawady/Clipify/stargazers)
[![Documentation Status](https://img.shields.io/badge/docs-passing-brightgreen.svg)](https://github.com/adelelawady/Clipify#readme)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<a href="https://pepy.tech/project/Clipify">
    <img src="https://static.pepy.tech/badge/Clipify" alt="Downloads">
  </a>
## 🌟 Características Principales

### Procesamiento de Contenido
- **Pipeline de Procesamiento de Video**
  - Extracción automática de audio y conversión de voz a texto
  - Segmentación temática inteligente usando IA
  - Conversión de formato optimizado para móviles (9:16, 4:5, 1:1)
  - Generación y superposición inteligente de subtítulos

### Capacidades de IA
- **Análisis Avanzado**
  - Segmentación de contenido con contexto
  - Generación dinámica de títulos
  - Extracción inteligente de palabras clave y hashtags
  - Análisis de sentimiento para optimización de contenido

### Opciones de Plataforma
- **Aplicación de Escritorio**
  - Interfaz gráfica intuitiva
  - Funcionalidad de arrastrar y soltar
  - Retroalimentación de procesamiento en tiempo real
  - Capacidades de procesamiento por lotes

- **Despliegue en Servidor**
  - Integración con API RESTful
  - Procesamiento asíncrono con webhooks
  - Arquitectura multi-inquilino
  - Soporte para despliegue en contenedores

## 🚀 Inicio Rápido

### Aplicación de Escritorio

🚀 Consulta nuestro proyecto completo basado en Clipify en [https://github.com/adelelawady/Clipify-hub](https://github.com/adelelawady/Clipify-hub) 🚀

Descarga e instala la última versión:

<p align="center">
  <a href="https://github.com/adelelawady/Clipify-Hub/releases/download/3.3.0/clipify-hub-installer.exe">
    <img src="https://img.shields.io/badge/Download-Installable%20App-blue?style=for-the-badge&logo=windows" alt="Download Installable">
  </a>
  <a href="https://github.com/adelelawady/Clipify-Hub/releases/download/3.3.0/clipify-hub-server.exe">
    <img src="https://img.shields.io/badge/Download-Server%20Only-green?style=for-the-badge&logo=docker" alt="Download Server">
  </a>
</p>

### Instalación del Paquete Python

```bash
# Via pip
pip install clipify

# From source
git clone https://github.com/adelelawady/Clipify.git
cd Clipify
pip install -r requirements.txt
```

## 💻 Ejemplos de Uso

### Implementación Básica
```python
from clipify.core.clipify import Clipify

# Initialize with basic configuration
clipify = Clipify(
    provider_name="hyperbolic",
    api_key="your-api-key",
    model="deepseek-ai/DeepSeek-V3",
    convert_to_mobile=True,
    add_captions=True
)

# Process video
result = clipify.process_video("input.mp4")

# Handle results
if result:
    print(f"Created {len(result['segments'])} segments")
    for segment in result['segments']:
        print(f"Segment {segment['segment_number']}: {segment['title']}")
```

### Configuración Avanzada
```python
clipify = Clipify(
    # AI Configuration
    provider_name="hyperbolic",
    api_key="your-api-key",
    model="deepseek-ai/DeepSeek-V3",
    max_tokens=5048,
    temperature=0.7,
    
    # Video Processing
    convert_to_mobile=True,
    add_captions=True,
    mobile_ratio="9:16",
    
    # Caption Styling
    caption_options={
        "font": "Bangers-Regular.ttf",
        "font_size": 60,
        "font_color": "white",
        "stroke_width": 2,
        "stroke_color": "black",
        "highlight_current_word": True,
        "word_highlight_color": "red",
        "shadow_strength": 0.8,
        "shadow_blur": 0.08,
        "line_count": 1,
        "padding": 50,
        "position": "bottom"
    }
)
```


## AudioExtractor


```python
from clipify.audio.extractor import AudioExtractor

# Initialize audio extractor
extractor = AudioExtractor()

# Extract audio from video
audio_path = extractor.extract_audio(
    video_path="input_video.mp4",
    output_path="extracted_audio.wav"
)

if audio_path:
    print(f"Audio successfully extracted to: {audio_path}")
```

##  SpeechToText

```python
from clipify.audio.speech import SpeechToText

# Initialize speech to text converter
converter = SpeechToText(model_size="base")  # Options: tiny, base, small, medium, large

# Convert audio to text with timing
result = converter.convert_to_text("audio_file.wav")

if result:
    print("Transcript:", result['text'])
    print("\nWord Timings:")
    for word in result['word_timings'][:5]:  # Show first 5 words
        print(f"Word: {word['text']}")
        print(f"Time: {word['start']:.2f}s - {word['end']:.2f}s")
```

## VideoConverter

```python
from clipify.video.converter import VideoConverter

# Initialize video converter
converter = VideoConverter()

# Convert video to mobile format with blurred background
result = converter.convert_to_mobile(
    input_video="landscape_video.mp4",
    output_video="mobile_video.mp4",
    target_ratio="9:16"  # Options: "1:1", "4:5", "9:16"
)

if result:
    print("Video successfully converted to mobile format")
```


## VideoConverterStretch


```python
from clipify.video.converterStretch import VideoConverterStretch

# Initialize stretch converter
stretch_converter = VideoConverterStretch()

# Convert video using stretch method
result = stretch_converter.convert_to_mobile(
    input_video="landscape.mp4",
    output_video="stretched.mp4",
    target_ratio="4:5"  # Options: "1:1", "4:5", "9:16"
)

if result:
    print("Video successfully converted using stretch method")
```


## VideoProcessor

```python
from clipify.video.processor import VideoProcessor

# Initialize video processor with caption styling
processor = VideoProcessor(
    # Font settings
    font="Bangers-Regular.ttf",
    font_size=60,
    font_color="white",
    
    # Text effects
    stroke_width=2,
    stroke_color="black",
    shadow_strength=0.8,
    shadow_blur=0.08,
    
    # Caption behavior
    highlight_current_word=True,
    word_highlight_color="red",
    line_count=1,
    padding=50,
    position="bottom"  # Options: "bottom", "top", "center"
)

# Process video with captions
result = processor.process_video(
    input_video="input_video.mp4",
    output_video="captioned_output.mp4",
    use_local_whisper="auto"  # Options: "auto", True, False
)

if result:
    print("Video successfully processed with captions")

# Process multiple video segments
segment_files = ["segment1.mp4", "segment2.mp4", "segment3.mp4"]
processed_segments = processor.process_video_segments(
    segment_files=segment_files,
    output_dir="processed_segments"
)
```

VideoProcessor proporciona capacidades potentes de subtítulos:
- Estilización de fuentes y efectos de texto personalizables
- Resaltado a nivel de palabra para mejor legibilidad
- Efectos de sombra y contorno para visibilidad
- Reconocimiento automático de voz usando Whisper
- Soporte para procesamiento por lotes de múltiples segmentos

## VideoCutter

```python
from clipify.video.cutter import VideoCutter

# Initialize video cutter
cutter = VideoCutter()

# Cut a specific segment
result = cutter.cut_video(
    input_video="full_video.mp4",
    output_video="segment.mp4",
    start_time=30.5,  # Start at 30.5 seconds
    end_time=45.2     # End at 45.2 seconds
)

if result:
    print("Video segment successfully cut")
``` 


## SmartTextProcessor

```python
from clipify.core.text_processor import SmartTextProcessor
from clipify.core.ai_providers import HyperbolicAI

# Initialize AI provider and text processor
ai_provider = HyperbolicAI(api_key="your_api_key")
processor = SmartTextProcessor(ai_provider)

# Process text content
text = "Your long text content here..."
segments = processor.segment_by_theme(text)

if segments:
    for segment in segments['segments']:
        print(f"\nTitle: {segment['title']}")
        print(f"Keywords: {', '.join(segment['keywords'])}")
        print(f"Content length: {len(segment['content'])} chars")
```

## 📦 Estructura del Proyecto
```
clipify/
├── clipify/
│   ├── __init__.py           # Package exports and version info
│   ├── core/
│   │   ├── __init__.py       # Core module exports
│   │   ├── clipify.py        # Main Clipify class implementation
│   │   ├── processor.py      # Content processing and segmentation
│   │   ├── text_processor.py # Text analysis and theme detection
│   │   └── ai_providers.py  # AI providers (OpenAI, Anthropic, Hyperbolic)
│   ├── video/
│   │   ├── __init__.py       # Video module exports
│   │   ├── processor.py      # Video captioning and effects
│   │   ├── converter.py      # Mobile format with blur background
│   │   ├── converter_stretch.py  # Stretch-based format conversion
│   │   └── cutter.py         # Video segment extraction
│   ├── audio/
│   │   ├── __init__.py       # Audio module exports
│   │   ├── extractor.py      # FFmpeg-based audio extraction
│   │   └── speech.py         # Whisper speech recognition
├── scripts/
│   ├── build.sh              # Package build script
│   └── publish.sh            # PyPI publishing script
├── .gitignore                # Git ignore patterns
├── LICENSE                 # MIT License
├── MANIFEST.in             # Package manifest
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
└── setup.py  # Package configuration


```

## 🛠️ Opciones de Configuración

### Proveedores de IA
- `hyperbolic`: Proveedor predeterminado con el modelo DeepSeek-V3
- `openai`: Soporte para modelos GPT de OpenAI
- `anthropic`: Modelos Claude de Anthropic
- `ollama`: Despliegue de modelos locales

### Configuración del Proveedor de IA (Gemini / OpenAI)

Puedes elegir qué proveedor de IA usar para la extracción de destacados. Por defecto, la interfaz y el pipeline usan Google Gemini, pero también se admite OpenAI.

- Variables de entorno (configurar en `.env`):
  - `GOOGLE_API_KEY` — Clave API para Google Generative AI (Gemini).
  - `OPENAI_API_KEY` — Clave API para OpenAI (si deseas usar modelos de OpenAI).
  - `GEMINI_MODEL` — nombre opcional del modelo Gemini predeterminado (p. ej. `gemini-2.5-flash`).
  - `OPENAI_MODEL` — nombre opcional del modelo OpenAI predeterminado (p. ej. `gpt-4o-mini`).
  - `AI_PROVIDER` — proveedor predeterminado opcional (`gemini` o `openai`). Predeterminado: `gemini`.

- En la interfaz de Gradio, puedes anular las claves por ejecución ingresándolas en los campos de Clave API de Gemini/OpenAI.

El pipeline intentará usar el proveedor seleccionado y recurrirá a un selector de destacados determinista simple si el proveedor falla.

### Formatos de Video
- Relaciones de Aspecto: `1:1`, `4:5`, `9:16`
- Formatos de Salida: MP4, MOV
- Preajustes de Calidad: Baja, Media, Alta

### Personalización de Subtítulos
- Personalización de fuentes
- Esquemas de color
- Opciones de posición
- Efectos de animación
- Resaltado de palabras

## 🤝 Contribuir

¡Bienvenidas las contribuciones! Así es como puedes ayudar:

1. Haz un fork del repositorio
2. Crea una rama de características (`git checkout -b feature/amazing-feature`)
3. Commitea los cambios (`git commit -m 'Add amazing feature'`)
4. Envía a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

Por favor, lee nuestras [Guías de Contribución](LICENSE.md) para más detalles.

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🌐 Soporte

- Soporte Empresarial: Contacta a adel50ali5b@gmail.com
- Soporte Comunitario: [Issues de GitHub](https://github.com/adelelawady/Clipify/issues)
- Documentación: [Wiki](https://github.com/adelelawady/Clipify)

## 🙏 Agradecimientos

- FFmpeg por el procesamiento de video

## 🔧 Primeros pasos (desarrollo local)

1. Copia `.env.example` a `.env` y completa tus claves API (no hagas commit de `.env`):

```bash
cp .env.example .env
# edit .env and add your keys
```

2. Crea y activa un entorno virtual de Python, instala las dependencias:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Inicia la interfaz de Gradio:

```bash
python ui/app_gradio.py
```

4. Abre la aplicación en tu navegador en http://127.0.0.1:7860 (o el puerto configurado en `GRADIO_SERVER_PORT`).

5. Sube un video y presiona "Generate clips". Los segmentos generados se escriben en `segmented_videos/input/` y la salida procesada aparece en `processed_videos/`.

- OpenAI por las capacidades de IA
- Comunidad de PyTorch
- Todos los contribuyentes y seguidores

---

<p align="center">
  <a href="https://buymeacoffee.com/adel50ali5b">
    <img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-☕-yellow.svg" alt="Buy me a coffee">
  </a>
</p>
