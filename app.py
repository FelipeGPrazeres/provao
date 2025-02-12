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
    print("filter_course function CALLED!") # **NEW DEBUG LOG - Function entry**
    selected_institution = request.json.get('institution') # Get institution from request
    category = request.json.get('category')

    if not category or category not in data_categories:
        return jsonify({"error": "Categoria não fornecida ou inválida"}), 400

    category_data = data_categories[category]
    filtered_data = category_data  # Start with all data for the category

    if selected_institution: # Apply institution filter if provided
        filtered_data = [] # Re-initialize filtered_data here to collect matches
        search_term_lower = selected_institution.lower() # Lowercase search term ONCE

        for item in category_data:
            institution_name = item.get('Instituição', '') # Get institution name
            institution_name_lower = institution_name.lower() # Lowercase institution name

            print(f"Comparing search term: '{search_term_lower}' with institution name: '{institution_name_lower}'") # **DEBUG LOGGING - COMPARE VALUES**

            if search_term_lower in institution_name_lower: # Substring check
                filtered_data.append(item) # Add matching item

    return jsonify(filtered_data) # Return jsonify of the (potentially filtered) data

if __name__ == '__main__':
    app.run(debug=True, port=5001)
