import io
import numpy as np
from PIL import Image
from app import app

def sample_png():
    stream = io.BytesIO()
    Image.fromarray(np.full((32, 40, 3), 120, dtype=np.uint8)).save(stream, format='PNG')
    stream.seek(0)
    return stream

def test_health():
    response = app.test_client().get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'

def test_homepage():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert b'LumaLab' in response.data

def test_process_image():
    response = app.test_client().post('/api/process', data={'image': (sample_png(), 'sample.png')}, content_type='multipart/form-data')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['width'] == 40 and data['height'] == 32
    assert data['processed'].startswith('data:image/jpeg;base64,')

def test_missing_image():
    assert app.test_client().post('/api/process').status_code == 400

def test_unsupported_file():
    response = app.test_client().post('/api/process', data={'image': (io.BytesIO(b'not an image'), 'notes.txt')}, content_type='multipart/form-data')
    assert response.status_code == 415
