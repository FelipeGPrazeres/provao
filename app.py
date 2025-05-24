# filepath: /c:/Users/Felip/Downloads/testes/2/provao/app.py
from flask import Flask, jsonify, request
import json
import threading
import time
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "https://provao-1.onrender.com",                 # Old frontend origin (keep if needed)
    "https://lightskyblue-grouse-667245.hostingersite.com",  # **ADD NEW FRONTEND ORIGIN HERE**
    "null" # Permitir origem 'null' para testes locais com file://
])
# ^ Allows cross-origin requests from the specified frontend

JSON_FILE_PATH = 'output_multi_sheet.json'

def keep_alive_loop():
    while True:
        try:
            requests.get('https://provao.onrender.com/keep_alive')
            requests.get('https://provao.onrender.com/ping_categories')
        except Exception as e:
            print("Error in keep_alive_loop:", e)
        time.sleep(120)

def load_data():
    """
    Loads the JSON data from a file and returns a dictionary
    representing categories and their items.
    """
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
    """
    Returns the list of available categories
    (keys of the data_categories dictionary).
    """
    return jsonify(list(data_categories.keys()))

@app.route('/courses')
def get_courses():
    """
    Expects a 'category' query parameter. If valid, returns
    the set of 'Curso' values for that category in the JSON data.
    """
    category = request.args.get('category')
    if not category or category not in data_categories:
        # 400 if category not provided or invalid
        return jsonify([]), 400

    category_data = data_categories[category]
    courses = {item.get('Curso', '') for item in category_data}
    # Collects unique course names in a set
    return jsonify(list(courses))

@app.route('/institutions')
def get_institutions():
    """
    Similar to /courses, but fetches 'Instituição' values
    for a valid category.
    """
    category = request.args.get('category')
    if not category or category not in data_categories:
        return jsonify([]), 400

    category_data = data_categories[category]
    institutions = {item.get('Instituição', '') for item in category_data}
    return jsonify(list(institutions))

@app.route('/filter_course', methods=['POST'])
def filter_course():
    """
    Accepts JSON with 'course', 'institution', and 'category'.
    Filters the dataset by 'Curso' and optionally by 'Instituição'.
    Returns list of matching data objects.
    """
    selected_course = request.json.get('course')
    selected_institution = request.json.get('institution')
    category = request.json.get('category')

    if not selected_course or not category or category not in data_categories:
        return jsonify({"error": "Curso ou categoria não fornecidos ou inválidos"}), 400

    category_data = data_categories[category]
    filtered_data = [
        item for item in category_data
        if selected_course.lower() in item.get('Curso', '').lower()
    ]

    # Apply institution filter only if provided
    if selected_institution:
        filtered_data = [
            item for item in filtered_data
            if selected_institution.lower() in item.get('Instituição', '').lower()
        ]

    return jsonify(filtered_data)

@app.route('/keep_alive')
def keep_alive():
    """
    Simple route to keep the server alive.
    Returns a JSON response with a success status.
    """
    return jsonify({"status": "Server is alive"})

@app.route('/ping_categories')  # New ping endpoint - try pinging /categories route
def ping_categories():
    """Pings the /categories endpoint as a form of activity."""
    categories = get_categories() # Actually call the /categories route logic
    return categories # Return the categories JSON response (same as /categories)

if __name__ == '__main__':
    # Runs the Flask app locally on port 5001
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    threading.Thread(target=keep_alive_loop, daemon=True).start()
    print("Started keep_alive_loop in the background.")
    app.run(debug=True, port=10000)