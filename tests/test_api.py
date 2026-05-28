import pytest
import json
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_predict_missing_fields(client):
    response = client.post('/api/predict',
        json={'location': 'Mumbai'},
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_recent_requests_endpoint(client):
    response = client.get('/api/recent-requests')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'requests' in data