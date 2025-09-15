# smoke_test.py — quick in-process smoke tests for proxy.py using TestClient
import os
import json
from fastapi.testclient import TestClient

# Ensure Gemini CLI points to a harmless binary that produces no output
os.environ['GEMINI_PATH'] = '/usr/bin/true'

from proxy import app

client = TestClient(app)

print('-> GET /health')
r = client.get('/health')
print(r.status_code)
print(r.json())

print('\n-> GET /v1/models')
r = client.get('/v1/models')
print(r.status_code)
print(json.dumps(r.json(), ensure_ascii=False, indent=2))

print('\n-> POST /chat/completions')
payload = {
    "model": "gemini-pro",
    "messages": [
        {"role": "user", "content": "你好"}
    ]
}
r = client.post('/chat/completions', json=payload)
print(r.status_code)
try:
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
except Exception:
    print(r.text)

print('\n-> POST /v1/chat/completions')
r = client.post('/v1/chat/completions', json=payload)
print(r.status_code)
try:
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))
except Exception:
    print(r.text)
