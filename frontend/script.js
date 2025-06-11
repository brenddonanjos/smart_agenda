const recordButton = document.getElementById("recordButton");
const stopButton = document.getElementById("stopButton");
const sendButton = document.getElementById("sendButton");
const audioPlayback = document.getElementById("audioPlayback");
const outputDiv = document.getElementById("output");

let audioBlob;
let mediaRecorder;

const recordAudio = async() => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    let chunks = [];

    mediaRecorder.ondataavailable = (event) => {
      chunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      audioBlob = new Blob(chunks, { type: "audio/wav" });              
      const audioUrl = URL.createObjectURL(audioBlob);
      audioPlayback.src = audioUrl;

      chunks = [];
      sendButton.disabled = false;
    };

    mediaRecorder.start();
    
    recordButton.disabled = true;
    recordButton.classList.add("recording");
    stopButton.disabled = false;
    sendButton.disabled = true;
    outputDiv.innerHTML = "<p>🎤 Gravando... Fale agora.</p>";
  } catch (error) {
    console.error("Erro ao gravar áudio:", error);
  }
}

const stopRecording = () => {
  
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  
  recordButton.disabled = false;
  recordButton.classList.remove("recording");
  stopButton.disabled = true;
  outputDiv.innerHTML = "<p>✅ Gravação concluída. Ouça acima e envie se estiver correto.</p>";
}

const sendAudio = async () => {
  if (!audioBlob) {
    alert("Nenhum áudio foi gravado ainda.");
    return;
  }
  sendButton.disabled = true;
  sendButton.innerText = "Enviando e Processando...";
  outputDiv.innerHTML = "<p>⏳ Enviando áudio e gerando JSON, aguarde...</p>";

  const formData = new FormData();
  formData.append("audio_file", audioBlob, "recording.wav");

  try {
    const response = await fetch("http://localhost:5000/journal", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Erro ${response.status}`);
    }

    const data = await response.json();
    outputDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;

  } catch (error) {
    console.error("Erro ao enviar o áudio:", error);
    outputDiv.innerHTML = `<p>❌ Erro ao processar: ${error.message}</p>`;
  } finally {
    sendButton.disabled = false;
    sendButton.innerText = "Enviar Áudio";
  }
}

document.addEventListener("DOMContentLoaded", () => {

  recordButton.addEventListener("click", recordAudio);
  stopButton.addEventListener("click", stopRecording);
  sendButton.addEventListener("click", sendAudio);
});
