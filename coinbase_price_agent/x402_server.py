import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from x402.fastapi.middleware import require_payment
from cdp.x402 import create_facilitator_config
import uvicorn
from .client import CoinbaseClient
from .parser import QueryParser

load_dotenv()

app = FastAPI(title="Coinbase Price Agent x402", description="Historical price data with x402 payments")

# x402 Configuration
X402_WALLET = os.getenv("X402_WALLET_ADDRESS", "0xce465C087305314F8f0eaD5A450898f19eFD0E03")
X402_NETWORK = os.getenv("X402_NETWORK", "base")
X402_PRICE = os.getenv("X402_PRICE", "0.01")  # $0.01 per query

# CDP API keys
CDP_API_KEY_ID = os.getenv("CDP_API_KEY_ID")
CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")

# Coinbase API keys
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_PRIVATE_KEY = os.getenv("COINBASE_PRIVATE_KEY")

# Asset addresses
USDC_ASSETS = {
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "base-sepolia": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
}

class UnifiedMiddleware(BaseHTTPMiddleware):
    """Unified middleware for CORS and x402 payments"""
    
    def __init__(self, app):
        super().__init__(app)
        
        facilitator_config = None
        if CDP_API_KEY_ID and CDP_API_KEY_SECRET:
            facilitator_config = create_facilitator_config(
                api_key_id=CDP_API_KEY_ID,
                api_key_secret=CDP_API_KEY_SECRET,
            )
        
        self.payment_handler = require_payment(
            path="/api/prices",
            price=f"${X402_PRICE}",
            pay_to_address=X402_WALLET,
            network=X402_NETWORK,
            facilitator_config=facilitator_config,
            description="Historical cryptocurrency price data"
        )
    
    def _add_headers(self, response: Response) -> Response:
        """Add CORS and security headers"""
        response.headers.update({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Cross-Origin-Opener-Policy": "same-origin-allow-popups",
            "Cross-Origin-Embedder-Policy": "require-corp"
        })
        return response
    
    async def dispatch(self, request: Request, call_next):
        if request.method in ["OPTIONS", "HEAD"]:
            return self._add_headers(Response())
        
        if request.url.path == "/api/prices" and request.method == "GET":
            response = await self.payment_handler(request, call_next)
        else:
            response = await call_next(request)
        
        return self._add_headers(response)

app.add_middleware(UnifiedMiddleware)

@app.get("/api/prices")
async def get_prices(query: str):
    """x402 protected endpoint for historical price data"""
    if not COINBASE_API_KEY or not COINBASE_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="Coinbase API keys not configured")
    
    try:
        # Parse natural language query
        parser = QueryParser()
        parsed_params = parser.parse_query(query)
        
        if not parsed_params["start"]:
            raise HTTPException(status_code=400, detail=f"Failed to parse date from query: '{query}'")
        
        # Get historical data
        client = CoinbaseClient(COINBASE_API_KEY, COINBASE_PRIVATE_KEY)
        data = await client.get_historical_prices(
            symbol=parsed_params["index"],
            start=parsed_params["start"],
            granularity=parsed_params["granularity"],
            end=parsed_params["end"]
        )
        
        return {
            "query": query,
            "parsed_params": parsed_params,
            "data": data,
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.head("/api/prices")
async def prices_head():
    """HEAD request for header checking - always free"""
    return Response(status_code=200)

@app.get("/")
async def root():
    """Root endpoint - agent description"""
    return {
        "name": "Coinbase Price Agent x402",
        "description": "Historical cryptocurrency price data with x402 micropayments",
        "version": "1.0.0",
        "x402Version": 1,
        "network": X402_NETWORK,
        "discoverable": True,
        "endpoints": {
            "/api/prices": {
                "description": "Get historical price data using natural language queries",
                "method": "GET",
                "price": f"${X402_PRICE}",
                "network": X402_NETWORK,
                "asset": USDC_ASSETS.get(X402_NETWORK, USDC_ASSETS["base"]),
                "examples": [
                    "Bitcoin price for last year",
                    "ETH prices for last month",
                    "Show me SOL hourly data for last week"
                ]
            }
        },
        "contact": {
            "owner": "Dmitrii Momot"
        },
        "author": "Dmitrii Momot",
        "x402_compatible": True
    }

@app.get("/.well-known/x402")
async def x402_discovery():
    """x402 discovery endpoint for Bazaar registration"""
    price_in_micro_units = str(int(float(X402_PRICE) * 1000000))
    
    return {
        "x402Version": 1,
        "name": "Coinbase Price Agent x402",
        "description": "Historical cryptocurrency price data with micropayments",
        "endpoints": [
            {
                "path": "/api/prices",
                "method": "GET",
                "price": f"${X402_PRICE}",
                "network": X402_NETWORK,
                "description": "Get historical crypto price data via natural language queries",
                "accepts": {
                    "scheme": "exact",
                    "network": X402_NETWORK,
                    "maxAmountRequired": price_in_micro_units,
                    "asset": USDC_ASSETS.get(X402_NETWORK, USDC_ASSETS["base"]),
                    "payTo": X402_WALLET,
                    "maxTimeoutSeconds": 300,
                    "resource": f"/api/prices"
                }
            }
        ],
        "contact": {
            "owner": "Dmitrii Momot"
        },
        "version": "1.0.0",
        "discoverable": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": int(time.time())}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        forwarded_allow_ips="*",
        proxy_headers=True
    )

