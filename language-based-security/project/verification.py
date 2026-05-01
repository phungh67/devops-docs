import socket
import json

SOCKET_PATH = "/tmp/prompt_injection_guard.sock"

def send_prompt(prompt):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.connect(SOCKET_PATH)
        client.sendall(prompt.encode('utf-8'))
        
        response = client.recv(8192).decode('utf-8')
        result = json.loads(response)
        
        print("\n" + "="*50)
        print(f"STATUS: {result.get('status')}")
        
        if result.get('status') == "BLOCKED":
            print(f"REASON: {result.get('reason')}")
            
        elif result.get('status') == "APPROVED":
            print("-" * 50)
            print("FINAL PAYLOAD FOR LLM:")
            print("-" * 50)
            # Printing this directly renders the \n as actual line breaks
            print(result.get('safe_payload'))
            
        print("="*50 + "\n")
        
    except FileNotFoundError:
        print("Error: Daemon is not running. Start main.py first.")
    finally:
        client.close()

if __name__ == "__main__":
    # Test a prompt with code data
    test_prompt = """Can you optimize this code for me? Make it run faster.
```python
def slow_function():
    print("This is slow")
```"""
    send_prompt(test_prompt)