document.getElementById("startBtn").addEventListener("click", async () => {
    document.getElementById("results").style.display = "none";
    document.getElementById("text").innerText = "Procesando...";
    document.getElementById("audio_emotion").innerText = "-";
    document.getElementById("text_emotion").innerText = "-";
    document.getElementById("suggestions").innerHTML = "";
  
    try {
      const res = await fetch("http://localhost:5000/api/process_audio", {
        method: "POST"
      });
  
      if (!res.ok) {
        alert("⚠️ Error al procesar audio. ¿Backend encendido?");
        return;
      }
  
      const data = await res.json();
  
      document.getElementById("text").innerText = data.transcription || "-";
      document.getElementById("audio_emotion").innerText = data.audio_emotion || "-";
      document.getElementById("text_emotion").innerText = data.text_emotion || "-";
  
      const suggestionsDiv = document.getElementById("suggestions");
      data.suggestions.forEach((s) => {
        const div = document.createElement("div");
        div.className = "suggestion";
        div.innerText = "💡 " + s;
        suggestionsDiv.appendChild(div);
      });
  
      document.getElementById("results").style.display = "block";
    } catch (err) {
      console.error("Error:", err);
      alert("❌ Error al conectar con el backend.");
    }
  });
  