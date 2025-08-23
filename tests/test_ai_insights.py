import pytest
import json
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING":True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_ai_insights_all_records(client):
    response = client.post('/api/ai-insights',json={"prompt":"all records"})
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "summary" in data
    assert len(data["summary"])>0

def test_ai_insights_last_30_days(client):
    response = client.post('/api/ai-insights', json={"prompt": "last 30 days"})
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert "summary" in data

def test_ai_insights_unsupported_query(client):
    response = client.post('/api/ai-insights', json={"prompt": "unsupported query"})
    assert response.status_code in [200, 400]  # Depending on how backend handles unknown queries
    
    data = json.loads(response.data)
    assert "summary" in data or "error" in data  # Checks either summary or error message is returned