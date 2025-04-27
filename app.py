from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from threading import Thread
import os
import sqlite3
import json
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Core y capas
from core.use_cases.transcribe_stream import TranscriptionUseCase
from core.use_cases.manage_history_use_case import ManageHistoryUseCase
from core.use_cases.get_history_use_case import GetHistoryUseCase
from infrastructure.audio.vosk_speech_to_text import VoskSpeechToText
from infrastructure.history.history_repository import HistoryRepository
from interfaces.audio.audio_streamer import AudioStreamer
from infrastructure.emotion.text_emotion_detector import TextEmotionAnalyzer
from infrastructure.emotion.keyword_extractor import KeywordExtractor
from infrastructure.ai.openai_recommendation_engine import OpenAIRecommendationEngine

# Cargar variables de entorno
load_dotenv()

# 🧠 Módulos de análisis
text_emotion_analyzer = TextEmotionAnalyzer()
keyword_extractor = KeywordExtractor()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("❌ No se encontró la variable de entorno OPENAI_API_KEY. Verifica tu archivo .env o el entorno.")

recommendation_engine = OpenAIRecommendationEngine(api_key=openai_api_key)

# 🗃️ Historial
history_repo = HistoryRepository()
manage_history_use_case = ManageHistoryUseCase(history_repo)
get_history_use_case = GetHistoryUseCase(history_repo)

# 🔧 Configuración de Flask
app = Flask(__name__, template_folder="presentation/web/templates", static_folder="presentation/web/static")
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'una-clave-secreta-muy-segura-por-defecto')
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# 🔤 Transcripción
speech_to_text = VoskSpeechToText()
transcriber = TranscriptionUseCase(speech_to_text)

# 📋 Variables globales
recording_thread = None
recording_active = False
streamer = None
current_client_id = None
current_call_name = None
emotion_word_buffer = []
MAX_EMOTION_WORDS = 15

# 🧠 Manejo de audio
def handle_audio(audio_chunk):
    global emotion_word_buffer, recording_active, current_client_id, current_call_name

    if not recording_active:
        return

    if speech_to_text.accept_waveform(audio_chunk):
        result = speech_to_text.get_result()
        text = result.get("text", "").strip()

        if text:
            print(f"✅ Texto final: {text}")
            socketio.emit("transcription", text)
            manage_history_use_case.add_transcription(current_client_id, current_call_name, text)

            words = text.split()
            emotion_word_buffer += words

            if len(emotion_word_buffer) >= MAX_EMOTION_WORDS:
                full_text = " ".join(emotion_word_buffer[:MAX_EMOTION_WORDS])

                # Emoción
                emotion_result = text_emotion_analyzer.analyze(full_text)
                print(f"🎭 Emoción detectada: {emotion_result['emotion']}")
                socketio.emit("emotion", emotion_result)
                manage_history_use_case.add_emotion(current_client_id, current_call_name, emotion_result['emotion'], emotion_result.get('score', 1.0))

                # Palabras clave
                keywords = keyword_extractor.extract_keywords(full_text)
                print(f"🔑 Palabras clave: {keywords}")
                socketio.emit("keywords", {"keywords": keywords})

                # Sugerencia
                suggestion = recommendation_engine.generate_advice(emotion_result['emotion'], keywords, full_text)
                print(f"📢 Sugerencia generada: {suggestion}")
                socketio.emit("suggestion", {"text": suggestion})
                manage_history_use_case.add_suggestion(current_client_id, current_call_name, suggestion)

                emotion_word_buffer = emotion_word_buffer[MAX_EMOTION_WORDS:]

streamer = AudioStreamer(handle_audio)

# --- FLASK LOGIN CONFIGURACIÓN ---

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = None
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
            conn.close()

# --- RUTAS WEB Y API ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        if not email or not password:
            flash('Se requiere correo y contraseña.', 'warning')
            return render_template('login.html')

        conn = None
        try:
            conn = sqlite3.connect("data/inmuebles.db")
            c = conn.cursor()
            c.execute("SELECT id, email, password_hash FROM usuarios WHERE email = ?", (email,))
            user_data = c.fetchone()

            if user_data and check_password_hash(user_data[2], password):
                user = User(id=user_data[0], email=user_data[1])
                login_user(user, remember=remember)
                flash('Inicio de sesión exitoso.', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Credenciales inválidas.', 'danger')
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")
            flash('Error en inicio de sesión.', 'danger')
        finally:
            if conn:
                conn.close()

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

# Ruta para ver el historial de llamadas
@app.route("/historial")
@login_required
def historial():
    return render_template("historial.html")


# Ruta para obtener el historial de llamadas en formato JSON
@app.route("/api/historial", methods=['GET'])
@login_required
def obtener_historial():
    client_id = request.args.get('client_id', None)
    conn = None
    try:
        conn = sqlite3.connect("data/inmuebles.db")
        c = conn.cursor()

        # Si client_id es proporcionado, filtramos
        if client_id:
            c.execute("SELECT client_id, call_name, transcriptions FROM historial WHERE client_id = ?", (client_id,))
        else:
            c.execute("SELECT client_id, call_name, transcriptions FROM historial")

        historial_data = c.fetchall()

        # Formatear el historial
        historial_list = []
        for data in historial_data:
            historial_list.append({
                "client_id": data[0],
                "call_name": data[1],
                "transcriptions": json.loads(data[2])  # Asegúrate de convertir las transcripciones a JSON
            })

        return jsonify(historial_list)  # Asegúrate de devolver un JSON válido
    except sqlite3.Error as e:
        print(f"Error al obtener historial: {e}")
        return jsonify({"error": "Error al obtener historial."}), 500
    finally:
        if conn:
            conn.close()



@app.route("/proyectos")
@login_required
def proyectos():
    return render_template("projects.html")

@app.route("/api/proyectos", methods=['GET'])
@login_required
def obtener_proyectos():
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
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"{str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/historial/<client_id>", methods=["GET"])
@login_required
def obtener_historial_cliente(client_id):
    historial = get_history_use_case.get_client_history(client_id)
    if historial:
        data = historial.to_dict()

        try:
            conn = sqlite3.connect("data/inmuebles.db")
            c = conn.cursor()

            for call_name, call_data in data["calls"].items():
                # Verificar si ya existe el registro
                c.execute('''
                    SELECT id FROM historial WHERE client_id = ? AND call_name = ?
                ''', (data["client_id"], call_name))
                existing = c.fetchone()

                transcriptions = json.dumps(call_data.get("transcriptions", []))
                emotions = json.dumps(call_data.get("emotions", []))
                suggestions = json.dumps(call_data.get("suggestions", []))

                if existing:
                    # Si existe, actualizar
                    print(f"📝 Actualizando historial de '{call_name}' para '{data['client_id']}'")
                    c.execute('''
                        UPDATE historial
                        SET transcriptions = ?, emotions = ?, suggestions = ?
                        WHERE id = ?
                    ''', (transcriptions, emotions, suggestions, existing[0]))
                else:
                    # Si no existe, insertar
                    print(f"➕ Insertando nueva llamada '{call_name}' para '{data['client_id']}'")
                    c.execute('''
                        INSERT INTO historial (client_id, call_name, transcriptions, emotions, suggestions)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (data["client_id"], call_name, transcriptions, emotions, suggestions))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Error guardando historial en la BD: {e}")

        return jsonify(data)
    else:
        return jsonify({"message": "No se encontró historial."}), 404

# --- SOCKET.IO EVENTOS ---

@socketio.on("connect")
def socket_connect():
    if not current_user.is_authenticated:
        print("🔒 Cliente NO autenticado vía WebSocket.")
        emit("status", {"message": "Conectado, pero necesitas iniciar sesión."})
    else:
        print(f"✅ Cliente WebSocket autenticado: {current_user.email}")
        emit("status", {"message": "Conectado y autenticado."})

@socketio.on("start_recording")
def start_recording(data=None):
    global recording_thread, recording_active, current_client_id, current_call_name, streamer

    if not current_user.is_authenticated:
        emit("status", {"message": "Error: debes iniciar sesión para grabar."})
        return

    # PEDIR explícitamente la cédula
    if not data or "cedula" not in data:
        emit("status", {"message": "Error: debes enviar la cédula del cliente."})
        return

    client_id_input = data["cedula"]

    if not recording_active:
        streamer = AudioStreamer(lambda chunk: handle_audio(chunk))
        recording_active = True
        current_client_id = client_id_input
        current_call_name = manage_history_use_case.start_new_call(current_client_id)

        try:
            recording_thread = Thread(target=streamer.start_stream)
            recording_thread.start()
            emit("status", {"message": "Grabación iniciada."})
        except Exception as e:
            print(f"Error al iniciar grabación: {e}")
            recording_active = False
            emit("status", {"message": "Error iniciando grabación."})
    else:
        emit("status", {"message": "La grabación ya está en curso."})

@socketio.on("stop_recording")
def stop_recording():
    global recording_active, streamer

    if not current_user.is_authenticated:
        emit("status", {"message": "Error: debes iniciar sesión."})
        return

    if recording_active:
        recording_active = False
        try:
            if streamer:
                streamer.stop_stream()
            emit("status", {"message": "Grabación detenida."})
        except Exception as e:
            print(f"Error al detener grabación: {e}")
            emit("status", {"message": "Error al detener grabación."})
    else:
        emit("status", {"message": "No hay grabación en curso."})

@socketio.on("disconnect")
def socket_disconnect():
    user_email = current_user.email if current_user.is_authenticated else "Usuario no autenticado"
    print(f"🔌 Cliente desconectado: {user_email}")

# --- Ejecutar servidor ---
if __name__ == "__main__":
    print("🌐 Levantando servidor Flask + SocketIO en puerto 5000")
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
