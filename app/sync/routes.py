from flask import request, redirect, render_template, Blueprint, jsonify
import os
from dotenv import load_dotenv
import requests

load_dotenv()

sync_bp = Blueprint('sync_bp',__name__)
API_KEY = os.getenv('API_KEY')
SHEET_ID = os.getenv('SHEET_ID')
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Sheet1?alt=json&key={API_KEY}"

def fetch_sheet_data():
    response = requests.get(url)
    data = response.json()

    if "values" in data:
        headers = data["values"][0]
        records = [dict(zip(headers, row)) for row in data["values"][1:]]
    return records

@sync_bp.route('/', methods=['GET'])
def index():
    return render_template('Index.html')

@sync_bp.route("/api/sheet")
def api_sheet():
    return jsonify(fetch_sheet_data())





        

