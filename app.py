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

def normalize_string(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    # s = unidecode(s) # Opcional: remover acentos (requer pip install unidecode)
    
    abbreviations = {
        "eng": "engenharia",
        "comp": "computacao",
        "adm": "administracao",
        "sao": "são",
        "info": "informacao",
        # Adicione mais mapeamentos conforme necessário
    }
    words = s.split()
    # Normaliza palavras inteiras e também verifica se partes de palavras são abreviações (ex: "eng.eletrica")
    # Esta parte pode ser mais complexa dependendo da necessidade.
    # Por simplicidade, vamos manter o split por espaço e normalizar palavras inteiras.
    normalized_words = [abbreviations.get(word.replace('.','').replace(',',''), word) for word in words]
    return " ".join(normalized_words)

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/formulario')
def formulario_page():
    return render_template('formulario.html')

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
    if not category or category not in json_data_for_suggestions:
        return jsonify([]), 400
        
    category_data = json_data_for_suggestions[category]
    courses = sorted(list(set(item.get('Curso', '') for item in category_data if item.get('Curso'))))
    return jsonify(courses)

# --- Rota para BUSCAR dados do SUPABASE ---
@app.route('/search_supabase', methods=['POST'])
def search_supabase():
    try:
        data = request.get_json()
        app.logger.info(f"Payload recebido em /search_supabase: {data}")

        selected_category = data.get('category')
        raw_institution = data.get('institution')
        raw_course = data.get('course')

        # Normalizar os termos de busca
        normalized_institution = normalize_string(raw_institution) if raw_institution else ""
        normalized_course = normalize_string(raw_course) if raw_course else ""

        app.logger.info(f"Filtrando com: Categoria='{selected_category}', Instituição (norm)='{normalized_institution}', Curso (norm)='{normalized_course}'")

        if not selected_category:
            app.logger.warning("Busca abortada: Categoria (tipo_cota) não fornecida.")
            return jsonify({"error": "Categoria (tipo_cota) é obrigatória."}), 400
        
        # Modificado: não exigir curso ou instituição, a busca pode ser só por categoria
        # if not normalized_course and not normalized_institution:
        #     app.logger.warning("Busca abortada: Nem curso nem instituição fornecidos após normalização.")
        #     return jsonify({"error": "Pelo menos um curso ou instituição deve ser especificado."}), 400

        query = supabase_client.table("dados_formulario").select("instituicao, curso, numero_unico, tipo_cota", count='exact')
        
        query = query.ilike("tipo_cota", f"{selected_category}%")
        app.logger.info(f"Filtro tipo_cota aplicado: ilike \"tipo_cota\", \"{selected_category}%\"")

        # Filtro de Curso
        if normalized_course:
            course_keywords_from_input = normalized_course.split(' ')
            app.logger.info(f"Processando keywords de CURSO normalizadas: {course_keywords_from_input}")
            for keyword_expanded in course_keywords_from_input:
                keyword_expanded = keyword_expanded.strip()
                if not keyword_expanded:
                    continue

                search_forms = {keyword_expanded} 
                for abbr, expanded_value_in_dict in abbreviations.items():
                    if expanded_value_in_dict == keyword_expanded:
                        search_forms.add(abbr)
                
                app.logger.info(f"Para keyword de curso '{keyword_expanded}', formas de busca são: {search_forms}")

                if len(search_forms) > 1:
                    or_filter_parts = [f'curso.ilike.*{form}*' for form in search_forms]
                    query = query.or_(",".join(or_filter_parts))
                    app.logger.info(f"Aplicado filtro OR para curso com '{keyword_expanded}': {','.join(or_filter_parts)}")
                elif search_forms: 
                    single_form = list(search_forms)[0]
                    query = query.ilike("curso", f"%{single_form}%")
                    app.logger.info(f"Aplicado filtro ILIKE para curso com '{single_form}'")

        # Filtro de Instituição (lógica similar ao curso)
        if normalized_institution:
            institution_keywords_from_input = normalized_institution.split(' ')
            app.logger.info(f"Processando keywords de INSTITUIÇÃO normalizadas: {institution_keywords_from_input}")
            for keyword_expanded in institution_keywords_from_input:
                keyword_expanded = keyword_expanded.strip()
                if not keyword_expanded:
                    continue

                search_forms = {keyword_expanded}
                for abbr, expanded_value_in_dict in abbreviations.items():
                    if expanded_value_in_dict == keyword_expanded:
                        search_forms.add(abbr)
                
                app.logger.info(f"Para keyword de instituição '{keyword_expanded}', formas de busca são: {search_forms}")

                if len(search_forms) > 1:
                    or_filter_parts = [f'instituicao.ilike.*{form}*' for form in search_forms]
                    query = query.or_(",".join(or_filter_parts))
                    app.logger.info(f"Aplicado filtro OR para instituição com '{keyword_expanded}': {','.join(or_filter_parts)}")
                elif search_forms:
                    single_form = list(search_forms)[0]
                    query = query.ilike("instituicao", f"%{single_form}%")
                    app.logger.info(f"Aplicado filtro ILIKE para instituição com '{single_form}'")
        
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
    app.run(debug=True, host='0.0.0.0', port=10000)