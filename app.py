# filepath: /c:/Users/Felip/Downloads/testes/2/provao/app.py
from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS
import json
import os # Para variáveis de ambiente
from supabase import create_client, Client # Importações do Supabase
# from unidecode import unidecode # Descomente se for usar para remover acentos

app = Flask(__name__)
CORS(app, origins=[
    "https://provao.onrender.com",
    "https://lightskyblue-grouse-667245.hostingersite.com",
    "null"
])

# Carregamento do JSON para sugestões
JSON_FILE_PATH = 'output_multi_sheet.json'
def load_json_data():
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Arquivo JSON {JSON_FILE_PATH} não encontrado.")
        return {}
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON {JSON_FILE_PATH}: {e}")
        return {}

json_data_for_suggestions = load_json_data()

# Carregar dados para autocomplete de instituição e curso
SUGGESTIONS_JSON_PATH = 'suggestions_data.json'
suggestions_data = {}
if os.path.exists(SUGGESTIONS_JSON_PATH):
    try:
        with open(SUGGESTIONS_JSON_PATH, 'r', encoding='utf-8') as f:
            suggestions_data = json.load(f)
        print(f"Arquivo de sugestões '{SUGGESTIONS_JSON_PATH}' carregado com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar o arquivo de sugestões '{SUGGESTIONS_JSON_PATH}': {e}")
else:
    print(f"AVISO: Arquivo de sugestões '{SUGGESTIONS_JSON_PATH}' não encontrado. Os campos de autocomplete podem não funcionar como esperado.")

# Configuração do Cliente Supabase Python
# É RECOMENDADO usar variáveis de ambiente para SUPABASE_URL e SUPABASE_KEY em produção
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "https://iradczvlimgyukwbwqcl.supabase.co")
SUPABASE_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlyYWRjenZsaW1neXVrd2J3cWNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMTQwMDcsImV4cCI6MjA2MzY5MDAwN30.CcLvcjhUaNvgSEHFunka_Er-RQ8iwMKInP5lvIrlqIY")
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(f"Supabase URL: {SUPABASE_URL}")
if SUPABASE_URL == "https://iradczvlimgyukwbwqcl.supabase.co" and "SUA_URL_SUPABASE" not in os.environ.get("SUPABASE_URL", "") :
    print("INFO: Usando URL Supabase do fallback no código.")
if SUPABASE_KEY == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlyYWRjenZsaW1neXVrd2J3cWNsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMTQwMDcsImV4cCI6MjA2MzY5MDAwN30.CcLvcjhUaNvgSEHFunka_Er-RQ8iwMKInP5lvIrlqIY" and "SUA_CHAVE_ANON_SUPABASE" not in os.environ.get("SUPABASE_ANON_KEY", ""):
    print("INFO: Usando chave Supabase do fallback no código.")

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/formulario')
def formulario_page():
    return render_template('formulario.html')

@app.route('/links')
def links_page():
    return render_template('links.html')

# --- Rotas para fornecer dados do JSON para SUGESTÕES ---
@app.route('/get_json_categories')
def get_json_categories():
    return jsonify(list(json_data_for_suggestions.keys()))

@app.route('/get_json_institutions')
def get_json_institutions():
    category = request.args.get('category')
    if not category or category not in json_data_for_suggestions:
        return jsonify([]), 400
    
    category_data = json_data_for_suggestions[category]
    institutions = sorted(list(set(item.get('Instituição', '') for item in category_data if item.get('Instituição'))))
    return jsonify(institutions)

@app.route('/get_json_courses')
def get_json_courses():
    category = request.args.get('category')
    # Se precisar de todos os cursos para autocomplete, ignorar categoria
    # if request.args.get('all') == 'true':
    #     return jsonify(suggestions_data.get('courses', []))

    if not category or category not in json_data_for_suggestions:
        return jsonify([]), 400
        
    category_data = json_data_for_suggestions[category]
    courses = sorted(list(set(item.get('Curso', '') for item in category_data if item.get('Curso'))))
    return jsonify(courses)

# --- Novas rotas para autocomplete global ---
@app.route('/get_all_institutions')
def get_all_institutions():
    return jsonify(suggestions_data.get('institutions', []))

@app.route('/get_all_courses')
def get_all_courses():
    return jsonify(suggestions_data.get('courses', []))

# --- Rota para BUSCAR dados do SUPABASE ---
@app.route('/search_supabase', methods=['POST'])
def search_supabase():
    try:
        data = request.get_json()
        app.logger.info(f"Payload recebido em /search_supabase: {data}")

        selected_category = data.get('category')
        selected_institution = data.get('institution') # Valor direto do datalist
        selected_course = data.get('course')           # Valor direto do datalist

        app.logger.info(f"Filtrando com: Categoria='{selected_category}', Instituição='{selected_institution}', Curso='{selected_course}'")

        if not selected_category:
            app.logger.warning("Busca abortada: Categoria (tipo_cota) não fornecida.")
            return jsonify({"error": "Categoria (tipo_cota) é obrigatória."}), 400
        
        query = supabase_client.table("dados_formulario").select("instituicao, curso, numero_unico, tipo_cota", count='exact')
        
        query = query.ilike("tipo_cota", f"{selected_category}%")
        app.logger.info(f"Filtro tipo_cota aplicado: ilike \"tipo_cota\", \"{selected_category}%\"")

        if selected_course:
            query = query.ilike("curso", f"%{selected_course.strip()}%")
            app.logger.info(f"Filtro de curso aplicado: ilike \"curso\", \"%{selected_course.strip()}%\"")

        if selected_institution:
            query = query.ilike("instituicao", f"%{selected_institution.strip()}%")
            app.logger.info(f"Filtro de instituição aplicado: ilike \"instituicao\", \"%{selected_institution.strip()}%\"")
        
        # Ordena os resultados pela coluna 'numero_unico' em ordem decrescente
        # Removido nulls_last=True para teste
        query = query.order("numero_unico", desc=True)

        response = query.execute()
        app.logger.info(f"Resposta da query Supabase: count={response.count}, data={response.data}")

        if hasattr(response, 'data'):
            return jsonify(response.data)
        else:
            app.logger.error(f"Erro estrutural na resposta do Supabase: {response}")
            return jsonify({"error": "Erro ao buscar dados no Supabase", "details": str(response)}), 500

    except Exception as e:
        app.logger.error(f"Exceção na rota /search_supabase: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor", "details": str(e)}), 500

if __name__ == '__main__':
    # Para desenvolvimento, você pode criar um arquivo .env com:
    # SUPABASE_URL=sua_url_real
    # SUPABASE_ANON_KEY=sua_chave_anon_real
    # from dotenv import load_dotenv
    # load_dotenv() # Descomente se for usar python-dotenv localmente

    # As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY devem ser configuradas 
    # no seu ambiente de produção (ex: Render, Heroku).
    # Define a porta a partir da variável de ambiente PORT, com fallback para 10000
    port = int(os.environ.get("PORT", 10000))
    # O host '0.0.0.0' permite acesso externo (necessário para a nuvem) e local.
    app.run(debug=True, host='0.0.0.0', port=port)