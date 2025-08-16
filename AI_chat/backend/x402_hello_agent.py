from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import os
import json
import time
import secrets
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="Hello x402 Agent", description="Simple agent that says Hello for payment")

# x402 Configuration
X402_PRICE = "100"  # 100 USDC микроединиц (0.0001 USDC)
X402_NETWORK = "base"
X402_ASSET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC на Base
X402_WALLET = os.getenv('X402_WALLET_ADDRESS', '0xce465C087305314F8f0eaD5A450898f19eFD0E03')

class X402PaymentValidator:
    def __init__(self):
        self.required_amount = int(X402_PRICE)
        
    def generate_payment_request(self, request_id=None):
        """Генерирует x402 payment request"""
        if not request_id:
            request_id = secrets.token_hex(16)
            
        return {
            "paymentRequest": {
                "id": request_id,
                "amount": str(self.required_amount),
                "asset": X402_ASSET,
                "network": X402_NETWORK,
                "recipient": X402_WALLET,
                "timeout": 300,  # 5 минут
                "description": "Payment for Hello service"
            }
        }
    
    def validate_payment_proof(self, proof_header):
        """Валидирует proof of payment (упрощенная версия)"""
        try:
            # В реальной реализации тут должна быть проверка on-chain транзакции
            # Для демо просто проверяем наличие заголовка
            if not proof_header:
                return False
                
            # Простая проверка формата (в продакшене нужна полная валидация)
            if "0x" in proof_header and len(proof_header) > 20:
                return True
                
            return False
        except Exception:
            return False

# Инициализация валидатора платежей
payment_validator = X402PaymentValidator()

@app.middleware("http")
async def x402_middleware(request: Request, call_next):
    """x402 middleware для обработки платежей"""
    
    # Проверяем только защищенные эндпоинты
    if request.url.path.startswith("/api/hello"):
        
        # Проверяем наличие payment proof
        payment_proof = request.headers.get("x-payment-proof")
        
        if not payment_proof:
            # Возвращаем 402 Payment Required с инструкциями
            payment_request = payment_validator.generate_payment_request()
            
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Payment Required",
                    "message": "This endpoint requires payment via x402 protocol",
                    **payment_request
                },
                headers={
                    "x-payment-required": "true",
                    "x-payment-amount": X402_PRICE,
                    "x-payment-asset": X402_ASSET,
                    "x-payment-network": X402_NETWORK,
                    "x-payment-recipient": X402_WALLET
                }
            )
        
        # Валидируем payment proof
        if not payment_validator.validate_payment_proof(payment_proof):
            return JSONResponse(
                status_code=402,
                content={
                    "error": "Invalid Payment Proof", 
                    "message": "Payment proof validation failed"
                }
            )
    
    # Если все ок, продолжаем
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    """Информация о сервисе"""
    return {
        "service": "Hello x402 Agent",
        "description": "Simple agent that says Hello for x402 payment",
        "version": "1.0.0",
        "endpoints": {
            "hello": "/api/hello",
            "pricing": {
                "amount": X402_PRICE,
                "asset": "USDC",
                "network": X402_NETWORK
            }
        }
    }

@app.get("/api/hello")
async def hello_endpoint():
    """Основной эндпоинт - говорит Hello за плату"""
    return {
        "message": "Hello! 👋",
        "agent": "x402 Hello Agent",
        "timestamp": int(time.time()),
        "status": "success"
    }

@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {"status": "healthy", "service": "x402-hello-agent"}

# x402 Discovery endpoint для автоматической регистрации
@app.get("/.well-known/x402")
async def x402_discovery():
    """x402 discovery endpoint для автоматической регистрации в Bazaar"""
    return {
        "version": "1.0",
        "endpoints": [
            {
                "path": "/api/hello",
                "method": "GET",
                "description": "Simple Hello service via x402 payment",
                "price": {
                    "amount": X402_PRICE,
                    "asset": X402_ASSET,
                    "network": X402_NETWORK
                },
                "accepts": [
                    {
                        "asset": X402_ASSET,
                        "description": "Simple Hello greeting service",
                        "extra": {
                            "name": "USD Coin",
                            "version": "2"
                        },
                        "maxAmountRequired": X402_PRICE,
                        "maxTimeoutSeconds": 300,
                        "mimeType": "application/json",
                        "network": X402_NETWORK,
                        "outputSchema": {
                            "input": {
                                "method": "GET",
                                "type": "http"
                            },
                            "output": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"},
                                    "agent": {"type": "string"},
                                    "timestamp": {"type": "number"}
                                }
                            }
                        },
                        "payTo": X402_WALLET,
                        "resource": "/api/hello",
                        "scheme": "exact"
                    }
                ]
            }
        ]
    }

if __name__ == "__main__":
    print("🚀 Запускаю x402 Hello Agent...")
    print(f"💰 Цена: {X402_PRICE} USDC микроединиц")
    print(f"🌐 Сеть: {X402_NETWORK}")
    print(f"💳 Кошелек: {X402_WALLET}")
    print(f"🔗 Эндпоинт: /api/hello")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
