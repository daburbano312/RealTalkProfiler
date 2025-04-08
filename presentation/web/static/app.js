const socket = io();

const btnStart = document.getElementById('btnStart');
const btnStop = document.getElementById('btnStop');
const frequencyAnimation = document.getElementById('frequencyAnimation'); // Contenedor de la animación

let transcription = "";
let allKeywords = []; // 🔑 Acumulador global de keywords

// Enviar evento para iniciar grabación
btnStart.addEventListener('click', () => {
    socket.emit('start_recording');
    // Mostrar la animación
    frequencyAnimation.style.visibility = 'visible';
    // Cambiar el estado de los botones
    btnStart.disabled = true;
    btnStop.disabled = false;
});
  
// Enviar evento para detener grabación
btnStop.addEventListener('click', () => {
    socket.emit('stop_recording');
    // Ocultar la animación
    frequencyAnimation.style.visibility = 'hidden';
    // Cambiar el estado de los botones
    btnStart.disabled = false;
    btnStop.disabled = true;
});
  
// Actualizar el estado de la aplicación
socket.on("status", function(data) {
    document.getElementById("status").innerText = data.message;
});

// Actualizar la transcripción
socket.on("transcription", (data) => {
    const output = document.getElementById("output");

    if (data && data.trim().length > 0) {
        transcription += " " + data.trim();
        output.innerText = transcription;
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

// Cambiar la vista cuando se haga clic en "Proyectos"
document.getElementById('projectsLink').addEventListener('click', function() {
    window.location.href = '/proyectos'; // Redirige a la página de proyectos
    updateActiveLink('projectsLink'); // Actualiza el enlace activo
});

// Cambiar la vista cuando se haga clic en "Dashboard"
document.getElementById('dashboardLink').addEventListener('click', function() {
    window.location.href = '/'; // Redirige a la página principal del Dashboard
    updateActiveLink('dashboardLink'); // Actualiza el enlace activo
});

// Función para actualizar el enlace activo en la barra lateral
function updateActiveLink(activeLinkId) {
    const links = document.querySelectorAll('.menu-item');
    links.forEach(link => link.classList.remove('active')); // Elimina 'active' de todos los enlaces
    const activeLink = document.getElementById(activeLinkId);
    activeLink.classList.add('active'); // Añade 'active' al enlace seleccionado
}
