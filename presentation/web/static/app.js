document.addEventListener('DOMContentLoaded', () => {
    // Intenta conectar a Socket.IO (asume que el servidor Flask/SocketIO está en el mismo host/puerto)
    // Si tu servidor está en otro lugar, reemplaza con la URL: const socket = io('http://tu-servidor.com');
    const socket = io();

    // --- Referencias a elementos del DOM ---
    const statusDiv = document.getElementById('status');
    const btnStart = document.getElementById('btnStart');
    const btnStop = document.getElementById('btnStop');
    const frequencyAnimation = document.getElementById('frequencyAnimation');
    const outputP = document.getElementById('output');
    const emotionOutputP = document.getElementById('emotionOutput');
    const keywordsOutputP = document.getElementById('keywordsOutput');
    const suggestionOutputP = document.getElementById('suggestionOutput');
    const suggestionSpinner = document.getElementById('suggestionSpinner');

    // --- Estado de la aplicación ---
    let isRecording = false;
    let isConnected = false;

    // --- Funciones auxiliares ---
    function updateStatus(message, type = 'info') {
        if (statusDiv) {
            statusDiv.textContent = message;
            statusDiv.className = `status-indicator status-${type}`; // Para estilizar diferente (info, success, error)
        }
        console.log(`Status: ${message}`);
    }

    function setRecordingState(recording) {
        isRecording = recording;
        if (btnStart) btnStart.disabled = recording || !isConnected;
        if (btnStop) btnStop.disabled = !recording || !isConnected;
        if (frequencyAnimation) {
            frequencyAnimation.classList.toggle('active', recording);
        }
        if (!recording) {
            // Resetear placeholders si no se está grabando
             resetOutputsToWaiting();
        }
    }

    function resetOutputsToWaiting() {
        if (outputP) outputP.textContent = 'Esperando inicio de grabación...';
        if (emotionOutputP) emotionOutputP.textContent = '...';
        if (keywordsOutputP) keywordsOutputP.textContent = '...';
        if (suggestionOutputP) suggestionOutputP.textContent = '...';
        if (suggestionSpinner) suggestionSpinner.style.display = 'none';
        // Limpiar clases de placeholder si se añadieron
        document.querySelectorAll('.output-placeholder').forEach(el => el.classList.add('output-placeholder'));
    }

     function clearPlaceholders() {
        document.querySelectorAll('.output-placeholder').forEach(el => el.classList.remove('output-placeholder'));
     }

    // --- Eventos de Socket.IO ---
    socket.on('connect', () => {
        isConnected = true;
        updateStatus('Conectado al servidor.', 'success');
        setRecordingState(false); // Asegurar estado inicial correcto
        resetOutputsToWaiting();
    });

    socket.on('disconnect', () => {
        isConnected = false;
        updateStatus('Desconectado del servidor. Intentando reconectar...', 'error');
        setRecordingState(false);
        isRecording = false; // Forzar estado
    });

    socket.on('connect_error', (err) => {
        isConnected = false;
        updateStatus(`Error de conexión: ${err.message}`, 'error');
        setRecordingState(false);
         isRecording = false; // Forzar estado
    });

    socket.on('status', (data) => {
        updateStatus(data.message, 'info');
        // Actualizar estado basado en mensajes específicos del backend
        if (data.message.includes("Grabación iniciada")) {
            setRecordingState(true);
            clearPlaceholders(); // Limpiar placeholders al iniciar
            outputP.textContent = "Escuchando..."; // Mensaje inicial
        } else if (data.message.includes("Grabación detenida")) {
            setRecordingState(false);
        } else if (data.message.includes("ya está en curso")) {
             setRecordingState(true); // Corregir estado si estaba desincronizado
        }
    });

    socket.on('transcription', (text) => {
        if (outputP) {
            outputP.textContent = text || outputP.textContent; // Mostrar texto o mantener el anterior si es vacío
            if (text) outputP.classList.remove('output-placeholder');
        }
    });

    socket.on('emotion', (data) => {
        if (emotionOutputP) {
            emotionOutputP.textContent = data.emotion || 'No detectada';
            emotionOutputP.classList.remove('output-placeholder');
            // Podrías mostrar más detalles si quieres, ej:
            // const details = Object.entries(data.probabilities)
            //     .map(([key, value]) => `${key}: ${Math.round(value * 100)}%`)
            //     .join(', ');
            // document.getElementById('emotionDetails').textContent = details;
        }
    });

    socket.on('keywords', (data) => {
        if (keywordsOutputP) {
            keywordsOutputP.textContent = data.keywords && data.keywords.length > 0 ? data.keywords.join(', ') : 'Ninguna detectada';
            keywordsOutputP.classList.remove('output-placeholder');
        }
    });

    socket.on('suggestion', (data) => {
        if (suggestionOutputP) {
             suggestionOutputP.textContent = data.text || 'No se pudo generar sugerencia.';
             suggestionOutputP.classList.remove('output-placeholder');
        }
        if (suggestionSpinner) suggestionSpinner.style.display = 'none'; // Ocultar spinner
    });

    // Mensaje si el backend indica que está generando sugerencia (opcional)
    socket.on('generating_suggestion', () => {
        if (suggestionOutputP) suggestionOutputP.textContent = 'Generando recomendación...';
        if (suggestionSpinner) suggestionSpinner.style.display = 'inline-block'; // Mostrar spinner
    });


    // --- Eventos de los Botones ---
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            if (isConnected) {
                console.log('Emitiendo start_recording');
                socket.emit('start_recording');
                updateStatus('Iniciando grabación...', 'info');
                // El estado de los botones se actualizará con la respuesta 'status' del servidor
                setRecordingState(true); // Actualización optimista
                clearPlaceholders();
                 outputP.textContent = "Escuchando...";
            } else {
                updateStatus('No conectado al servidor.', 'error');
            }
        });
    }

    if (btnStop) {
        btnStop.addEventListener('click', () => {
            if (isConnected) {
                console.log('Emitiendo stop_recording');
                socket.emit('stop_recording');
                updateStatus('Deteniendo grabación...', 'info');
                // El estado de los botones se actualizará con la respuesta 'status' del servidor
                setRecordingState(false); // Actualización optimista
            } else {
                updateStatus('No conectado al servidor.', 'error');
            }
        });
    }

    // --- Inicialización ---
    updateStatus('Intentando conectar...', 'info');
    setRecordingState(false); // Estado inicial seguro

}); // Fin de DOMContentLoaded