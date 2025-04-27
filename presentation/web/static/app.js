document.addEventListener('DOMContentLoaded', () => {
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
            statusDiv.className = `status-indicator status-${type}`;
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
            resetOutputsToWaiting();
        }
    }

    function resetOutputsToWaiting() {
        if (outputP) outputP.textContent = 'Esperando inicio de grabación...';
        if (emotionOutputP) emotionOutputP.textContent = '...';
        if (keywordsOutputP) keywordsOutputP.textContent = '...';
        if (suggestionOutputP) suggestionOutputP.textContent = '...';
        if (suggestionSpinner) suggestionSpinner.style.display = 'none';
        document.querySelectorAll('.output-placeholder').forEach(el => el.classList.add('output-placeholder'));
    }

    function clearPlaceholders() {
        document.querySelectorAll('.output-placeholder').forEach(el => el.classList.remove('output-placeholder'));
    }

    // --- Eventos de Socket.IO ---
    socket.on('connect', () => {
        isConnected = true;
        updateStatus('Conectado al servidor.', 'success');
        setRecordingState(false);
        resetOutputsToWaiting();
    });

    socket.on('disconnect', () => {
        isConnected = false;
        updateStatus('Desconectado del servidor. Intentando reconectar...', 'error');
        setRecordingState(false);
        isRecording = false;
    });

    socket.on('connect_error', (err) => {
        isConnected = false;
        updateStatus(`Error de conexión: ${err.message}`, 'error');
        setRecordingState(false);
        isRecording = false;
    });

    socket.on('status', (data) => {
        updateStatus(data.message, 'info');
        if (data.message.includes("Grabación iniciada")) {
            setRecordingState(true);
            clearPlaceholders();
            outputP.textContent = "Escuchando...";
        } else if (data.message.includes("Grabación detenida")) {
            setRecordingState(false);
        } else if (data.message.includes("ya está en curso")) {
            setRecordingState(true);
        }
    });

    socket.on('transcription', (text) => {
        if (outputP) {
            outputP.textContent = text || outputP.textContent;
            if (text) outputP.classList.remove('output-placeholder');
        }
    });

    socket.on('emotion', (data) => {
        if (emotionOutputP) {
            emotionOutputP.textContent = data.emotion || 'No detectada';
            emotionOutputP.classList.remove('output-placeholder');
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
        if (suggestionSpinner) suggestionSpinner.style.display = 'none';
    });

    socket.on('generating_suggestion', () => {
        if (suggestionOutputP) suggestionOutputP.textContent = 'Generando recomendación...';
        if (suggestionSpinner) suggestionSpinner.style.display = 'inline-block';
    });

    // --- Eventos de los Botones ---
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            if (isConnected) {
                const cedula = prompt("Por favor, ingrese la cédula del cliente:");

                if (cedula && cedula.trim() !== "") {
                    console.log('Emitiendo start_recording con cédula:', cedula.trim());
                    socket.emit('start_recording', { cedula: cedula.trim() });
                    window.currentCedula = cedula.trim(); // 🚨 Guardar cédula globalmente
                    updateStatus('Iniciando grabación...', 'info');
                    setRecordingState(true);
                    clearPlaceholders();
                    outputP.textContent = "Escuchando...";
                } else {
                    alert("Debe ingresar una cédula válida para iniciar la grabación.");
                }
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
                setRecordingState(false);

                // 🚨 NUEVO: Consumir automáticamente la API de historial al detener
                if (window.currentCedula && window.currentCedula.trim() !== "") {
                    fetch(`/api/historial/${window.currentCedula.trim()}`)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error('Error al guardar historial en la base de datos.');
                            }
                            return response.json();
                        })
                        .then(data => {
                            console.log('Historial guardado correctamente en la base de datos.');

                            // 🚨 Mostrar notificación de éxito (Toast)
                            showToast("Historial guardado correctamente.", "success");
                        })
                        .catch(error => {
                            console.error('Error al consumir API de historial:', error);
                            showToast("Error al guardar historial.", "error");
                        });
                } else {
                    console.warn('⚠ No hay cédula registrada para guardar historial.');
                }
            } else {
                updateStatus('No conectado al servidor.', 'error');
            }
        });
    }

    // 🚨 NUEVO: Función para mostrar el Toast
    function showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
    
        // Crear el botón "Ver Historial"
        const viewButton = document.createElement('button');
        viewButton.textContent = 'Ver Historial';
        viewButton.style.marginLeft = '10px';
        viewButton.style.padding = '5px 10px';
        viewButton.style.backgroundColor = '#007bff';
        viewButton.style.color = 'white';
        viewButton.style.border = 'none';
        viewButton.style.borderRadius = '5px';
        viewButton.style.cursor = 'pointer';
    
        // Función para redirigir al historial
        viewButton.addEventListener('click', () => {
            const cedula = window.currentCedula;  // Usamos la cédula guardada globalmente
            if (cedula) {
                // Redirigir al historial usando la cédula del cliente
                window.location.href = `/api/historial/${cedula}`;
            }
        });
    
        // Estilo básico para el Toast (puedes personalizar)
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.backgroundColor = type === "success" ? '#28a745' : '#dc3545';
        toast.style.color = 'white';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '5px';
        toast.style.fontSize = '16px';
        toast.style.zIndex = '9999';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.justifyContent = 'space-between';
    
        // Añadir el botón al toast
        toast.appendChild(viewButton);
    
        // Mostrar el toast en la pantalla
        document.body.appendChild(toast);
    
        // Desaparecer el toast después de 3 segundos
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 500);
        }, 3000);
    }    

    // --- Inicialización ---
    updateStatus('Intentando conectar...', 'info');
    setRecordingState(false);

}); // Fin de DOMContentLoaded
