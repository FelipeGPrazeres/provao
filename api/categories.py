import json

JSON_FILE_PATH = 'output_multi_sheet.json'  # Relative path to JSON, assuming it's in the project root

def load_data():
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found: {JSON_FILE_PATH}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error: JSON decode error in {JSON_FILE_PATH}: {e}")
        return {}

data_categories = load_data()

def get_categories_data():
    return list(data_categories.keys())

def handler(req, res):
    categories = get_categories_data()
    res.status(200).json(categories)