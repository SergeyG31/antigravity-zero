import sys
import json
import requests
import os

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN", "mock_token")

def log(msg):
    # MCP servers must log to stderr to avoid corrupting stdout
    print(f"DEBUG: {msg}", file=sys.stderr)

def handle_request(request):
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "HuggingFaceReelsLocal",
                "version": "1.0.0"
            }
        }
    
    elif method == "tools/list":
        return {
            "tools": [
                {
                    "name": "hf_inference",
                    "description": "Run inference on a Hugging Face model",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "model": {"type": "string", "description": "Model ID on Hugging Face"},
                            "inputs": {"type": "string", "description": "Input text for the model"}
                        },
                        "required": ["model", "inputs"]
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "hf_inference":
            model = arguments.get("model")
            inputs = arguments.get("inputs")
            
            try:
                API_URL = f"https://api-inference.huggingface.co/models/{model}"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                response = requests.post(API_URL, headers=headers, json={"inputs": inputs})
                
                if response.status_code == 200:
                    return {
                        "content": [
                            {"type": "text", "text": json.dumps(response.json(), indent=2)}
                        ]
                    }
                else:
                    return {
                        "isError": True,
                        "content": [
                            {"type": "text", "text": f"HF API Error: {response.text}"}
                        ]
                    }
            except Exception as e:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Error calling HF: {str(e)}"}
                    ]
                }
    
    return None

def main():
    log("HuggingFaceReels Python Server Started")
    for line in sys.stdin:
        try:
            request = json.loads(line)
            request_id = request.get("id")
            
            result = handle_request(request)
            
            if result is not None:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                print(json.dumps(response))
                sys.stdout.flush()
        except Exception as e:
            log(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
