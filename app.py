# filepath: /c:/Users/Felip/Downloads/testes/2/provao/app.py
from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    "https://provao.onrender.com",
    "https://lightskyblue-grouse-667245.hostingersite.com",
    "null"
])

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/formulario')
def formulario_page():
    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)