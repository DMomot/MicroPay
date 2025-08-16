import json
import base64
import time
import secrets
import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import os
from dotenv import load_dotenv

load_dotenv('../.env')

class CoinbaseClient:
    def __init__(self):
        self.key_name = os.getenv('CDP_KEY_NAME')
        self.key_secret = os.getenv('CDP_KEY_SECRET')
        self.base_url = 'https://api.cdp.coinbase.com'
        
    def base64url_encode(self, data):
        return base64.urlsafe_b64encode(data).decode().rstrip('=')

    def build_jwt(self, method, path):
        uri = f"{method} api.cdp.coinbase.com{path}"
        
        # Header
        header = {
            "typ": "JWT",
            "alg": "EdDSA", 
            "kid": self.key_name,
            "nonce": secrets.token_hex(16),
        }
        
        # Payload
        payload = {
            'iss': 'cdp',
            'nbf': int(time.time()),
            'exp': int(time.time()) + 120,
            'sub': self.key_name,
            'uri': uri,
        }
        
        # Encode header and payload
        header_b64 = self.base64url_encode(json.dumps(header).encode())
        payload_b64 = self.base64url_encode(json.dumps(payload).encode())
        header_payload = f"{header_b64}.{payload_b64}"
        
        # Ed25519 signature
        key_buf = base64.b64decode(self.key_secret)
        private_key = Ed25519PrivateKey.from_private_bytes(key_buf[:32])
        signature = private_key.sign(header_payload.encode())
        signature_b64 = self.base64url_encode(signature)
        
        return f"{header_payload}.{signature_b64}"

    def make_request(self, method, path, data=None):
        jwt_token = self.build_jwt(method, path)
        
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{path}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response.json() if response.status_code == 200 else None

    def get_resources(self):
        """Получает список ресурсов"""
        return self.make_request('GET', '/platform/v2/x402/discovery/resources')
        
    def get_wallets(self):
        """Получает список кошельков"""
        return self.make_request('GET', '/v2/accounts')
        
    def get_balance(self, account_id):
        """Получает баланс аккаунта"""
        return self.make_request('GET', f'/v2/accounts/{account_id}')
