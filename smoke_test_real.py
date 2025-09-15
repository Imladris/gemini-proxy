# smoke_test_real.py — in-process test using the real Gemini CLI
import os
import json
import traceback
from fastapi.testclient import TestClient

# Use the real gemini found on system
os.environ['GEMINI_PATH'] = '/opt/homebrew/bin/gemini'

from proxy import app

client = TestClient(app)

payload = {
    "model": "gemini-pro",
    "messages": [
        {"role": "user", "content": "请用一句话介绍你自己"}
    ]
}

print('Sending request to /chat/completions using real Gemini CLI...')
try:
    r = client.post('/chat/completions', json=payload, timeout=120)
    print('Status:', r.status_code)
    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    except Exception:
        print('Non-JSON response:')
        print(r.text)
except Exception as e:
    print('Request failed:')
    traceback.print_exc()
