import json
import os
import time
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from bazaar_scout import BazaarScout

load_dotenv()

class GeminiAgentFinder:
    """AI агент с Gemini для умного поиска x402 агентов по промпту"""
    
    def __init__(self, min_rating: float = 0.5, refresh_interval_minutes: int = 60):
        self.scout = BazaarScout()
        self.agents_cache = None
        self.cache_timestamp = 0  # Время последнего обновления кэша
        self.min_rating = min_rating  # Минимальный рейтинг для попадания в выборку
        self.refresh_interval = refresh_interval_minutes * 60  # Конвертируем в секунды
        
        # Настройка Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY не найден в переменных окружения!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def load_agents(self):
        """Загружает и кэширует список агентов с проверкой времени обновления"""
        current_time = time.time()
        
        # Проверяем нужно ли обновить кэш
        if (self.agents_cache is None or 
            current_time - self.cache_timestamp > self.refresh_interval):
            
            print(f"🔄 Загружаем агентов из Bazaar... (интервал: {self.refresh_interval//60} мин)")
            data = self.scout.get_all_agents()
            if data and 'items' in data:
                # Фильтруем только агентов с описанием
                self.agents_cache = [
                    agent for agent in data['items']
                    if self._has_description(agent)
                ]
                self.cache_timestamp = current_time
                print(f"✅ Загружено {len(self.agents_cache)} агентов с описанием")
            else:
                self.agents_cache = []
                print("❌ Не удалось загрузить агентов")
        else:
            remaining_time = int((self.refresh_interval - (current_time - self.cache_timestamp)) / 60)
            print(f"📋 Используем кэш агентов (обновление через {remaining_time} мин)")
            
        return self.agents_cache
    
    def _has_description(self, agent):
        """Проверяет есть ли описание у агента"""
        accepts = agent.get('accepts', [])
        if not accepts:
            return False
            
        description = accepts[0].get('description', '').strip()
        return len(description) > 0
    
    def find_agents_by_prompt(self, prompt: str) -> List[Dict]:
        """Находит агентов по промпту с помощью Gemini"""
        agents = self.load_agents()
        if not agents:
            return []
        
        print(f"🧠 Анализируем промпт с Gemini: '{prompt}'")
        
        # Анализируем каждого агента с помощью Gemini
        matching_agents = []
        for i, agent in enumerate(agents):
            print(f"🔍 Анализируем агента {i+1}/{len(agents)}", end='\r')
            
            rating = self._rate_agent_with_gemini(agent, prompt)
            
            if rating >= self.min_rating:
                agent_info = self._format_agent_info(agent, rating)
                matching_agents.append(agent_info)
        
        print(f"\n✅ Найдено {len(matching_agents)} агентов с рейтингом >= {self.min_rating}")
        
        # Сортируем по рейтингу
        matching_agents.sort(key=lambda x: x['rating'], reverse=True)
        
        return matching_agents
    
    def _rate_agent_with_gemini(self, agent: Dict, prompt: str) -> float:
        """Оценивает соответствие агента промпту с помощью Gemini"""
        try:
            accepts = agent.get('accepts', [{}])[0]
            resource = agent.get('resource', '')
            description = accepts.get('description', '')
            
            # Создаем промпт для Gemini
            analysis_prompt = f"""
Анализируй насколько подходит этот x402 агент для запроса пользователя.

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: "{prompt}"

АГЕНТ:
- Ресурс: {resource}
- Описание: {description}

ЗАДАЧА:
Оцени от 0.0 до 1.0 насколько этот агент подходит для выполнения запроса пользователя.

КРИТЕРИИ ОЦЕНКИ:
- 1.0 = Идеально подходит, точно выполнит задачу
- 0.8-0.9 = Очень хорошо подходит
- 0.6-0.7 = Хорошо подходит, но есть нюансы  
- 0.4-0.5 = Частично подходит
- 0.1-0.3 = Слабо подходит
- 0.0 = Совсем не подходит

Учитывай:
- Семантическое соответствие функционала агента и запроса
- Ключевые слова в описании
- Тип задачи (поиск, генерация, анализ, API и т.д.)

ОТВЕТ: только число от 0.0 до 1.0, ничего больше.
"""
            
            response = self.model.generate_content(analysis_prompt)
            rating_text = response.text.strip()
            
            # Извлекаем число из ответа
            try:
                rating = float(rating_text)
                # Ограничиваем диапазон 0-1
                rating = max(0.0, min(1.0, rating))
                return rating
            except ValueError:
                # Если не смогли распарсить, возвращаем 0
                print(f"⚠️ Не удалось распарсить рейтинг: {rating_text}")
                return 0.0
                
        except Exception as e:
            print(f"❌ Ошибка анализа с Gemini: {e}")
            return 0.0
    
    def _format_agent_info(self, agent: Dict, rating: float) -> Dict:
        """Форматирует информацию об агенте"""
        accepts = agent.get('accepts', [{}])[0]
        
        return {
            'resource': agent.get('resource'),
            'description': accepts.get('description'),
            'price_usdc': accepts.get('maxAmountRequired'),
            'network': accepts.get('network'),
            'timeout_seconds': accepts.get('maxTimeoutSeconds'),
            'asset_address': accepts.get('asset'),
            'pay_to_address': accepts.get('payTo'),
            'last_updated': agent.get('lastUpdated'),
            'rating': round(rating, 3)  # Рейтинг от 0 до 1
        }
    
    def search_and_display(self, prompt: str, show_details: bool = True):
        """Ищет и красиво отображает результаты"""
        print(f"🔍 Ищу агентов для: '{prompt}'")
        print(f"📊 Минимальный рейтинг: {self.min_rating}\n")
        
        matching_agents = self.find_agents_by_prompt(prompt)
        
        if not matching_agents:
            print(f"❌ Не найдено агентов с рейтингом >= {self.min_rating}")
            return
        
        print(f"\n✅ Найдено {len(matching_agents)} подходящих агентов:\n")
        
        for i, agent in enumerate(matching_agents[:10], 1):  # Показываем топ-10
            # Эмодзи по рейтингу
            if agent['rating'] >= 0.9:
                emoji = "🌟"
            elif agent['rating'] >= 0.7:
                emoji = "🔥"
            elif agent['rating'] >= 0.5:
                emoji = "✅"
            else:
                emoji = "⚠️"
            
            print(f"{emoji} #{i} | Рейтинг: {agent['rating']}")
            print(f"📡 Ресурс: {agent['resource']}")
            print(f"📝 Описание: {agent['description']}")
            
            if show_details:
                print(f"💰 Цена: {agent['price_usdc']} USDC")
                print(f"🌍 Сеть: {agent['network']}")
                print(f"⏱️  Таймаут: {agent['timeout_seconds']}s")
                print(f"💳 Адрес оплаты: {agent['pay_to_address']}")
                print(f"🕐 Обновлен: {agent['last_updated']}")
            
            print("-" * 80)
    
    def get_top_agents(self, prompt: str, limit: int = 5) -> List[Dict]:
        """Возвращает топ агентов с высоким рейтингом"""
        matching_agents = self.find_agents_by_prompt(prompt)
        return matching_agents[:limit]
    
    def set_min_rating(self, min_rating: float):
        """Устанавливает минимальный рейтинг для фильтрации"""
        self.min_rating = max(0.0, min(1.0, min_rating))
        print(f"📊 Минимальный рейтинг установлен: {self.min_rating}")
    

    
    def get_rating_stats(self, prompt: str) -> Dict:
        """Получает статистику рейтингов для всех агентов"""
        agents = self.load_agents()
        if not agents:
            return {}
        
        print(f"📊 Анализируем все агенты для: '{prompt}'")
        
        ratings = []
        for i, agent in enumerate(agents):
            print(f"🔍 Анализируем {i+1}/{len(agents)}", end='\r')
            rating = self._rate_agent_with_gemini(agent, prompt)
            ratings.append(rating)
        
        print(f"\n📈 Статистика рейтингов:")
        
        stats = {
            'total_agents': len(ratings),
            'avg_rating': round(sum(ratings) / len(ratings), 3),
            'max_rating': round(max(ratings), 3),
            'min_rating': round(min(ratings), 3),
            'above_threshold': len([r for r in ratings if r >= self.min_rating]),
            'rating_distribution': {
                'excellent (0.9-1.0)': len([r for r in ratings if r >= 0.9]),
                'good (0.7-0.9)': len([r for r in ratings if 0.7 <= r < 0.9]),
                'ok (0.5-0.7)': len([r for r in ratings if 0.5 <= r < 0.7]),
                'poor (0.3-0.5)': len([r for r in ratings if 0.3 <= r < 0.5]),
                'bad (0.0-0.3)': len([r for r in ratings if r < 0.3]),
            }
        }
        
        for key, value in stats.items():
            if key != 'rating_distribution':
                print(f"  {key}: {value}")
        
        print(f"  Распределение рейтингов:")
        for category, count in stats['rating_distribution'].items():
            print(f"    {category}: {count}")
        
        return stats

def main():
    print("🤖 Gemini AI Agent Finder для x402 Bazaar")
    print("=" * 50)
    
    try:
        # Интервал обновления из переменной окружения (по умолчанию 60 минут)
        refresh_interval = int(os.getenv('AGENTS_REFRESH_INTERVAL_MINUTES', '60'))
        finder = GeminiAgentFinder(min_rating=0.5, refresh_interval_minutes=refresh_interval)
        
        # Примеры поиска
        test_queries = [
            "найти информацию в интернете",
            "узнать погоду в Москве",
            "получить цены на акции Tesla",
            "сгенерировать видео с картинкой",
        ]
        
        for query in test_queries:
            print(f"\n{'='*60}")
            finder.search_and_display(query, show_details=False)
        
        # Интерактивный режим
        print(f"\n🎯 Интерактивный режим (минимальный рейтинг: {finder.min_rating}):")
        print("Команды: 'stats <запрос>' - статистика, 'threshold <число>' - изменить порог")
        
        while True:
            try:
                user_input = input("\n💬 Введите запрос (или 'exit'): ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'выход']:
                    print("👋 До свидания!")
                    break
                
                if user_input.startswith('stats '):
                    query = user_input[6:]
                    finder.get_rating_stats(query)
                    continue
                
                if user_input.startswith('threshold '):
                    try:
                        new_threshold = float(user_input[10:])
                        finder.set_min_rating(new_threshold)
                    except ValueError:
                        print("❌ Неверный формат числа")
                    continue
                
                if user_input:
                    finder.search_and_display(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
                
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("💡 Убедитесь что GEMINI_API_KEY установлен в .env файле")

if __name__ == "__main__":
    main()
