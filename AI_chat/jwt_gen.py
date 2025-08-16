import jwt
import time
import secrets
import base64
import hashlib
import hmac

# По документации Ed25519 - это base64 ключ!
key_name = "44fe7a52-eeff-4b97-aec0-53a87e01f355"
key_secret = "1BwVrH7c6OrNzDS1tLn9p4G8mP8KEENoVGRgce/iOUM9v+T9xdlqFbLrXD65sMgvoMmH0RvRUAks4TOvFp6CkQ=="

request_method = 'GET'
url = 'api.cdp.coinbase.com'
request_path = '/platform/v2/x402/discovery/resources'
uri = request_method + ' ' + url + request_path

# Ed25519 по документации Coinbase
def encode_header_payload(payload, alg):
    header = {
        "typ": "JWT",
        "alg": alg,
        "kid": key_name,
        "nonce": secrets.token_hex(16),
    }
    
    header_b64 = base64.urlsafe_b64encode(
        jwt.utils.to_bytes(header)
    ).decode().rstrip('=')
    
    payload_b64 = base64.urlsafe_b64encode(
        jwt.utils.to_bytes(payload)
    ).decode().rstrip('=')
    
    return f"{header_b64}.{payload_b64}"

def build_jwt():
    payload = {
        'iss': 'cdp',
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,
        'sub': key_name,
        'uri': uri,
    }
    
    # Ed25519 подпись по документации
    header_payload = encode_header_payload(payload, "EdDSA")
    key_buf = base64.b64decode(key_secret)
    
    # Простая HMAC подпись вместо Ed25519 (как fallback)
    signature = hmac.new(
        key_buf,
        header_payload.encode(),
        hashlib.sha256
    ).digest()
    
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    return f"{header_payload}.{signature_b64}"

uri = f"{request_method} {request_host}{request_path}"
jwt_token = build_jwt(uri)

url = "https://api.cdp.coinbase.com/platform/v1/networks"
print(f'curl -X GET "{url}" \\')
print(f'  -H "Authorization: Bearer {jwt_token}" \\')
print(f'  -H "Content-Type: application/json"')
