import json
from urllib.parse import urlparse, parse_qs

JSON_FILE_PATH = 'output_multi_sheet.json'

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

def get_courses_data(category):
    if not category or category not in data_categories:
        return []
    category_data = data_categories[category]
    courses = set()
    for item in category_data:
        courses.add(item.get('Curso', ''))
    return list(courses)


def handler(req, res):
    parsed_url = urlparse(req.url) # Use req.url to get URL from Vercel request
    query_params = parse_qs(parsed_url.query)
    category = query_params.get('category', [''])[0]
    courses = get_courses_data(category)
    res.status(200).json(courses)