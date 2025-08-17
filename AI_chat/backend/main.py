from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

app = FastAPI(title="AI Chat Bot API", version="1.0.0")

# Get CORS origins from environment or use default
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Загружаем системный промпт из файла
def load_prompt(prompt_name='system_prompt'):
    try:
        with open(f'prompts/{prompt_name}.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "You are a friendly AI assistant. Always respond in English only."

SYSTEM_PROMPT = load_prompt()
PROMPT_OPTIMIZER = load_prompt('prompt_optimizer')
AGENT_DETECTOR = load_prompt('agent_detector')

model = genai.GenerativeModel('gemini-2.0-flash')

def add_query_to_agents(agents_data, user_query):
    """
    Add query parameters to agent URLs for frontend convenience
    
    Args:
        agents_data: Response from finder service with agents
        user_query: Original user query to add as parameter
        
    Returns:
        Modified agents data with query parameters added to URLs
    """
    if not isinstance(agents_data, dict) or 'agents' not in agents_data:
        return agents_data
    
    modified_agents = []
    
    for agent in agents_data.get('agents', []):
        # Create a copy of the agent
        modified_agent = agent.copy()
        
        # Add query parameter to the resource URL
        resource = agent.get('resource', '')
        if resource and user_query:
            # Add query parameter to URL
            query_params = {'query': user_query}
            if '?' in resource:
                # URL already has parameters
                resource_with_query = f"{resource}&{urlencode(query_params)}"
            else:
                # Clean URL, add query parameter
                resource_with_query = f"{resource}?{urlencode(query_params)}"
            
            modified_agent['resource'] = resource_with_query
        
        modified_agents.append(modified_agent)
    
    # Return modified data
    result = agents_data.copy()
    result['agents'] = modified_agents
    return result

class ChatMessage(BaseModel):
    message: str

@app.get("/")
async def root():
    return {
        "message": "AI Chat Bot API is running",
        "status": "healthy",
        "service": "ai_chat_backend",
        "version": "1.0.0",
        "endpoints": ["/api/chat"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat(chat_message: ChatMessage):
    if not chat_message.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Step 1: Generate response to user
        full_prompt = SYSTEM_PROMPT + "\n\nUser: " + chat_message.message
        chat_response = model.generate_content(full_prompt)
        user_response = chat_response.text
        
        # Step 2: Check if we need to search for agents
        agent_check_prompt = AGENT_DETECTOR + "\n\n" + chat_message.message
        agent_check_response = model.generate_content(agent_check_prompt)
        needs_agents = agent_check_response.text.strip().upper() == "YES"
        
        response_data = {
            "response": user_response,
            "needs_agents": needs_agents
        }
        
        # Step 3: If agents needed, search for them
        if needs_agents:
            try:
                # Optimize prompt for agent search
                optimize_prompt = PROMPT_OPTIMIZER + "\n\n" + chat_message.message
                optimization_response = model.generate_content(optimize_prompt)
                short_prompt = optimization_response.text.strip()
                
                # Search for agents
                search_payload = {
                    "prompt": short_prompt,
                    "max_results": 10,
                    "min_rating": 0.8
                }
                
                search_response = requests.post(
                    'https://aifinder-production.up.railway.app/search',
                    json=search_payload,
                    headers={'Content-Type': 'application/json', 'accept': 'application/json'},
                    timeout=10
                )
                
                if search_response.status_code == 200:
                    agents_data = search_response.json()
                    
                    # Add query parameters to agent URLs for frontend convenience
                    agents_with_query = add_query_to_agents(agents_data, chat_message.message)
                    
                    response_data.update({
                        "optimized_prompt": short_prompt,
                        "agents_found": len(agents_data.get('agents', [])),
                        "agents": agents_with_query
                    })
                else:
                    response_data["agent_search_error"] = f"Search failed: {search_response.status_code}"
                    
            except requests.exceptions.Timeout:
                response_data["agent_search_error"] = "Agent search timeout"
            except requests.exceptions.ConnectionError:
                response_data["agent_search_error"] = "Agent search service unavailable"
            except Exception as e:
                response_data["agent_search_error"] = f"Agent search error: {str(e)}"
        
        return response_data
        
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
