from flask import request, redirect, render_template, Blueprint, jsonify
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from sqlalchemy import text
from datetime import datetime
from app.models import EmployeeBasicInfo, EmployeeSalaryInfo, EmployeeContactInfo
from app.extensions import db

load_dotenv()

sync_bp = Blueprint('sync_bp',__name__)
API_KEY = os.getenv('API_KEY')
SHEET_ID = os.getenv('SHEET_ID')

def get_url(sheet):

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet}?alt=json&key={API_KEY}"
    return url

def fetch_sheet_data(sheet):
    
    url = get_url(sheet)
    response = requests.get(url)
    data = response.json()

    if "values" in data:
        headers = data["values"][0]
        records = [dict(zip(headers, row)) for row in data["values"][1:]]
    return records

@sync_bp.route('/', methods=['GET'])
def index():
    return render_template('Index.html')


@sync_bp.route('/sync-to-db')
def sync_to_db():

    sheet1_data = fetch_sheet_data('Sheet1')
    sheet2_data = fetch_sheet_data('Sheet2')
    sheet3_data = fetch_sheet_data('Sheet3')

    sheet2_map = {row['Employee_ID']: row for row in sheet2_data}
    sheet3_map = {row['Employee_ID']: row for row in sheet3_data}

    for row in sheet1_data:
        emp_id = row.get('Employee_ID')
        if not emp_id:
            continue

        # Basic Info
        basic = EmployeeBasicInfo.query.filter_by(employee_id=emp_id).first()
        if not basic:
            basic = EmployeeBasicInfo(
                employee_id=emp_id,
                first_name=row.get('First_Name'),
                date_of_joining=datetime.strptime(row.get('Date_of_Joining'), "%Y-%m-%d")
            )
            db.session.add(basic)

        # Salary Info
        if emp_id in sheet3_map and not EmployeeSalaryInfo.query.filter_by(employee_id=emp_id).first():
            salary_row = sheet3_map[emp_id]
            db.session.add(
                EmployeeSalaryInfo(
                    employee_id=emp_id,
                    salary=int(salary_row.get('Salary', 0)),
                    pay_grade=salary_row.get('Pay_Grade')
                )
            )

        # Contact Info
        if emp_id in sheet2_map and not EmployeeContactInfo.query.filter_by(employee_id=emp_id).first():
            contact_row = sheet2_map[emp_id]
            db.session.add(
                EmployeeContactInfo(
                    employee_id=emp_id,
                    phone_number=contact_row.get('Phone_Number'),
                    city=contact_row.get('City')
                )
            )

    db.session.commit()
    return jsonify({'message': 'Data synced to database'})


@sync_bp.route('/api/employees')
def get_employees():
    
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("Page_size",10))
    offset = (page-1)*page_size

    query = text("""
        SELECT 
            b.employee_id,
            b.first_name,
            b.date_of_joining,
            s.salary,
            s.pay_grade,
            c.phone_number,
            c.city
        FROM employee_basic_info b
        LEFT JOIN employee_salary_info s ON b.employee_id = s.employee_id
        LEFT JOIN employee_contact_info c ON b.employee_id = c.employee_id
        ORDER BY b.employee_id
        LIMIT :limit OFFSET :offset
    """)

    result = db.session.execute(query, {'limit': page_size, 'offset': offset})
    rows = [dict(row._mapping) for row in result]

    return jsonify(rows)