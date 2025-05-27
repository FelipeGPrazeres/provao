import json
import csv

def convert_json_to_csv(json_file_path, csv_file_path):
    """
    Converts specific fields from a JSON file to a CSV file.
    The JSON file is expected to be a dictionary where each value is a list of records.
    All records from all lists will be aggregated into a single CSV.

    Args:
        json_file_path (str): The path to the input JSON file.
        csv_file_path (str): The path to the output CSV file.
    """
    fields_to_extract = ['tipo_cota', 'Instituição', 'Curso', 'Grupo', 'Nota']
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data_by_sheet = json.load(json_file) # Carrega o dicionário principal

        if not isinstance(data_by_sheet, dict):
            print(f"Erro: O conteúdo do arquivo JSON ({json_file_path}) não é um dicionário como esperado.")
            return

        all_records = []
        for sheet_name, records_in_sheet in data_by_sheet.items():
            if isinstance(records_in_sheet, list):
                all_records.extend(records_in_sheet)
                print(f"Encontrados {len(records_in_sheet)} registros na planilha: {sheet_name}")
            else:
                print(f"Aviso: O valor para a chave '{sheet_name}' não é uma lista e será ignorado.")

        if not all_records:
            print("Erro: Nenhum registro encontrado nas listas dentro do JSON.")
            return

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields_to_extract, extrasaction='ignore')
            writer.writeheader()

            count = 0
            for sheet_name, records_in_sheet in data_by_sheet.items():
                if isinstance(records_in_sheet, list):
                    for record in records_in_sheet:
                        if isinstance(record, dict):
                            row_data = {field: record.get(field) for field in fields_to_extract if field != 'tipo_cota'}
                            row_data['tipo_cota'] = sheet_name
                            writer.writerow(row_data)
                            count += 1
                        else:
                            print(f"Aviso: Registro ignorado pois não é um dicionário: {record} na planilha {sheet_name}")
            
            print(f"\nConversão concluída! {count} registros totais processados de todas as planilhas.")
            print(f"Arquivo CSV salvo em: {csv_file_path}")

    except FileNotFoundError:
        print(f"Erro: Arquivo JSON não encontrado em '{json_file_path}'")
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o arquivo JSON em '{json_file_path}'. Verifique se é um JSON válido.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == '__main__':
    json_input_path = 'output_multi_sheet.json'
    csv_output_path = 'dados_convertidos_agregados.csv' # Novo nome para o CSV agregado

    convert_json_to_csv(json_input_path, csv_output_path) 