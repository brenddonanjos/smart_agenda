from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from src.journal.crew import journa_service
from src.translator.main import translator_service
import logging
import json
import re

app = Flask("journal")
CORS(app)

ALLOWED_EXTENSIONS = {'flac', 'mp3', 'wav'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_audio_file(file):
    if not file.filename.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
        return False, "Tipo de arquivo não suportado"
    
    if len(file.read()) > 50 * 1024 * 1024:
        return False, "Arquivo muito grande"

    if file.filename == '':
        return False, "Nenhum arquivo selecionado"
    
    allowed_extension = False
    for extension in ALLOWED_EXTENSIONS:
        if file.filename.lower().endswith(extension):
            allowed_extension = True
            break    
    if not allowed_extension:
        return False, "Tipo de arquivo não suportado"
    
    file.seek(0)
    return True, None

def clean_json_string(json_string):
    """Limpa e corrige JSON malformado retornado pelos agentes"""
    json_pattern = r'\{.*?\}'
    match = re.search(json_pattern, json_string, re.DOTALL)
    if match:
        json_string = match.group(0)
    
    json_string = json_string.strip()    
    json_string = json_string.replace("'", '"')    
    json_string = ''.join(char for char in json_string if ord(char) >= 32 or char in '\n\r\t')
    
    return json_string

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/journal", methods=["POST"])
def research_topic():
    if 'audio_file' not in request.files:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400
    
    file = request.files['audio_file']
    is_valid, error = validate_audio_file(file)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    try:
        print("Traduzindo audio ..")
        error, result_text = translator_service.translate(audio_stream=file.stream, file_name=file.filename)
        if error:
            return jsonify({"error": f"Falha ao transcrever áudio: {error}"}), 500
        
        logger.info(f"Processando arquivo: {file.filename}")
        logger.info(f"Texto transcrito: {result_text[:100]}...")
        
        print("Enviado ao Crew")
        crew_result = journa_service.crew().kickoff(inputs={ "phrase": result_text })

        # Debug: imprimir todos os resultados
        logger.info(f"Número de tasks executadas: {len(crew_result.tasks_output)}")
        for i, task_output in enumerate(crew_result.tasks_output):
            logger.info(f"Task {i} resultado: {repr(task_output.raw)}")

        # Verificar se é um aniversário
        identifier_result = crew_result.tasks_output[0].raw.strip()
        if identifier_result == "0":
            return jsonify({
                "identified": False,
                "message": "Não foi identificado como solicitação de aniversário"
            }), 200
        
        # Extrair informações do aniversário
        if len(crew_result.tasks_output) < 2:
            return jsonify({"error": "Tarefa de extração não foi executada"}), 500
            
        birthday_extractor_result = crew_result.tasks_output[1].raw.strip()        
        if not birthday_extractor_result:
            return jsonify({"error": "Não foi possível extrair as informações do aniversário"}), 500
        
        # Tentar fazer parse do JSON
        try:
            cleaned_json = clean_json_string(birthday_extractor_result)
            json_result = json.loads(cleaned_json)
        except json.JSONDecodeError as json_error:
            logger.error(f"Erro no parse do JSON: {json_error}")
            return jsonify({
                "error": "JSON retornado pelo agente está malformado",
                "raw_response": birthday_extractor_result,
                "json_error": str(json_error)
            }), 500
        
        # Obter sugestões de presente
        gift_suggestion_result = ""
        if len(crew_result.tasks_output) >= 3:
            gift_suggestion_result = crew_result.tasks_output[2].raw.strip()
            gift_suggestion_result = gift_suggestion_result.split("\n")
            json_result["gift_suggestions"] = gift_suggestion_result
        
        json_result["original_text"] = result_text        
        return jsonify({
            "identified": True,
            "response": json_result
        }), 200

    except Exception as e:
        logger.error(f"Erro geral: {str(e)}", exc_info=True)
        return jsonify({"error": f"Falha ao processar áudio: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)