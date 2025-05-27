import json

INPUT_JSON_PATH = 'output_multi_sheet.json'
OUTPUT_SUGGESTIONS_PATH = 'suggestions_data.json'

def generate_suggestions():
    all_institutions = set()
    all_courses = set()

    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{INPUT_JSON_PATH}' não encontrado.")
        return
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar JSON do arquivo '{INPUT_JSON_PATH}'.")
        return

    if not isinstance(data, dict):
        print(f"Erro: O conteúdo de '{INPUT_JSON_PATH}' não é um dicionário como esperado.")
        return

    for category_data in data.values():
        if isinstance(category_data, list):
            for item in category_data:
                if isinstance(item, dict):
                    institution = item.get('Instituição')
                    course = item.get('Curso')
                    if institution:
                        all_institutions.add(institution.strip())
                    if course:
                        all_courses.add(course.strip())
    
    suggestions = {
        "institutions": sorted(list(all_institutions)),
        "courses": sorted(list(all_courses))
    }

    try:
        with open(OUTPUT_SUGGESTIONS_PATH, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=4)
        print(f"Arquivo de sugestões '{OUTPUT_SUGGESTIONS_PATH}' gerado com sucesso!")
        print(f"Total de instituições únicas: {len(suggestions['institutions'])}")
        print(f"Total de cursos únicos: {len(suggestions['courses'])}")
    except IOError:
        print(f"Erro: Não foi possível escrever o arquivo '{OUTPUT_SUGGESTIONS_PATH}'.")

if __name__ == '__main__':
    generate_suggestions() 