import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from x402.fastapi.middleware import require_payment
from cdp.x402 import create_facilitator_config
import uvicorn
from .analyst import BlockchainAnalyst

load_dotenv()

app = FastAPI(
    title="Blockchain Analyst Agent x402", 
    description="Professional blockchain analyst with x402 micropayments"
)

# x402 Configuration
X402_WALLET = os.getenv("X402_WALLET_ADDRESS", "0xce465C087305314F8f0eaD5A450898f19eFD0E03")
X402_NETWORK = os.getenv("X402_NETWORK", "base")
X402_PRICE = os.getenv("X402_PRICE", "0.05")  # $0.05 per analysis

# CDP API keys
CDP_API_KEY_ID = os.getenv("CDP_API_KEY_ID")
CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")

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
            path="/api/analyze",
            price=f"${X402_PRICE}",
            pay_to_address=X402_WALLET,
            network=X402_NETWORK,
            facilitator_config=facilitator_config,
            description="Professional blockchain analysis and insights"
        )
    
    def _add_headers(self, response: Response) -> Response:
        """Add CORS and security headers"""
        response.headers.update({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "X-Payment-Required, X-Accept-Payment"
        })
        return response
    
    async def dispatch(self, request: Request, call_next):
        # ALWAYS handle OPTIONS first for CORS preflight
        if request.method == "OPTIONS":
            return self._add_headers(Response(status_code=200))
        
        if request.method == "HEAD":
            return self._add_headers(Response())
        
        # For x402 protected endpoint, we need to handle CORS differently
        if request.url.path == "/api/analyze" and request.method in ["GET", "POST"]:
            try:
                response = await self.payment_handler(request, call_next)
                # Add CORS headers to x402 responses
                return self._add_headers(response)
            except Exception as e:
                # If x402 fails, still add CORS headers
                error_response = Response(
                    content=str(e),
                    status_code=500,
                    media_type="text/plain"
                )
                return self._add_headers(error_response)
        else:
            response = await call_next(request)
            return self._add_headers(response)

app.add_middleware(UnifiedMiddleware)

# Initialize analyst
analyst = BlockchainAnalyst()

@app.get("/api/analyze")
async def analyze_blockchain(query: str):
    """x402 protected endpoint for blockchain analysis"""
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    if not analyst.model:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")
    
    try:
        # Perform analysis
        result = await analyst.analyze_query(query.strip())
        
        return {
            "query": query,
            "analysis": result,
            "timestamp": int(time.time()),
            "agent": "Blockchain Analyst (Gemini Flash 2.0)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.head("/api/analyze")
async def analyze_head():
    """HEAD request for header checking - always free"""
    return Response(status_code=200)

@app.get("/")
async def root():
    """Root endpoint - agent description"""
    return {
        "name": "Blockchain Analyst Agent x402 (Gemini Flash 2.0)",
        "description": "Professional blockchain analyst powered by Gemini Flash 2.0, providing comprehensive market analysis, trend insights, and investment recommendations with x402 micropayments",
        "version": "1.0.0",
        "x402Version": 1,
        "network": X402_NETWORK,
        "discoverable": True,
        "specialties": [
            "Cryptocurrency market analysis",
            "DeFi protocol evaluation", 
            "NFT market trends",
            "Technical analysis",
            "Risk assessment",
            "Investment recommendations",
            "On-chain data interpretation",
            "Regulatory impact analysis"
        ],
        "endpoints": {
            "/api/analyze": {
                "description": "Get comprehensive blockchain analysis using natural language queries",
                "method": "GET",
                "price": f"${X402_PRICE}",
                "network": X402_NETWORK,
                "asset": USDC_ASSETS.get(X402_NETWORK, USDC_ASSETS["base"]),
                "examples": [
                    "Analyze Bitcoin's recent price movement and predict next week's trend",
                    "What are the best DeFi yield farming opportunities right now?",
                    "Evaluate the risk of investing in Ethereum before the next upgrade",
                    "Compare the performance of top 10 cryptocurrencies this month"
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
        "name": "Blockchain Analyst Agent x402 (Gemini Flash 2.0)",
        "description": "Professional blockchain analyst powered by Gemini Flash 2.0, providing comprehensive market analysis and investment insights",
        "endpoints": [
            {
                "path": "/api/analyze",
                "method": "GET",
                "price": f"${X402_PRICE}",
                "network": X402_NETWORK,
                "description": "Get professional blockchain analysis via natural language queries",
                "accepts": {
                    "scheme": "exact",
                    "network": X402_NETWORK,
                    "maxAmountRequired": price_in_micro_units,
                    "asset": USDC_ASSETS.get(X402_NETWORK, USDC_ASSETS["base"]),
                    "payTo": X402_WALLET,
                    "maxTimeoutSeconds": 300,
                    "resource": f"/api/analyze"
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
