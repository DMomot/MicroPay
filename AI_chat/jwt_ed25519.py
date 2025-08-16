import json
import base64
import time
import secrets
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Твои правильные Ed25519 ключи!
key_name = "44fe7a52-eeff-4b97-aec0-53a87e01f355"
key_secret = "1BwVrH7c6OrNzDS1tLn9p4G8mP8KEENoVGRgce/iOUM9v+T9xdlqFbLrXD65sMgvoMmH0RvRUAks4TOvFp6CkQ=="
request_method = 'GET'
url = 'api.cdp.coinbase.com'
request_path = '/platform/v2/x402/discovery/resources'
uri = request_method + ' ' + url + request_path

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).decode().rstrip('=')

def build_jwt():
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
        'exp': int(time.time()) + 120,
        'sub': key_name,
        'uri': uri,
    }
    
    # Encode header and payload
    header_b64 = base64url_encode(json.dumps(header).encode())
    payload_b64 = base64url_encode(json.dumps(payload).encode())
    header_payload = f"{header_b64}.{payload_b64}"
    
    # Ed25519 signature
    key_buf = base64.b64decode(key_secret)
    private_key = Ed25519PrivateKey.from_private_bytes(key_buf[:32])  # Ed25519 uses 32 bytes
    signature = private_key.sign(header_payload.encode())
    signature_b64 = base64url_encode(signature)
    
    return f"{header_payload}.{signature_b64}"

jwt_token = build_jwt()
print(f"JWT: {jwt_token}")
print(f'\ncurl -X GET "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources" \\')
print(f'  -H "Authorization: Bearer {jwt_token}" \\')
print(f'  -H "Content-Type: application/json"')
