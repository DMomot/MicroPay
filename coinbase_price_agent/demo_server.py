import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import Response
import uvicorn
from .client import CoinbaseClient
from .parser import QueryParser

load_dotenv()

app = FastAPI(title="Coinbase Price Agent Demo", description="Historical price data demo server")

# Configuration
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_PRIVATE_KEY = os.getenv("COINBASE_PRIVATE_KEY")
X402_PRICE = "0.01"  # Demo price

@app.get("/api/prices")
async def get_prices(query: str):
    """Demo endpoint for historical price data (would be x402 protected in production)"""
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
            "timestamp": int(time.time()),
            "note": "This is a demo - in production this would require x402 payment"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint - agent description"""
    return {
        "name": "Coinbase Price Agent Demo",
        "description": "Historical cryptocurrency price data (demo version)",
        "version": "1.0.0",
        "endpoints": {
            "/api/prices": {
                "description": "Get historical price data using natural language queries",
                "method": "GET",
                "price": f"${X402_PRICE} (in production)",
                "examples": [
                    "/api/prices?query=Bitcoin price for last year",
                    "/api/prices?query=ETH prices for last month", 
                    "/api/prices?query=Show me SOL hourly data for last week"
                ]
            }
        },
        "note": "This is a demo version. Production version would include x402 micropayments."
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
        port=port
    )

