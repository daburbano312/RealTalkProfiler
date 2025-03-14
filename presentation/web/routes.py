# presentation/web/routes.py
from flask import jsonify, request, session
from werkzeug.exceptions import BadRequest, InternalServerError
from flask_socketio import emit  # Nuevo import
import logging
import time
import uuid
import json

def configure_routes(app, socketio, audio_processor, emotion_analyzer, suggestion_generator):
    
    @app.route('/')
    def index():
        return '<h1>Bienvenido al Dashboard de Análisis de Emociones</h1>'

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "ok",
            "timestamp": time.time(),
            "services": {
                "audio_processing": "active",
                "emotion_analysis": "active",
                "suggestion_generation": "active"
            }
        })

    @app.route('/api/analyze/audio', methods=['POST'])
    def analyze_audio():
        try:
            if 'audio' not in request.files:
                raise BadRequest("No audio file provided")
            
            audio_file = request.files['audio']
            session_id = request.form.get('session_id', str(uuid.uuid4()))
            
            audio_data = audio_file.read()
            transcription = audio_processor.process_audio(audio_data)
            emotion_analysis = emotion_analyzer.analyze_audio(audio_data)
            
            suggestions = suggestion_generator.generate_from_emotion(
                emotion_analysis,
                context={
                    "session_id": session_id,
                    "text": transcription.text
                }
            )
            
            return jsonify({
                "session_id": session_id,
                "transcription": transcription.to_dict(),
                "emotion_analysis": emotion_analysis.to_dict(),
                "suggestions": [s.to_dict() for s in suggestions]
            })
            
        except Exception as e:
            logging.error(f"Audio analysis error: {str(e)}")
            raise InternalServerError("Error processing audio")

    @app.route('/api/analyze/text', methods=['POST'])
    def analyze_text():
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                raise BadRequest("Missing text in request body")
            
            emotion_analysis = emotion_analyzer.analyze_text(data['text'])
            suggestions = suggestion_generator.generate_from_text(
                data['text'],
                context=data.get('context', {})
            )
            
            return jsonify({
                "text": data['text'],
                "emotion_analysis": emotion_analysis.to_dict(),
                "suggestions": [s.to_dict() for s in suggestions]
            })
            
        except Exception as e:
            logging.error(f"Text analysis error: {str(e)}")
            raise InternalServerError("Error processing text")

    # WebSocket implementation con SocketIO
    @socketio.on('real_time_audio')  # Usa la instancia socketio
    def handle_real_time_stream(data):
        session_id = str(uuid.uuid4())
        buffer = bytearray(data['audio_chunk'])
        
        try:
            if len(buffer) >= 4096:
                chunk = bytes(buffer[:4096])
                transcription = audio_processor.process_audio(chunk)
                emotion_analysis = emotion_analyzer.analyze_audio(chunk)
                
                emit('audio_update', {
                    "session_id": session_id,
                    "partial_text": transcription.text,
                    "emotion": emotion_analysis.predominant_emotion.value,
                    "confidence": emotion_analysis.confidence
                })
                
        except Exception as e:
            logging.error(f"WebSocket error: {str(e)}")
            emit('error', {'message': str(e)})

    @socketio.on('finalize_audio')  # Usa la instancia socketio
    def handle_final_audio(data):
        try:
            final_transcription = audio_processor.process_audio(data['final_audio'])
            emotion_analysis = emotion_analyzer.analyze_audio(data['final_audio'])
            suggestions = suggestion_generator.generate_from_transcription(final_transcription)
            
            emit('final_result', {
                "session_id": data['session_id'],
                "final_text": final_transcription.text,
                "emotion_analysis": emotion_analysis.to_dict(),
                "suggestions": [s.to_dict() for s in suggestions]
            })
            
        except Exception as e:
            logging.error(f"Final processing error: {str(e)}")

    # Resto del código sin cambios...
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            "error": "Bad Request",
            "message": str(e.description)
        }), 400

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500

    @app.route('/api/history/<session_id>', methods=['GET'])
    def get_session_history(session_id):
        return jsonify({
            "session_id": session_id,
            "data": "Historial no implementado"
        })

    @app.route('/api/feedback', methods=['POST'])
    def save_feedback():
        try:
            data = request.get_json()
            return jsonify({"status": "Feedback recibido"})
        except Exception as e:
            logging.error(f"Feedback error: {str(e)}")
            raise InternalServerError("Error saving feedback")