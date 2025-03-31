# 🧠 RealTalk Profiler

RealTalk Profiler es una aplicación que graba tu voz, transcribe lo que dices, analiza tus emociones tanto por audio como por texto, y genera una sugerencia empática con ayuda de inteligencia artificial.

---

## 📁 Estructura del Proyecto

```
RealTalkProfiler/
├── config/
│   └── settings.py
├── core/
│   ├── entities/
│   └── use_cases/
├── infrastructure/
│   ├── ai/
│   ├── audio/
│   └── emotion/
├── interfaces/
│   ├── ai/
│   ├── audio/
│   └── emotion_detection/
├── libs/
│   └── OpenVokaturi-4-0-win64.dll
├── models/
│   └── vosk/
│       └── es/
├── presentation/
│   ├── backend/
│   │   ├── app.py
│   │   └── routes.py
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── script.js
├── .env
└── requirements.txt
```

---

## ⚙️ Requisitos

- Python 3.10 o superior
- pip
- Navegador moderno (Chrome, Firefox, Edge)
- Acceso a un micrófono

---

## 📦 Instalación

1. **Clona el repositorio**:

```bash
git clone https://github.com/tu_usuario/realtalk-profiler.git
cd realtalk-profiler
```

2. **Crea y activa un entorno virtual**:

```bash
python -m venv env
env\Scripts\activate  # En Windows
```

3. **Instala dependencias**:

```bash
pip install -r requirements.txt
```

4. **Configura tus variables de entorno** (en `.env`):

```env
OPENAI_API_KEY=sk-**************
VOKATURI_DLL_PATH=libs/OpenVokaturi-4-0-win64.dll
AUDIO_SAMPLE_RATE=48000
```

---

## ▶️ Ejecución

### 🧠 Backend

```bash
python -m presentation.backend.app
```

Accede a: [http://localhost:5000](http://localhost:5000)

---

## 🖥️ Uso

1. Abre la app en el navegador.
2. Presiona el botón `🔴 Procesar Audio`.
3. Habla claramente durante unos segundos.
4. Verás:
   - 📃 Transcripción
   - 🎤 Emoción por voz (Vokaturi)
   - ✍️ Emoción por texto (OpenAI + Pysentimiento)
   - 💡 Sugerencia empática basada en tu estado emocional

---

## 🧠 Créditos

- Voz a texto: [Vosk](https://alphacephei.com/vosk/)
- Detección de emociones por voz: [Vokaturi](https://www.vokaturi.com/)
- Análisis emocional por texto: [Pysentimiento](https://github.com/josecannete/pysentimiento) + [OpenAI GPT]
- Frontend simple: HTML + CSS + JS
- Backend: Python + Flask + WebSockets

---

## ⚠️ Nota

Este proyecto es solo una demo técnica. No reemplaza apoyo psicológico profesional.

---

## 🫶 ¡Gracias por usar RealTalk Profiler!