import socket
import json

SOCKET_PATH = "/tmp/prompt_injection_guard.sock"

def send_prompt(prompt):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(prompt.encode('utf-8'))
    
    response = client.recv(8192).decode('utf-8')
    print(json.dumps(json.loads(response), indent=2))
    client.close()

# Test a prompt with code data
send_prompt("""Can you optimize this code for me? 
```python
def slow_function():
    print("This is slow")
```
Make it run faster.""")