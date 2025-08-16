import requests
import json
import time
from jwt_generator import generate_jwt

class BazaarScout:
    """Сканер x402 Bazaar для поиска доступных AI моделей и сервисов"""
    
    def __init__(self):
        self.base_url = "https://api.cdp.coinbase.com"
        self.discovery_endpoint = "/platform/v2/x402/discovery/resources"
        
    def get_all_agents(self):
        """Получает список всех агентов из x402 Bazaar"""
        try:
            jwt_token = generate_jwt(self.discovery_endpoint)
            
            headers = {
                "Authorization": f"Bearer {jwt_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}{self.discovery_endpoint}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка при запросе: {e}")
            return None
    
    def analyze_agents(self, data):
        """Анализирует полученные данные о агентах"""
        if not data or 'items' not in data:
            print("❌ Нет данных для анализа")
            return
            
        agents = data['items']
        print(f"🔍 Найдено агентов: {len(agents)}")
        print(f"📊 Общая информация: {data.get('pagination', {})}")
        print(f"🔗 x402 версия: {data.get('x402Version', 'N/A')}\n")
        
        # Группировка по типам сервисов
        services = {}
        for agent in agents:
            resource = agent.get('resource', 'Unknown')
            domain = resource.split('/')[2] if '://' in resource else 'Unknown'
            
            if domain not in services:
                services[domain] = []
            services[domain].append(agent)
        
        # Вывод анализа
        for domain, domain_agents in services.items():
            print(f"🌐 {domain} ({len(domain_agents)} сервисов):")
            for agent in domain_agents:
                self.print_agent_info(agent)
            print()
    
    def print_agent_info(self, agent):
        """Выводит информацию об агенте"""
        resource = agent.get('resource', 'N/A')
        accepts = agent.get('accepts', [])
        last_updated = agent.get('lastUpdated', 'N/A')
        
        print(f"  📡 {resource}")
        
        if accepts:
            accept = accepts[0]  # Берем первый accept
            max_amount = accept.get('maxAmountRequired', 'N/A')
            timeout = accept.get('maxTimeoutSeconds', 'N/A')
            network = accept.get('network', 'N/A')
            asset = accept.get('asset', 'N/A')
            description = accept.get('description', 'N/A')
            
            print(f"    💰 Цена: {max_amount} USDC")
            print(f"    ⏱️  Таймаут: {timeout}s")
            print(f"    🌍 Сеть: {network}")
            if description:
                print(f"    📝 Описание: {description}")
        
        print(f"    🕐 Обновлен: {last_updated}")
    
    def find_ai_models(self, data):
        """Ищет специфически AI модели среди агентов"""
        if not data or 'items' not in data:
            return []
            
        ai_keywords = ['ai', 'ml', 'model', 'gpt', 'llm', 'generation', 'analysis', 'prediction']
        ai_agents = []
        
        for agent in data['items']:
            resource = agent.get('resource', '').lower()
            description = agent.get('accepts', [{}])[0].get('description', '').lower()
            
            if any(keyword in resource or keyword in description for keyword in ai_keywords):
                ai_agents.append(agent)
        
        return ai_agents
    
    def save_results(self, data, filename="bazaar_agents.json"):
        """Сохраняет результаты в JSON файл с фильтрацией запрещённых агентов"""
        
        # Чёрный список запрещённых URL
        blacklisted_urls = [
            "https://scoutpay-production.up.railway.app/api/prices",
            "scoutpay-production.up.railway.app"
        ]
        
        # Фильтруем агентов
        if data and 'items' in data:
            original_count = len(data['items'])
            filtered_items = []
            
            for agent in data['items']:
                resource = agent.get('resource', '')
                
                # Проверяем, не находится ли агент в чёрном списке
                is_blacklisted = any(blacklisted_url in resource for blacklisted_url in blacklisted_urls)
                
                if not is_blacklisted:
                    filtered_items.append(agent)
                else:
                    print(f"🚫 Заблокирован агент: {resource}")
            
            data['items'] = filtered_items
            
            # Обновляем счётчик
            if 'pagination' in data:
                data['pagination']['total'] = len(filtered_items)
            
            blocked_count = original_count - len(filtered_items)
            if blocked_count > 0:
                print(f"🚫 Заблокировано агентов: {blocked_count}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Результаты сохранены в {filename}")

def main():
    print("🔍 ScoutPay Bazaar Scout - поиск AI моделей в x402 Bazaar\n")
    
    scout = BazaarScout()
    
    # Получаем данные
    print("📡 Получаем список агентов...")
    data = scout.get_all_agents()
    
    if data:
        # Анализируем
        print("📊 Анализируем агентов...\n")
        scout.analyze_agents(data)
        
        # Ищем AI модели
        ai_agents = scout.find_ai_models(data)
        if ai_agents:
            print(f"\n🤖 Найдено AI моделей: {len(ai_agents)}")
            for agent in ai_agents:
                scout.print_agent_info(agent)
        
        # Сохраняем результаты
        scout.save_results(data)
        
        print(f"\n✅ Сканирование завершено!")
    else:
        print("❌ Не удалось получить данные из Bazaar")

if __name__ == "__main__":
    main()
