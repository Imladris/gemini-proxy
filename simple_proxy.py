from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import logging
import uuid
import time
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            models = {
                "object": "list",
                "data": [{
                    "id": "gemini-2.5-pro-preview-06-05",
                    "object": "model",
                    "owned_by": "google",
                    "permission": []
                }]
            }
            self.wfile.write(json.dumps(models).encode())
            return
            
        self.send_error(404)

    def do_POST(self):
        if self.path == '/v1/chat/completions':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode())
                
                # 生成请求ID
                request_id = str(uuid.uuid4().hex)
                logging.info(f"[REQUEST_START] id={request_id}")
                
                try:
                    # 处理消息
                    messages = request_data.get('messages', [])
                    prompt = self._process_messages(messages)
                    
                    # 调用 Gemini
                    logging.info(f"[GEMINI_CALL_START] id={request_id}")
                    response = self._call_gemini(prompt)
                    logging.info(f"[GEMINI_CALL_END] id={request_id} output_preview='{response[:100]}'")
                    
                    # 构建响应
                    completion = {
                        "id": f"chatcmpl-{request_id}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": request_data.get('model', 'gemini-2.5-pro-preview-06-05'),
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": len(response.split()),
                            "total_tokens": len(prompt.split()) + len(response.split())
                        }
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(completion).encode())
                    logging.info(f"[REQUEST_END] id={request_id} status=success")
                    return
                    
                except Exception as e:
                    logging.error(f"[ERROR] id={request_id} error={str(e)}")
                    error = {
                        "error": {
                            "message": str(e),
                            "type": "internal_error",
                            "code": "gemini_error"
                        }
                    }
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(error).encode())
                    return
            
        self.send_error(404)
        
    def _process_messages(self, messages):
        """处理消息历史"""
        formatted = []
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '').strip()
            
            if role == 'system':
                formatted.append(f"Instructions: {content}\n")
            elif role == 'user':
                formatted.append(f"Human: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
                
        # 确保以助手提示符结尾
        if messages and messages[-1].get('role') == 'user':
            formatted.append("Assistant:")
            
        return "\n\n".join(formatted)

    def _call_gemini(self, prompt):
        """调用 Gemini CLI 并清理输出"""
        gemini_path = os.getenv('GEMINI_PATH', '/opt/homebrew/bin/gemini')
        
        # 检查 Gemini CLI 是否存在
        if not os.path.exists(gemini_path):
            raise FileNotFoundError(f"Gemini CLI not found at {gemini_path}")
            
        try:
            # 调用 Gemini CLI
            process = subprocess.Popen(
                [gemini_path, '--prompt', prompt, '--yolo', '--approval-mode', 'yolo'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=30)
            
            if process.returncode != 0:
                raise RuntimeError(f"Gemini CLI failed: {stderr}")
                
            # 清理输出
            return self._clean_output(stdout)
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError("Gemini CLI timed out")
            
    def _clean_output(self, output):
        """清理 Gemini 输出"""
        if not output:
            return "I apologize, but I received no response."
            
        lines = []
        for line in output.split('\n'):
            # 跳过 ASCII 艺术和 UI 元素
            if any(char in line for char in '█░╭╮╯╰│─┌┐└┘'):
                continue
                
            # 跳过命令行提示和状态信息
            if any(marker in line.lower() for marker in [
                'tips for getting', 'ask questions', '/help',
                'interaction summary', 'session id', 'wall time',
                'agent', 'performance', 'success rate'
            ]):
                continue
            
            # 清理 XML/HTML 标签
            if '<' in line:
                text = line.split('<')[0].strip()
                if text:
                    lines.append(text)
                continue
                
            # 保留有效文本
            if line.strip():
                lines.append(line.strip())
                
        result = ' '.join(lines)
        return result.strip() or "I apologize, but I was unable to generate a proper response."

def run_server(port=9999):
    print(f"Starting server on port {port}...")
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == '__main__':
    run_server()