import whisper
import tempfile
import os

class Translator:
  _instance = None
  _model = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(Translator, cls).__new__(cls)
      print("Carregando modelo ..")
      cls._model = whisper.load_model("turbo")
    return cls._instance

  def translate(self, audio_stream, file_name):
    result = ""
    if not self._model:
      return "Modelo não carregado", result
    
    temp_filepath = None

    try: 
      file_extension = f".{file_name.rsplit('.', 1)[1]}"

      print("Criando arquivo temporário ...\n")
      with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_audio_file:
        temp_filepath = temp_audio_file.name
        temp_audio_file.write(audio_stream.read())

      test = "audios/aniversario_larissa.mp3"

      print("\nTranscrevendo áudio ...\n")
      result = self._model.transcribe(temp_filepath, fp16=False)
      result = result["text"] if result["text"] else ""
      return None, result
    except Exception as e: 
      return str(e), result
    finally:
      if temp_filepath and os.path.exists(temp_filepath):
        print(f"Removendo arquivo temporário: {temp_filepath}")
        os.remove(temp_filepath)

translator_service = Translator()