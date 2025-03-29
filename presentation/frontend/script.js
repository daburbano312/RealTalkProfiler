async function processAudio() {
    document.getElementById('results').style.display = 'none';
  
    const res = await fetch("http://localhost:5000/api/process_audio", {
      method: "POST"
    });
  
    if (!res.ok) {
      alert("Error al procesar el audio. ¿El backend está corriendo?");
      return;
    }
  
    const data = await res.json();
    document.getElementById("text").innerText = data.transcription;
    document.getElementById("audio_emotion").innerText = data.audio_emotion;
    document.getElementById("text_emotion").innerText = data.text_emotion;
  
    const suggestionsDiv = document.getElementById("suggestions");
    suggestionsDiv.innerHTML = "";
    data.suggestions.forEach(s => {
      const el = document.createElement("div");
      el.className = "suggestion";
      el.innerText = s;
      suggestionsDiv.appendChild(el);
    });
  
    document.getElementById('results').style.display = 'block';
  }
  