from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
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

def get_categories_data():
    return list(data_categories.keys())

def get_courses_data(category):
    if not category or category not in data_categories:
        return []
    category_data = data_categories[category]
    courses = set()
    for item in category_data:
        courses.add(item.get('Curso', ''))
    return list(courses)

def get_institutions_data(category):
    if not category or category not in data_categories:
        return []
    category_data = data_categories[category]
    institutions = set()
    for item in category_data:
        institutions.add(item.get('Instituição', ''))
    return list(institutions)

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

class handler(BaseHTTPRequestHandler):

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # For CORS
        self.end_headers()
        json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.wfile.write(json_bytes)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Allow', 'GET, POST, OPTIONS')
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == '/categories':
            categories = get_categories_data()
            self.send_json_response(categories)
        elif path == '/courses':
            category = query_params.get('category', [''])[0]
            courses = get_courses_data(category)
            self.send_json_response(courses)
        elif path == '/institutions':
            category = query_params.get('category', [''])[0]
            institutions = get_institutions_data(category)
            self.send_json_response(institutions)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*') # For CORS
            self.end_headers()
            self.wfile.write(b'Not Found')
        return

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/filter_course':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                category = request_data.get('category')
                course = request_data.get('course')
                institution = request_data.get('institution')
                filtered_data = filter_course_data(category, course, institution)
                self.send_json_response(filtered_data)
            except json.JSONDecodeError:
                self.send_json_response({"error": "Invalid JSON"}, 400)
            except Exception as e:
                print(f"Error processing POST request: {e}")
                self.send_json_response({"error": "Server error"}, 500)

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*') # For CORS
            self.end_headers()
            self.wfile.write(b'Not Found')
        return

def run_server(server_class=HTTPServer, handler_class=handler, port=5001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run_server()