from flask import redirect, jsonify, request, render_template, current_app as app
from openai import OpenAI
from app.extensions import db
from sqlalchemy import text
from datetime import datetime, timedelta
import os
from . import ai_bp


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fetch_records(sql_query, params=None):
    params = params or {}
    app.logger.info(f"Executing SQL query: {sql_query} with params: {params}")

    try:
        result = db.session.execute(text(sql_query), params)
        records = [dict(row._mapping) for row in result]
        app.logger.info(f"Fetched {len(records)} records from database")
        return records
    except Exception as e:
        app.logger.error(f"Database query error: {e}")
        raise


@ai_bp.route('/api/ai-insights', methods=['POST'])
def ai_insights():
    user_prompt = request.json.get('prompt', '').lower()
    app.logger.info(f"Received AI insight request with prompt: {user_prompt}")

    try:
        if 'all records' in user_prompt or 'all columns' in user_prompt or 'full details' in user_prompt:
            app.logger.info("User requested all records")
            sql = """
            SELECT 
                b.*, 
                s.*, 
                c.*
            FROM employee_basic_info b
            LEFT JOIN employee_salary_info s ON b.employee_id = s.employee_id
            LEFT JOIN employee_contact_info c ON b.employee_id = c.employee_id
            ORDER BY b.employee_id
            """
            records = fetch_records(sql)
            preview = records[:10]
            data_str = ""
            for row in preview:
                row_str = "; ".join([f"{k}: {v}" for k, v in row.items()])
                data_str += f"{row_str}\n"
            prompt_for_ai = f"Here are the full details for the first 10 employees:\n{data_str}\nSummarize or explain this."

        elif 'last 30 days' in user_prompt:
            app.logger.info("User requested last 30 days records")
            start_date = datetime.now() - timedelta(days=30)
            sql = """
            SELECT 
                b.*, 
                s.*, 
                c.*
            FROM employee_basic_info b
            LEFT JOIN employee_salary_info s ON b.employee_id = s.employee_id
            LEFT JOIN employee_contact_info c ON b.employee_id = c.employee_id
            WHERE b.date_of_joining >= :start_date
            ORDER BY b.date_of_joining DESC
            LIMIT 50
            """
            records = fetch_records(sql, {'start_date': start_date})
            preview = records[:10]
            data_str = ""
            for row in preview:
                row_str = "; ".join([f"{k}: {v}" for k, v in row.items()])
                data_str += f"{row_str}\n"
            prompt_for_ai = f"These are full details for employees who joined in the last 30 days:\n{data_str}\nSummarize this data."

        elif 'top cities' in user_prompt:
            app.logger.info("User requested top cities")
            sql = """
            SELECT city, COUNT(*) AS count 
            FROM employee_contact_info
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 3
            """
            records = fetch_records(sql)
            cities = [f"{r['city']}: {r['count']} employees" for r in records]
            data_str = "\n".join(cities)
            prompt_for_ai = f"Here is the employee count per city:\n{data_str}\nPlease summarize this."

        else:
            app.logger.warning(f"Unsupported query prompt received: {user_prompt}")
            return jsonify({"summary": "Sorry, supported queries: 'all records', 'last 30 days', and 'top cities'."})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_for_ai}],
            max_tokens=500
        )
        summary = response.choices[0].message.content
        app.logger.info("Successfully received response from OpenAI API")

        return jsonify({"summary": summary})

    except Exception as e:
        app.logger.error(f"Error processing AI insights request: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500


@ai_bp.route('/ai-insights', methods=['GET'])
def ai_insights_page():
    """
    Serves the AI Insights frontend page with input box and display area.
    """
    return render_template('ai_insights.html')
