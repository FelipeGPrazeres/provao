import json

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

def filter_course_data(category, course=None, institution=None):
    if not category or category not in data_categories:
        return []
    category_data = data_categories[category]
    filtered_data = category_data
    if course:
        filtered_data = [
            item for item in filtered_data
            if item.get('Curso', '').lower() == course.lower()
        ]
    if institution:
        filtered_data = [
            item for item in filtered_data
            if item.get('Instituição', '').lower() == institution.lower()
        ]
    return filtered_data


def handler(req, res):
    try:
        request_data = req.body # Vercel request body is already parsed JSON
        category = request_data.get('category')
        course = request_data.get('course')
        institution = request_data.get('institution')
        filtered_data = filter_course_data(category, course, institution)
        res.status(200).json(filtered_data)
    except Exception as e:
        print(f"Error processing POST request: {e}")
        res.status(500).json({"error": "Server error"})