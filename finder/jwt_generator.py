import json
import base64
import time
import secrets
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Coinbase CDP API Keys для x402 Bazaar
key_name = "44fe7a52-eeff-4b97-aec0-53a87e01f355"
key_secret = "1BwVrH7c6OrNzDS1tLn9p4G8mP8KEENoVGRgce/iOUM9v+T9xdlqFbLrXD65sMgvoMmH0RvRUAks4TOvFp6CkQ=="

def base64url_encode(data):
    """Кодирование в base64url без padding"""
    return base64.urlsafe_b64encode(data).decode().rstrip('=')

def generate_jwt(endpoint_path):
    """Генерирует JWT токен для Coinbase CDP API"""
    request_method = 'GET'
    url = 'api.cdp.coinbase.com'
    uri = f"{request_method} {url}{endpoint_path}"
    
    # Header
    header = {
        "typ": "JWT",
        "alg": "EdDSA",
        "kid": key_name,
        "nonce": secrets.token_hex(16),
    }
    
    # Payload
    payload = {
        'iss': 'cdp',
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,  # 2 минуты
        'sub': key_name,
        'uri': uri,
    }
    
    # Encode header and payload
    header_b64 = base64url_encode(json.dumps(header).encode())
    payload_b64 = base64url_encode(json.dumps(payload).encode())
    header_payload = f"{header_b64}.{payload_b64}"
    
    # Ed25519 signature
    key_buf = base64.b64decode(key_secret)
    private_key = Ed25519PrivateKey.from_private_bytes(key_buf[:32])
    signature = private_key.sign(header_payload.encode())
    signature_b64 = base64url_encode(signature)
    
    return f"{header_payload}.{signature_b64}"

if __name__ == "__main__":
    # Генерируем JWT для discovery endpoint
    endpoint = "/platform/v2/x402/discovery/resources"
    jwt_token = generate_jwt(endpoint)
    
    print(f"JWT Token generated for x402 Bazaar:")
    print(f"Endpoint: {endpoint}")
    print(f"Token: {jwt_token}")
    print(f"\nCurl command:")
    print(f'curl -X GET "https://api.cdp.coinbase.com{endpoint}" \\')
    print(f'  -H "Authorization: Bearer {jwt_token}" \\')
    print(f'  -H "Content-Type: application/json"')
