from flask import Flask, jsonify, request
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://provao-1.onrender.com"]) # **SPECIFIC ORIGIN - REPLACE WITH YOUR FRONTEND URL**

JSON_FILE_PATH = 'output_multi_sheet.json'

def load_data():
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading JSON file '{JSON_FILE_PATH}': {e}")
        return {}

data_categories = load_data()

@app.route('/categories')
def get_categories():
    return jsonify(list(data_categories.keys()))

@app.route('/courses')
def get_courses():
    category = request.args.get('category')
    if not category or category not in data_categories:
        return jsonify([]), 400

    category_data = data_categories[category]
    courses = set()
    for item in category_data:
        courses.add(item.get('Curso', ''))
    return jsonify(list(courses))

@app.route('/institutions')
def get_institutions():
    category = request.args.get('category')
    if not category or category not in data_categories:
        return jsonify([]), 400

    category_data = data_categories[category]
    institutions = set()
    for item in category_data:
        institutions.add(item.get('Instituição', ''))
    return jsonify(list(institutions))


@app.route('/filter_course', methods=['POST'])
def filter_course():
    selected_course = request.json.get('course')
    selected_institution = request.json.get('institution') # Get institution from request
    category = request.json.get('category')

    if not selected_course or not category or category not in data_categories:
        return jsonify({"error": "Curso ou categoria não fornecidos ou inválidos"}), 400

    category_data = data_categories[category]
    filtered_data = category_data
    if selected_course:
        filtered_data = [
            item for item in filtered_data
            if selected_course.lower() in item.get('Curso', '').lower()
        ]
    if selected_institution: # Apply institution filter if provided
        filtered_data = [
            item for item in filtered_data
            if selected_institution.lower() in item.get('Instituição', '').lower()  
        ]

    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
