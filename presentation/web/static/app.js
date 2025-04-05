const socket = io();

const btnStart = document.getElementById('btnStart');
const btnStop = document.getElementById('btnStop');

let transcription = "";
let allKeywords = []; // 🔑 Acumulador global de keywords

// Enviar evento para iniciar grabación
btnStart.addEventListener('click', () => {
    socket.emit('start_recording');
  });
  
  // Enviar evento para detener grabación
  btnStop.addEventListener('click', () => {
    socket.emit('stop_recording');
  });
  
  // Actualizar el estado de la aplicación
  socket.on('status', (data) => {
    statusDiv.textContent = data.message;
  });

socket.on("transcription", (data) => {
    const output = document.getElementById("output");

    if (data && data.trim().length > 0) {
        transcription += " " + data.trim();
        output.innerText = transcription;

        // ❌ Ya no es necesario enviar al backend, el análisis se hace allá
        // socket.emit("transcription", data.trim());
    }
});

// 🎭 Mostrar la emoción detectada por el backend
socket.on("emotion", (data) => {
    const emotionDiv = document.getElementById("emotionOutput");
    emotionDiv.innerText = `🧠 ${data.emotion.toUpperCase()}`;
});

// 🔑 Acumular y mostrar palabras clave sin duplicados
socket.on("keywords", (data) => {
    const keywordsDiv = document.getElementById("keywordsOutput");

    if (data && data.keywords && keywordsDiv) {
        data.keywords.forEach((word) => {
            if (!allKeywords.includes(word)) {
                allKeywords.push(word);
            }
        });

        keywordsDiv.innerText = allKeywords.join(", ");
    }
});

// 📢 Mostrar sugerencia generada por GPT-4
socket.on("suggestion", (data) => {
    const suggestionDiv = document.getElementById("suggestionOutput");

    if (data && data.text && suggestionDiv) {
        suggestionDiv.innerText = data.text;
    }
});
