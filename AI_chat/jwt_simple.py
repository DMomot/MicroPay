import jwt
import time
import secrets

# Точно по документации ECDSA пример (но с твоими ключами как HMAC)
key_name = "44fe7a52-eeff-4b97-aec0-53a87e01f355"
key_secret = "1BwVrH7c6OrNzDS1tLn9p4G8mP8KEENoVGRgce/iOUM9v+T9xdlqFbLrXD65sMgvoMmH0RvRUAks4TOvFp6CkQ=="
request_method = "GET"
request_host = "api.cdp.coinbase.com"
request_path = "/platform/v2/x402/discovery/resources"

def build_jwt(uri):
    jwt_payload = {
        'sub': key_name,
        'iss': "cdp",
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,
        'uri': uri,
    }
    # Поскольку у нас нет PEM ключа, используем HS256
    import base64
    decoded_secret = base64.b64decode(key_secret)
    jwt_token = jwt.encode(
        jwt_payload,
        decoded_secret,
        algorithm='HS256',
    )
    return jwt_token

def main():
    uri = f"{request_method} {request_host}{request_path}"
    jwt_token = build_jwt(uri)
    print(jwt_token)

if __name__ == "__main__":
    main()
