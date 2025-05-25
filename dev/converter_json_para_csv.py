import json
import csv
import io

# Marcadores para eu encontrar o conteúdo CSV na saída do script
CSV_OUTPUT_MARKER_START = "---CSV_CONTENT_START---"
CSV_OUTPUT_MARKER_END = "---CSV_CONTENT_END---"

# Cabeçalhos do CSV baseados em supabase.md
CSV_HEADERS = ['id', 'nome', 'tipo_cota', 'instituicao', 'curso', 'numero_unico']

# Nomes das chaves esperadas no JSON.
# !!! Se estas não forem as chaves corretas no seu output_multi_sheet.json, o script falhará ou produzirá um CSV incorreto !!!
JSON_NOME_KEY = "Nome Completo"     # Ex: "João da Silva"
JSON_INSTITUICAO_KEY = "Instituição" # Ex: "USP"
JSON_CURSO_KEY = "Curso"          # Ex: "Engenharia Civil"
JSON_NOTA_KEY = "Nota"            # Ex: 750.50 ou "750,50"

INPUT_JSON_FILE = 'output_multi_sheet.json'

def generate_csv_content_string():
    """
    Lê o arquivo JSON de entrada, converte para uma string CSV na memória.
    Retorna a string CSV ou None em caso de erro.
    """
    try:
        with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{INPUT_JSON_FILE}' não encontrado na raiz do projeto.")
        return None
    except json.JSONDecodeError:
        print(f"ERRO: Falha ao decodificar '{INPUT_JSON_FILE}'. Verifique se é um JSON válido.")
        return None
    except Exception as e:
        print(f"ERRO inesperado ao ler o JSON: {e}")
        return None

    output_string_io = io.StringIO()
    writer = csv.writer(output_string_io, quoting=csv.QUOTE_MINIMAL)
    
    # Escreve o cabeçalho
    writer.writerow(CSV_HEADERS)

    processed_items_count = 0
    # Itera sobre cada categoria (que é a chave principal do JSON, ex: "L1", "L2")
    for tipo_cota_from_json_key, items_in_category in json_data.items():
        if not isinstance(items_in_category, list):
            print(f"AVISO: O valor para a chave de categoria '{tipo_cota_from_json_key}' no JSON não é uma lista. Pulando esta categoria.")
            continue
            
        for item in items_in_category:
            if not isinstance(item, dict):
                print(f"AVISO: Um item dentro da categoria '{tipo_cota_from_json_key}' não é um dicionário válido. Pulando item: {item}")
                continue

            # Extrai dados do item JSON
            nome_val = item.get(JSON_NOME_KEY, "")
            instituicao_val = item.get(JSON_INSTITUICAO_KEY, "")
            curso_val = item.get(JSON_CURSO_KEY, "")
            
            # tipo_cota para o CSV vem da chave da categoria no JSON
            tipo_cota_val = tipo_cota_from_json_key 

            nota_json_val = item.get(JSON_NOTA_KEY)
            numero_unico_csv_val = "" # Valor padrão se a nota não puder ser processada

            if isinstance(nota_json_val, (int, float)):
                numero_unico_csv_val = float(nota_json_val)
            elif isinstance(nota_json_val, str) and nota_json_val.strip():
                try:
                    numero_unico_csv_val = float(nota_json_val.replace(',', '.').strip())
                except ValueError:
                    print(f"AVISO: Não foi possível converter a string de Nota '{nota_json_val}' para float. Item (Nome: '{nome_val}', Curso: '{curso_val}'). Nota será deixada em branco no CSV.")
            elif nota_json_val is not None: # Se não for None, nem número, nem string processável
                 print(f"AVISO: Valor de Nota inesperado '{nota_json_val}' (Tipo: {type(nota_json_val)}) para o item (Nome: '{nome_val}', Curso: '{curso_val}'). Nota será deixada em branco no CSV.")
            
            # Escreve a linha no CSV (id é deixado em branco)
            writer.writerow([
                "", # id
                nome_val,
                tipo_cota_val,
                instituicao_val,
                curso_val,
                numero_unico_csv_val
            ])
            processed_items_count += 1
    
    print(f"INFO: Processamento JSON concluído. {processed_items_count} linhas de dados prontas para o CSV (excluindo cabeçalho).")
    return output_string_io.getvalue()

# Parte principal da execução do script
print("INFO: Iniciando conversão de JSON para CSV...")
print(f"INFO: Usando o arquivo de entrada: '{INPUT_JSON_FILE}'")
print(f"INFO: Chaves JSON esperadas (ajuste no script se estas estiverem incorretas):")
print(f"  Nome: '{JSON_NOME_KEY}'")
print(f"  Instituição: '{JSON_INSTITUICAO_KEY}'")
print(f"  Curso: '{JSON_CURSO_KEY}'")
print(f"  Nota: '{JSON_NOTA_KEY}'")
print("-" * 30)

OUTPUT_CSV_FILE = 'dados_para_importar.csv' # Definir o nome do arquivo de saída

csv_data_string = generate_csv_content_string()

if csv_data_string:
    try:
        with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8') as f_out:
            f_out.write(csv_data_string)
        print(f"SUCESSO: Arquivo '{OUTPUT_CSV_FILE}' foi criado com o conteúdo CSV.")
        # Opcional: imprimir uma pequena amostra se desejar
        # print("Amostra do CSV (primeiras 5 linhas):")
        # lines = csv_data_string.splitlines()
        # for i in range(min(5, len(lines))):
        #     print(lines[i])
    except IOError:
        print(f"ERRO: Falha ao escrever o arquivo CSV '{OUTPUT_CSV_FILE}'. Verifique as permissões.")
    except Exception as e:
        print(f"ERRO inesperado ao salvar o arquivo CSV: {e}")
else:
    print("ERRO: Falha ao gerar o conteúdo CSV. O arquivo não foi criado. Verifique as mensagens de erro acima.")
