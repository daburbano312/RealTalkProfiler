from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from threading import Thread
import os
import sqlite3
from flask_cors import CORS
# --- NUEVAS IMPORTACIONES PARA LOGIN ---
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# ---------------------------------------

from core.use_cases.transcribe_stream import TranscriptionUseCase
from infrastructure.audio.vosk_speech_to_text import VoskSpeechToText
from interfaces.audio.audio_streamer import AudioStreamer
from infrastructure.emotion.text_emotion_detector import TextEmotionAnalyzer
from infrastructure.emotion.keyword_extractor import KeywordExtractor
from infrastructure.ai.openai_recommendation_engine import OpenAIRecommendationEngine
from dotenv import load_dotenv
load_dotenv()

# 🧠 Módulos de análisis
text_emotion_analyzer = TextEmotionAnalyzer()
keyword_extractor = KeywordExtractor()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ No se encontró la variable de entorno OPENAI_API_KEY. Verifica tu archivo .env o el entorno.")

recommendation_engine = OpenAIRecommendationEngine(api_key=openai_api_key)

emotion_word_buffer = []
MAX_EMOTION_WORDS = 15

# 🔧 Configuración de Flask
app = Flask(__name__,
            template_folder="presentation/web/templates",
            static_folder="presentation/web/static")
# --- NUEVA CONFIGURACIÓN PARA LOGIN ---
# Se necesita una clave secreta para manejar las sesiones de usuario de forma segura.
# ¡CAMBIA ESTO por una cadena aleatoria y segura en producción! Puedes usar os.urandom(24)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'una-clave-secreta-muy-segura-por-defecto')
# ---------------------------------------
CORS(app) # Habilita CORS para toda la app
socketio = SocketIO(app, cors_allowed_origins="*") # Permite conexiones SocketIO de cualquier origen

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
# Si un usuario no autenticado intenta acceder a una página protegida,
# será redirigido a la vista de login (la función 'login').
login_manager.login_view = 'login'
# Mensaje que se mostrará al usuario redirigido (opcional)
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info" # Categoría de mensaje flash (opcional)

# --- MODELO DE USUARIO PARA FLASK-LOGIN ---
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login usa esta función para recargar el objeto usuario desde el ID de usuario almacenado en la sesión."""
    conn = None # Inicializa conn a None
    try:
        conn = sqlite3.connect("data/inmuebles.db")
        c = conn.cursor()
        c.execute("SELECT id, email FROM usuarios WHERE id = ?", (user_id,))
        user_data = c.fetchone()
        if user_data:
            return User(id=user_data[0], email=user_data[1])
        return None
    except sqlite3.Error as e:
        print(f"Error al cargar usuario desde BD: {e}")
        return None
    finally:
        if conn:
            conn.close() # Asegura que la conexión se cierre

# ---------------------------------------

# 🔤 Transcripción
speech_to_text = VoskSpeechToText()
transcriber = TranscriptionUseCase(speech_to_text)

# Variable global para el hilo de grabación
recording_thread = None
recording_active = False

# 📞 Procesamiento de audio (sin cambios en esta función por ahora)
def handle_audio(audio_chunk):
    global emotion_word_buffer, recording_active

    if not recording_active:
        return

    if speech_to_text.accept_waveform(audio_chunk):
        result = speech_to_text.get_result()
        text = result.get("text", "").strip()

        if text:
            print(f"✅ Texto final: {text}")
            # Asegúrate de que el cliente esté conectado antes de emitir
            # (SocketIO maneja esto, pero es buena práctica considerarlo)
            socketio.emit("transcription", text)

            words = text.split()
            emotion_word_buffer += words
            print(f"🧠 Palabras acumuladas: {len(emotion_word_buffer)}")

            if len(emotion_word_buffer) >= MAX_EMOTION_WORDS:
                full_text = " ".join(emotion_word_buffer[:MAX_EMOTION_WORDS])

                # Emoción
                emotion_result = text_emotion_analyzer.analyze(full_text)
                print(f"🎭 Emoción detectada: {emotion_result['emotion']}")
                socketio.emit("emotion", emotion_result)

                # Palabras clave
                keywords = keyword_extractor.extract_keywords(full_text)
                print(f"🔑 Palabras clave: {keywords}")
                socketio.emit("keywords", {"keywords": keywords})

                # Generar sugerencia
                suggestion = recommendation_engine.generate_advice(
                    emotion_result['emotion'],
                    keywords,
                    full_text
                )
                print(f"📢 Sugerencia generada: {suggestion}")
                socketio.emit("suggestion", {"text": suggestion})

                # Limpiar buffer
                emotion_word_buffer = emotion_word_buffer[MAX_EMOTION_WORDS:]

# 🎙️ Iniciar el streaming de audio
# Nota: Asegúrate de que AudioStreamer maneje correctamente los reinicios si la app se recarga
streamer = AudioStreamer(handle_audio)


# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión del usuario."""
    if current_user.is_authenticated:
        # Si el usuario ya está autenticado, redirige al dashboard
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False # Checkbox para "Recordarme"

        if not email or not password:
             flash('Se requiere correo y contraseña.', 'warning')
             return render_template('login.html')

        conn = None
        try:
            conn = sqlite3.connect("data/inmuebles.db")
            c = conn.cursor()
            # Busca al usuario por email en la tabla 'usuarios'
            c.execute("SELECT id, email, password_hash FROM usuarios WHERE email = ?", (email,))
            user_data = c.fetchone()

            if user_data and check_password_hash(user_data[2], password):
                # Si el usuario existe y la contraseña hasheada coincide
                user = User(id=user_data[0], email=user_data[1])
                login_user(user, remember=remember) # Inicia la sesión del usuario
                flash('Inicio de sesión exitoso.', 'success')

                # Redirige al usuario a la página que intentaba acceder antes del login,
                # o al dashboard ('index') si no había ninguna página específica.
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                # Si las credenciales son incorrectas
                flash('Credenciales inválidas. Por favor, inténtalo de nuevo.', 'danger')

        except sqlite3.Error as e:
            print(f"Error de base de datos durante el login: {e}")
            flash('Ocurrió un error durante el inicio de sesión. Inténtalo más tarde.', 'danger')
        finally:
            if conn:
                conn.close()

    # Si es método GET o falla el POST, muestra el formulario de login
    return render_template('login.html')


@app.route('/logout')
@login_required # Solo usuarios autenticados pueden cerrar sesión
def logout():
    """Cierra la sesión del usuario actual."""
    logout_user() # Cierra la sesión de Flask-Login
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login')) # Redirige a la página de login

# --- RUTAS PRINCIPALES DE LA APLICACIÓN (PROTEGIDAS) ---

@app.route("/")
@login_required # Requiere que el usuario esté autenticado para ver el dashboard
def index():
    """Página principal (Dashboard)."""
    # 'current_user' está disponible en las plantillas gracias a Flask-Login
    return render_template("index.html")

@app.route("/proyectos")
@login_required # Requiere autenticación para ver la página de proyectos
def proyectos():
    """Página que muestra los proyectos inmobiliarios."""
    return render_template("projects.html")

# --- RUTAS API (PROTEGIDAS) ---

@app.route("/api/proyectos", methods=['GET'])
@login_required # Requiere autenticación para acceder a los datos de la API
def obtener_proyectos():
    """Endpoint API para obtener la lista de proyectos."""
    conn = None
    try:
        conn = sqlite3.connect("data/inmuebles.db")
        c = conn.cursor()
        c.execute("SELECT id, nombre, ubicacion, precio, descripcion FROM proyectos")
        proyectos_db = c.fetchall()

        if proyectos_db:
            proyectos_list = [
                {"id": p[0], "nombre": p[1], "ubicacion": p[2], "precio": p[3], "descripcion": p[4]}
                for p in proyectos_db
            ]
            return jsonify(proyectos_list)
        else:
            return jsonify({"message": "No se encontraron proyectos."}), 404

    except sqlite3.Error as e:
        print(f"Error de base de datos en /api/proyectos: {e}")
        return jsonify({"error": f"Error en la base de datos: {str(e)}"}), 500
    except Exception as e:
        print(f"Error inesperado en /api/proyectos: {e}")
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# --- EVENTOS DE SOCKET.IO (CON VERIFICACIÓN DE AUTENTICACIÓN) ---

@socketio.on("connect")
def connect():
    """Maneja la conexión de un cliente WebSocket."""
    # Verifica si el usuario está autenticado al momento de la conexión WebSocket
    if not current_user.is_authenticated:
         print("🔌 Cliente NO AUTENTICADO intentó conectar vía WebSocket.")
         # Puedes decidir desconectar al cliente si no está autenticado
         # return False # Descomenta esto para rechazar conexiones no autenticadas
         # O simplemente registrar el evento
         emit("status", {"message": "Conectado, pero se requiere iniciar sesión para funciones completas."})
    else:
        print(f"✅ Cliente conectado vía WebSocket: {current_user.email}")
        emit("status", {"message": "Conectado y autenticado."})


@socketio.on("start_recording")
def start_recording():
    """Inicia la grabación de audio si el usuario está autenticado."""
    global recording_thread, recording_active
    # Verifica la autenticación ANTES de iniciar cualquier proceso
    if not current_user.is_authenticated:
        print("🔒 Intento de iniciar grabación por usuario no autenticado.")
        emit("status", {"message": "Error: Debes iniciar sesión para grabar.", "type": "error"})
        return # No hace nada si no está logueado

    if not recording_active:
        recording_active = True
        print(f"🚀 Iniciando grabación para {current_user.email}...")
        # Asegúrate de que el streamer se inicialice correctamente
        # Considera si necesitas crear una nueva instancia de streamer por sesión/usuario
        try:
            recording_thread = Thread(target=streamer.start_stream)
            recording_thread.start()
            emit("status", {"message": "Grabación iniciada.", "type": "info"})
        except Exception as e:
             print(f"Error al iniciar el hilo de grabación: {e}")
             recording_active = False
             emit("status", {"message": "Error al iniciar la grabación.", "type": "error"})
    else:
        emit("status", {"message": "La grabación ya está en curso.", "type": "warning"})

@socketio.on("stop_recording")
def stop_recording():
    """Detiene la grabación de audio si el usuario está autenticado."""
    global recording_active
    # Verifica autenticación
    if not current_user.is_authenticated:
        print("🔒 Intento de detener grabación por usuario no autenticado.")
        emit("status", {"message": "Error: Debes iniciar sesión.", "type": "error"})
        return

    if recording_active:
        print(f"⏹️ Deteniendo grabación para {current_user.email}...")
        recording_active = False
        try:
            # Asegúrate de que streamer exista y tenga el método stop_stream
            streamer.stop_stream()
            # Espera a que el hilo termine si es necesario (opcional, depende de cómo manejes los hilos)
            # if recording_thread and recording_thread.is_alive():
            #     recording_thread.join()
            emit("status", {"message": "Grabación detenida.", "type": "info"})
        except Exception as e:
             print(f"Error al detener el stream de audio: {e}")
             # Aunque falle la detención del stream, marcamos como inactiva la grabación
             emit("status", {"message": "Error al detener grabación, pero se marcó como inactiva.", "type": "error"})
    else:
        emit("status", {"message": "No hay grabación en curso para detener.", "type": "warning"})


@socketio.on("disconnect")
def disconnect():
    """Maneja la desconexión de un cliente WebSocket."""
    user_email = current_user.email if current_user.is_authenticated else "Usuario no autenticado"
    print(f"🔌 Cliente desconectado: {user_email}")
    # Puedes añadir lógica de limpieza aquí si es necesario

# 🚀 Ejecutar servidor
if __name__ == "__main__":
    print("🌐 Levantando servidor Flask + SocketIO en puerto 5000")
    # debug=True es útil para desarrollo, pero ¡DESACTÍVALO en producción!
    # host='0.0.0.0' permite conexiones desde otras máquinas en la red.
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)