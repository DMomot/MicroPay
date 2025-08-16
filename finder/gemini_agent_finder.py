import json
import os
import time
from typing import List, Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from bazaar_scout import BazaarScout

load_dotenv()

class GeminiAgentFinder:
    """AI agent with Gemini for smart x402 agent search by prompt"""
    
    def __init__(self, min_rating: float = 0.5, refresh_interval_minutes: int = 60):
        self.scout = BazaarScout()
        self.agents_cache = None
        self.cache_timestamp = 0  # Last cache update timestamp
        self.min_rating = min_rating  # Minimum rating for inclusion
        self.refresh_interval = refresh_interval_minutes * 60  # Convert to seconds
        
        # Gemini setup
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def load_agents(self):
        """Loads and caches agent list with refresh time check"""
        current_time = time.time()
        
        # Check if cache needs refresh
        if (self.agents_cache is None or 
            current_time - self.cache_timestamp > self.refresh_interval):
            
            print(f"🔄 Loading agents from Bazaar... (interval: {self.refresh_interval//60} min)")
            data = self.scout.get_all_agents()
            if data and 'items' in data:
                # Filter only agents with description
                self.agents_cache = [
                    agent for agent in data['items']
                    if self._has_description(agent)
                ]
                self.cache_timestamp = current_time
                print(f"✅ Loaded {len(self.agents_cache)} agents with description")
            else:
                self.agents_cache = []
                print("❌ Failed to load agents")
        else:
            remaining_time = int((self.refresh_interval - (current_time - self.cache_timestamp)) / 60)
            print(f"📋 Using cached agents (refresh in {remaining_time} min)")
            
        return self.agents_cache
    
    def _has_description(self, agent):
        """Check if agent has description"""
        accepts = agent.get('accepts', [])
        if not accepts:
            return False
            
        description = accepts[0].get('description', '').strip()
        return len(description) > 0
    
    def find_agents_by_prompt(self, prompt: str) -> List[Dict]:
        """Find agents by prompt using Gemini"""
        agents = self.load_agents()
        if not agents:
            return []
        
        print(f"🧠 Analyzing prompt with Gemini: '{prompt}'")
        
        # Analyze each agent with Gemini
        matching_agents = []
        for i, agent in enumerate(agents):
            print(f"🔍 Analyzing agent {i+1}/{len(agents)}", end='\r')
            
            rating = self._rate_agent_with_gemini(agent, prompt)
            
            if rating >= self.min_rating:
                agent_info = self._format_agent_info(agent, rating)
                matching_agents.append(agent_info)
        
        print(f"\n✅ Found {len(matching_agents)} agents with rating >= {self.min_rating}")
        
        # Sort by rating
        matching_agents.sort(key=lambda x: x['rating'], reverse=True)
        
        return matching_agents
    
    def _rate_agent_with_gemini(self, agent: Dict, prompt: str) -> float:
        """Rate agent relevance to prompt using Gemini"""
        try:
            accepts = agent.get('accepts', [{}])[0]
            resource = agent.get('resource', '')
            description = accepts.get('description', '')
            
            # Create prompt for Gemini with reasoning request
            analysis_prompt = f"""
Analyze how well this x402 agent matches the user request.

USER REQUEST: "{prompt}"

AGENT:
- Resource: {resource}
- Description: {description}

TASK:
Rate from 0.0 to 1.0 how well this agent fits the user request.
ALSO provide your reasoning.

RATING CRITERIA:
- 1.0 = Perfect match, will definitely complete the task
- 0.8-0.9 = Very good match
- 0.6-0.7 = Good match, but some nuances
- 0.4-0.5 = Partial match
- 0.1-0.3 = Weak match
- 0.0 = No match at all

Consider:
- Semantic correspondence between agent functionality and request
- Keywords in description
- Task type (search, generation, analysis, API, etc.)

RESPONSE FORMAT:
REASONING: [explain your analysis in 1-2 sentences]
RATING: [number from 0.0 to 1.0]
"""
            
            response = self.model.generate_content(analysis_prompt)
            response_text = response.text.strip()
            
            # Parse reasoning and rating from response
            try:
                reasoning = ""
                rating = 0.0
                
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('REASONING:'):
                        reasoning = line.replace('REASONING:', '').strip()
                    elif line.startswith('RATING:'):
                        rating_str = line.replace('RATING:', '').strip()
                        rating = float(rating_str)
                
                # Limit rating to 0-1 range
                rating = max(0.0, min(1.0, rating))
                
                # Print reasoning to console
                if rating >= self.min_rating:
                    print(f"🤖 {resource}")
                    print(f"   💭 Reasoning: {reasoning}")
                    print(f"   ⭐ Rating: {rating}")
                
                return rating
                
            except ValueError:
                # If parsing fails, try to extract just the number
                try:
                    # Look for any number in the response
                    import re
                    numbers = re.findall(r'(\d+\.?\d*)', response_text)
                    if numbers:
                        rating = float(numbers[-1])  # Take the last number found
                        rating = max(0.0, min(1.0, rating))
                        if rating >= self.min_rating:
                            print(f"🤖 {resource} - Rating: {rating} (parsing fallback)")
                        return rating
                except:
                    pass
                
                print(f"⚠️ Could not parse rating from: {response_text}")
                return 0.0
                
        except Exception as e:
            print(f"❌ Error analyzing with Gemini: {e}")
            return 0.0
    
    def _format_agent_info(self, agent: Dict, rating: float) -> Dict:
        """Format agent information"""
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
            'rating': round(rating, 3)  # Rating from 0 to 1
        }
    
    def search_and_display(self, prompt: str, show_details: bool = True):
        """Search and display results beautifully"""
        print(f"🔍 Searching agents for: '{prompt}'")
        print(f"📊 Minimum rating: {self.min_rating}\n")
        
        matching_agents = self.find_agents_by_prompt(prompt)
        
        if not matching_agents:
            print(f"❌ No agents found with rating >= {self.min_rating}")
            return
        
        print(f"\n✅ Found {len(matching_agents)} suitable agents:\n")
        
        for i, agent in enumerate(matching_agents[:10], 1):  # Show top-10
            # Эмодзи по рейтингу
            if agent['rating'] >= 0.9:
                emoji = "🌟"
            elif agent['rating'] >= 0.7:
                emoji = "🔥"
            elif agent['rating'] >= 0.5:
                emoji = "✅"
            else:
                emoji = "⚠️"
            
            print(f"{emoji} #{i} | Rating: {agent['rating']}")
            print(f"📡 Resource: {agent['resource']}")
            print(f"📝 Description: {agent['description']}")
            
            if show_details:
                print(f"💰 Price: {agent['price_usdc']} USDC")
                print(f"🌍 Network: {agent['network']}")
                print(f"⏱️  Timeout: {agent['timeout_seconds']}s")
                print(f"💳 Payment address: {agent['pay_to_address']}")
                print(f"🕐 Updated: {agent['last_updated']}")
            
            print("-" * 80)
    
    def get_top_agents(self, prompt: str, limit: int = 5) -> List[Dict]:
        """Returns top agents with high rating"""
        matching_agents = self.find_agents_by_prompt(prompt)
        return matching_agents[:limit]
    
    def set_min_rating(self, min_rating: float):
        """Set minimum rating for filtering"""
        self.min_rating = max(0.0, min(1.0, min_rating))
        print(f"📊 Minimum rating set: {self.min_rating}")
    

    
    def get_rating_stats(self, prompt: str) -> Dict:
        """Get rating statistics for all agents"""
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
