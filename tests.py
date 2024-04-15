import pytest
from cli_rest import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_greet_get_missing_required_option(client):
    """Test the greet command with missing required options using GET request."""
    response = client.get('/api/greet')
    assert response.status_code == 400
    assert "Missing required option: --name" in response.json['error']

def test_greet_post_missing_required_option(client):
    """Test the greet command with missing required options using POST request."""
    response = client.post('/api/greet', json={})
    assert response.status_code == 400
    assert "Missing required option: --name" in response.json['error']

def test_greet_get_success(client):
    """Test the greet command success scenario using GET request."""
    response = client.get('/api/greet?name=John&age=30')
    assert response.status_code == 200
    assert "Hello, John. You are 30 years old." in response.json['message']

def test_greet_post_success(client):
    """Test the greet command success scenario using POST request."""
    response = client.post('/api/greet', json={"name": "John", "age": 30})
    assert response.status_code == 200
    assert "Hello, John. You are 30 years old." in response.json['message']

def test_greet_get_success_short_options(client):
    """Test the greet command success scenario using GET request with short options."""
    response = client.get('/api/greet?n=Jane&s=Maple&age=25')
    assert response.status_code == 200
    assert "Hello, Jane. You are 25 years old. Your burth street is Maple." in response.json['message']

def test_greet_get_with_flag(client):
    """Test the greet command with the flag using GET request."""
    response = client.get('/api/greet?name=John&age=30&cc=Yeah')
    assert response.status_code == 200
    assert "You are from California: True" in response.json['message']

def test_greet_get_without_flag(client):
    """Test the greet command without the flag using GET request."""
    response = client.get('/api/greet?name=John&age=30')
    assert response.status_code == 200
    assert "You are from California: False" in response.json['message']

def test_greet_post_with_flag(client):
    """Test the greet command with the flag using POST request."""
    response = client.post('/api/greet', json={"name": "John", "age": 30, "cc": True})
    assert response.status_code == 200
    assert "You are from California: True" in response.json['message']

def test_greet_post_without_flag(client):
    """Test the greet command without the flag using POST request."""
    response = client.post('/api/greet', json={"name": "John", "age": 30})
    assert response.status_code == 200
    assert "You are from California: False" in response.json['message']

def test_greet_get_invalid_choice(client):
    """Test the greet command with an invalid choice for the --verbose option using GET request."""
    response = client.get('/api/greet?name=John&age=30&verbose=NOT_A_LEVEL')
    assert response.status_code == 400
    assert "Invalid value for --verbose. Choose from" in response.json['error']

def test_greet_get_valid_choice(client):
    """Test the greet command with a valid choice for the --verbose option using GET request."""
    response = client.get('/api/greet?name=John&age=30&verbose=DEBUG')
    assert response.status_code == 200
    assert "Verbose: DEBUG" in response.json['message']

def test_send_email_success(client):
    """Test the send_email command success scenario."""
    valid_email = "test@example.com"
    response = client.post('/api/send-email', json={"email": valid_email})
    assert response.status_code == 200
    assert f"Email sent to {valid_email}" in response.json['message']

def test_send_email_invalid_email(client):
    """Test the send_email command with an invalid email."""
    invalid_email = "test"
    response = client.post('/api/send-email', json={"email": invalid_email})
    assert response.status_code == 500
    assert "is not a valid email address" in response.json['error']