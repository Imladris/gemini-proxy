import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from proxy import app


class ProxyTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('proxy.run_gemini_cli', new_callable=AsyncMock)
    def test_chat_completions_messages(self, mock_run):
        mock_run.return_value = 'Gemini response text'
        payload = {
            'messages': [
                {'role': 'user', 'content': 'Say hello'}
            ],
            'model': 'gemini-local'
        }
        resp = self.client.post('/v1/chat/completions', json=payload)
        self.assertEqual(resp.status_code, 200)
        j = resp.json()
        self.assertIn('choices', j)
        self.assertEqual(j['choices'][0]['message']['content'], 'Gemini response text')

    def test_no_prompt(self):
        resp = self.client.post('/v1/chat/completions', json={})
        self.assertEqual(resp.status_code, 400)

    @patch('proxy.asyncio.create_subprocess_exec')
    def test_run_gemini_cli_called(self, mock_create):
        # Mock an async subprocess that returns stdout
        mock_proc = MagicMock()
        async def mock_communicate():
            return (b'ok', b'')
        mock_proc.communicate = mock_communicate
        mock_proc.returncode = 0

        async def mock_create_proc(*args, **kwargs):
            return mock_proc

        mock_create.side_effect = mock_create_proc
        from proxy import run_gemini_cli
        import asyncio
        out = asyncio.run(run_gemini_cli('hello'))
        self.assertEqual(out, 'ok')


if __name__ == '__main__':
    unittest.main()
