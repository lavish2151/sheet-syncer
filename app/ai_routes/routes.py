from flask import redirect, jsonify, request, render_template, current_app as app
from openai import OpenAI
from app.extensions import db
from sqlalchemy import text
from datetime import datetime, timedelta
import os
from . import ai_bp
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

schema_description = schema_description = """
You have access to the following database schema with tables and their relationships:

Table: employee_basic_info
- id (Primary Key)
- employee_id (Unique, NOT NULL)
- first_name (NOT NULL)
- date_of_joining (NOT NULL)

Table: employee_salary_info
- id (Primary Key)
- employee_id (Foreign Key to employee_basic_info.employee_id, NOT NULL)
- salary
- pay_grade

Table: employee_contact_info
- id (Primary Key)
- employee_id (Foreign Key to employee_basic_info.employee_id, NOT NULL)
- phone_number
- city

Relationships:
- employee_salary_info has a many-to-one relationship with employee_basic_info via employee_id.
- employee_contact_info has a many-to-one relationship with employee_basic_info via employee_id.
- Each employee_basic_info record may have zero or one related salary_info and contact_info record.
"""


def fetch_records(sql_query, params=None):
    params = params or {}
    app.logger.info(f"Executing SQL query: {sql_query} with params: {params}")

    try:
        result = db.session.execute(text(sql_query), params)
        records = [dict(row._mapping) for row in result]
        print(records)
        app.logger.info(f"Fetched {len(records)} records from database")
        return records
    except Exception as e:
        app.logger.error(f"Database query error: {e}")
        raise

    
def generate_sql_query_with_llm(user_prompt):
    combined_prompt=(
        f"{schema_description}\n"
        f'User question: "{user_prompt}"\n'
        "Write a SQL select query (limit 50 rows) for this question. Output only the SQL code.Not write anything other than that. Consider, the output row should contain all the information if not specified by the user. Keep in mind that my database type is postgresql"
    )
    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {'role': 'system', 'content':'You are a helpful SQL assistant'},
            {'role': 'user', 'content':combined_prompt}
        ],
        max_tokens = 300
    )
    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.removeprefix('```sql').strip()
    sql_query = sql_query.removesuffix('```').strip()
    return sql_query


def is_select_query(sql_query):
    sql_query = sql_query.strip().lower()
    if not sql_query.startswith('select'):
        return False
    dangerours_keywords = ["insert", "update", "delete", "drop", "alter", "truncate", "create"]
    for keyword in dangerours_keywords:
        if keyword in sql_query:
            return False
    return True


@ai_bp.route('/api/ai-insights', methods=['POST'])
def ai_insights():
    """
    Main API endpoint for AI-powered insights.
    Receives a natural language prompt, generates and executes SQL,
    then summarizes and returns results as JSON.
    """
    try:
        user_prompt = request.json.get('prompt', '')
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400
        app.logger.info(f"Received prompt: {user_prompt}")

        sql_query = generate_sql_query_with_llm(user_prompt)

        if not is_select_query(sql_query):
            return jsonify({"summary": "Generated SQL query is invalid or not allowed."}), 400

        records = fetch_records(sql_query)
        preview = records[:10]

        data_str = "\n".join(
            "; ".join(f"{k}: {v}" for k, v in row.items())
            for row in preview
        )

        summary_prompt = (
            f'User question: "{user_prompt}"\n'
            f"Here is sample data (up to 10 rows):\n{data_str}\n"
            "Please provide a concise and clear summary based on this data."
        )

        summary_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": schema_description},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=250
        )
        summary = summary_resp.choices[0].message.content.strip()
        app.logger.info("Successfully generated summary")

        return jsonify({"summary": summary})
    except Exception as e:
        app.logger.error(f"Error in AI insights endpoint: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred."}), 500


@ai_bp.route('/ai-insights', methods=['GET'])
def ai_insights_page():
    """
    Serves the AI Insights frontend page with input box and display area.
    """
    return render_template('ai_insights.html')
