import json
import re
from typing import List, Dict
from bazaar_scout import BazaarScout

class AIAgentFinder:
    """AI агент для поиска подходящих x402 агентов по промпту"""
    
    def __init__(self):
        self.scout = BazaarScout()
        self.agents_cache = None
        
    def load_agents(self):
        """Загружает и кэширует список агентов"""
        if self.agents_cache is None:
            print("🔄 Загружаем агентов из Bazaar...")
            data = self.scout.get_all_agents()
            if data and 'items' in data:
                # Фильтруем только агентов с описанием
                self.agents_cache = [
                    agent for agent in data['items']
                    if self._has_description(agent)
                ]
                print(f"✅ Загружено {len(self.agents_cache)} агентов с описанием")
            else:
                self.agents_cache = []
                print("❌ Не удалось загрузить агентов")
        return self.agents_cache
    
    def _has_description(self, agent):
        """Проверяет есть ли описание у агента"""
        accepts = agent.get('accepts', [])
        if not accepts:
            return False
            
        description = accepts[0].get('description', '').strip()
        return len(description) > 0
    
    def find_agents_by_prompt(self, prompt: str) -> List[Dict]:
        """Находит агентов по промпту пользователя"""
        agents = self.load_agents()
        if not agents:
            return []
        
        # Извлекаем ключевые слова из промпта
        keywords = self._extract_keywords(prompt.lower())
        
        # Ищем подходящих агентов
        matching_agents = []
        for agent in agents:
            score = self._calculate_match_score(agent, keywords, prompt.lower())
            if score > 0:
                agent_info = self._format_agent_info(agent, score)
                matching_agents.append(agent_info)
        
        # Сортируем по релевантности
        matching_agents.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return matching_agents
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """Извлекает ключевые слова из промпта"""
        # Убираем стоп-слова и извлекаем значимые слова
        stop_words = {'и', 'или', 'но', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'из', 'к', 'о', 'а', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Извлекаем слова
        words = re.findall(r'\b\w+\b', prompt)
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def _calculate_match_score(self, agent: Dict, keywords: List[str], prompt: str) -> float:
        """Вычисляет релевантность агента промпту"""
        score = 0.0
        
        accepts = agent.get('accepts', [{}])[0]
        resource = agent.get('resource', '').lower()
        description = accepts.get('description', '').lower()
        
        # Прямое совпадение в описании
        for keyword in keywords:
            if keyword in description:
                score += 3.0
            if keyword in resource:
                score += 2.0
        
        # Проверяем семантические совпадения
        semantic_matches = self._check_semantic_matches(prompt, description, resource)
        score += semantic_matches
        
        return score
    
    def _check_semantic_matches(self, prompt: str, description: str, resource: str) -> float:
        """Проверяет семантические совпадения"""
        score = 0.0
        
        # Категории и их ключевые слова
        categories = {
            'search': ['поиск', 'найти', 'search', 'find', 'exa', 'google'],
            'weather': ['погода', 'weather', 'температура', 'climate'],
            'finance': ['цены', 'акции', 'stock', 'price', 'trading', 'финансы', 'деньги'],
            'ai': ['генерация', 'ai', 'generation', 'model', 'gpt', 'llm', 'машинное обучение'],
            'code': ['код', 'code', 'programming', 'e2b', 'execution', 'run'],
            'image': ['изображение', 'image', 'picture', 'photo', 'visual'],
            'video': ['видео', 'video', 'remix', 'movie'],
            'memory': ['память', 'memory', 'storage', 'save', 'remember'],
            'data': ['данные', 'data', 'analysis', 'analytics', 'информация']
        }
        
        for category, category_keywords in categories.items():
            prompt_matches = sum(1 for word in category_keywords if word in prompt)
            desc_matches = sum(1 for word in category_keywords if word in description)
            resource_matches = sum(1 for word in category_keywords if word in resource)
            
            if prompt_matches > 0 and (desc_matches > 0 or resource_matches > 0):
                score += 2.0 * prompt_matches
        
        return score
    
    def _format_agent_info(self, agent: Dict, score: float) -> Dict:
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
            'relevance_score': round(score, 2)
        }
    
    def search_and_display(self, prompt: str):
        """Ищет и красиво отображает результаты"""
        print(f"🔍 Ищу агентов для: '{prompt}'\n")
        
        matching_agents = self.find_agents_by_prompt(prompt)
        
        if not matching_agents:
            print("❌ Не найдено подходящих агентов с описанием")
            return
        
        print(f"✅ Найдено {len(matching_agents)} подходящих агентов:\n")
        
        for i, agent in enumerate(matching_agents[:10], 1):  # Показываем топ-10
            print(f"🤖 #{i} | Релевантность: {agent['relevance_score']}")
            print(f"📡 Ресурс: {agent['resource']}")
            print(f"📝 Описание: {agent['description']}")
            print(f"💰 Цена: {agent['price_usdc']} USDC")
            print(f"🌍 Сеть: {agent['network']}")
            print(f"⏱️  Таймаут: {agent['timeout_seconds']}s")
            print(f"💳 Адрес оплаты: {agent['pay_to_address']}")
            print(f"🕐 Обновлен: {agent['last_updated']}")
            print("-" * 80)
    
    def get_json_results(self, prompt: str) -> str:
        """Возвращает результаты в JSON формате"""
        matching_agents = self.find_agents_by_prompt(prompt)
        
        result = {
            'query': prompt,
            'found_agents': len(matching_agents),
            'agents': matching_agents[:10]  # Топ-10
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

def main():
    print("🤖 AI Agent Finder для x402 Bazaar")
    print("=" * 50)
    
    finder = AIAgentFinder()
    
    # Примеры поиска
    test_queries = [
        "найти информацию в интернете",
        "узнать погоду",
        "цены на акции",
        "генерация видео",
        "выполнить код python",
        "поиск в github"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        finder.search_and_display(query)
        print(f"{'='*60}")
    
    # Интерактивный режим
    print("\n🎯 Интерактивный режим:")
    while True:
        try:
            user_prompt = input("\n💬 Введите ваш запрос (или 'exit' для выхода): ").strip()
            
            if user_prompt.lower() in ['exit', 'quit', 'выход']:
                print("👋 До свидания!")
                break
            
            if user_prompt:
                finder.search_and_display(user_prompt)
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break

if __name__ == "__main__":
    main()
