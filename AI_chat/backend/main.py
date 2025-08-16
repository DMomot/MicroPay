from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# import google.generativeai as genai
import os
from dotenv import load_dotenv

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
        return "Ты дружелюбный AI ассистент. Отвечай на русском языке."

SYSTEM_PROMPT = load_prompt()

model = genai.GenerativeModel('gemini-2.0-flash')

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
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    try:
        # Объединяем системный промпт с сообщением пользователя
        full_prompt = SYSTEM_PROMPT + "\n\nПользователь: " + chat_message.message
        response = model.generate_content(full_prompt)
        return {"response": response.text}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации ответа: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
