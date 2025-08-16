from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from gemini_agent_finder import GeminiAgentFinder
import uvicorn

app = FastAPI(
    title="ScoutPay AI Agent Finder API",
    description="API для поиска x402 агентов по промпту",
    version="1.0.0"
)

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем Gemini AI агента
try:
    import os
    refresh_interval = int(os.getenv('AGENTS_REFRESH_INTERVAL_MINUTES', '60'))
    finder = GeminiAgentFinder(min_rating=0.5, refresh_interval_minutes=refresh_interval)
except ValueError as e:
    print(f"❌ Ошибка инициализации Gemini: {e}")
    print("💡 Убедитесь что GEMINI_API_KEY установлен в .env файле")
    finder = None

class SearchRequest(BaseModel):
    prompt: str
    max_results: Optional[int] = 10
    min_rating: Optional[float] = 0.5

class AgentInfo(BaseModel):
    resource: str
    description: str
    price_usdc: str
    network: str
    timeout_seconds: int
    asset_address: str
    pay_to_address: str
    last_updated: str
    rating: float  # Рейтинг от 0 до 1

class SearchResponse(BaseModel):
    query: str
    found_agents: int
    agents: List[AgentInfo]
    status: str

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "ScoutPay AI Agent Finder API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search",
            "health": "/health", 
            "agents": "/agents/all"
        }
    }

@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini не инициализирован. Проверьте GEMINI_API_KEY")
    
    try:
        # Проверяем что можем загрузить агентов
        agents = finder.load_agents()
        return {
            "status": "healthy",
            "agents_loaded": len(agents),
            "min_rating": finder.min_rating,
            "message": "API работает нормально"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API недоступен: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_agents(request: SearchRequest):
    """Поиск агентов по промпту с Gemini"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini не инициализирован")
    
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Промпт не может быть пустым")
        
        # Устанавливаем минимальный рейтинг если передан
        original_min_rating = finder.min_rating
        if request.min_rating is not None:
            finder.set_min_rating(request.min_rating)
        
        # Поиск агентов с Gemini
        matching_agents = finder.find_agents_by_prompt(request.prompt)
        
        # Восстанавливаем оригинальный рейтинг
        finder.min_rating = original_min_rating
        
        # Ограничиваем количество результатов
        limited_agents = matching_agents[:request.max_results]
        
        return SearchResponse(
            query=request.prompt,
            found_agents=len(matching_agents),
            agents=[AgentInfo(**agent) for agent in limited_agents],
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")

@app.get("/agents/all")
async def get_all_agents():
    """Получить всех агентов с описанием"""
    try:
        agents = finder.load_agents()
        
        formatted_agents = []
        for agent in agents:
            agent_info = finder._format_agent_info(agent, 0.0)
            formatted_agents.append(agent_info)
        
        return {
            "total_agents": len(formatted_agents),
            "agents": formatted_agents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки агентов: {str(e)}")

@app.get("/categories")
async def get_categories():
    """Получить доступные категории агентов"""
    try:
        agents = finder.load_agents()
        
        # Группируем по доменам
        categories = {}
        for agent in agents:
            resource = agent.get('resource', '')
            if '://' in resource:
                domain = resource.split('/')[2]
                if domain not in categories:
                    categories[domain] = 0
                categories[domain] += 1
        
        return {
            "categories": categories,
            "total_domains": len(categories)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки категорий: {str(e)}")

@app.get("/search/examples")
async def get_search_examples():
    """Примеры поисковых запросов"""
    return {
        "examples": [
            "найти информацию в интернете",
            "узнать погоду в Москве", 
            "цены на акции Apple",
            "генерация видео с картинкой",
            "выполнить код Python",
            "поиск репозиториев на GitHub",
            "получить данные о криптовалюте",
            "анализ текста с помощью AI",
            "создать изображение",
            "сохранить данные в память"
        ]
    }

@app.post("/rating/stats")
async def get_rating_stats(request: SearchRequest):
    """Получить статистику рейтингов для запроса"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini не инициализирован")
    
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Промпт не может быть пустым")
        
        stats = finder.get_rating_stats(request.prompt)
        return {
            "query": request.prompt,
            "stats": stats,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

@app.post("/rating/threshold")
async def update_rating_threshold(min_rating: float):
    """Обновить минимальный рейтинг"""
    if finder is None:
        raise HTTPException(status_code=500, detail="Gemini не инициализирован")
    
    if not (0.0 <= min_rating <= 1.0):
        raise HTTPException(status_code=400, detail="Рейтинг должен быть от 0.0 до 1.0")
    
    finder.set_min_rating(min_rating)
    return {
        "min_rating": finder.min_rating,
        "message": f"Минимальный рейтинг установлен: {finder.min_rating}"
    }



if __name__ == "__main__":
    print("🚀 Запускаем ScoutPay AI Agent Finder API...")
    print("📡 API будет доступен на http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
