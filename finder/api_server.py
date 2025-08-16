from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from gemini_agent_finder import GeminiAgentFinder
import uvicorn

app = FastAPI(
    title="ScoutPay AI Agent Finder API",
    description="API for searching x402 agents by prompt",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify exact domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini AI agent
try:
    import os
    refresh_interval = int(os.getenv('AGENTS_REFRESH_INTERVAL_MINUTES', '60'))
    finder = GeminiAgentFinder(min_rating=0.5, refresh_interval_minutes=refresh_interval)
except ValueError as e:
    print(f"❌ Gemini initialization error: {e}")
    print("💡 Make sure GEMINI_API_KEY is set in .env file")
    finder = None

class SearchRequest(BaseModel):
    prompt: str
    max_results: Optional[int] = 10
    min_rating: Optional[float] = 0.5

class AgentInfo(BaseModel):
    name: str
    resource: str
    description: str
    price_usdc: str
    network: str
    timeout_seconds: int
    asset_address: str
    pay_to_address: str
    last_updated: str
    rating: float  # Rating from 0 to 1

class SearchResponse(BaseModel):
    query: str
    found_agents: int
    agents: List[AgentInfo]
    status: str



@app.get("/health")
async def health_check():
    """Check API status"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini not initialized. Check GEMINI_API_KEY")
    
    try:
        # Check if we can load agents
        agents = finder.load_agents()
        return {
            "status": "healthy",
            "agents_loaded": len(agents),
            "min_rating": finder.min_rating,
            "message": "API working normally"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API unavailable: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_agents(request: SearchRequest):
    """Search agents by prompt with Gemini"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini not initialized")
    
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Set minimum rating if provided
        original_min_rating = finder.min_rating
        if request.min_rating is not None:
            finder.set_min_rating(request.min_rating)
        
        # Search agents with Gemini
        matching_agents = finder.find_agents_by_prompt(request.prompt)
        
        # Restore original rating
        finder.min_rating = original_min_rating
        
        # Limit results count
        limited_agents = matching_agents[:request.max_results]
        
        return SearchResponse(
            query=request.prompt,
            found_agents=len(matching_agents),
            agents=[AgentInfo(**agent) for agent in limited_agents],
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/agents/stats")
async def get_agents_stats():
    """Get agent statistics"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini not initialized")
    
    try:
        # Get all agents from Bazaar
        all_bazaar_data = finder.scout.get_all_agents()
        total_in_bazaar = len(all_bazaar_data.get('items', [])) if all_bazaar_data else 0
        
        # Get filtered agents with descriptions
        agents_with_desc = finder.load_agents()
        
        return {
            "total_agents_in_bazaar": total_in_bazaar,
            "agents_with_description": len(agents_with_desc),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading agents: {str(e)}")





if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8081))
    
    print("🚀 Starting ScoutPay AI Agent Finder API...")
    print(f"📡 API will be available on port {port}")
    print("📚 Documentation: /docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )
