"""
Утилиты для создания nonce для EIP3009 с информацией о destination chain и address
"""

import secrets
import struct

def create_cctp_nonce(destination_domain: int, destination_address: str) -> bytes:
    """
    Создает 32-байтовый nonce для CCTP трансфера
    
    Структура nonce (32 байта):
    - 4 байта: destination domain (uint32)
    - 20 байт: destination address (address)
    - 8 байт: случайные данные
    
    Args:
        destination_domain: CCTP domain ID (0 = Ethereum, 1 = Avalanche, 2 = Optimism, 3 = Arbitrum, 6 = Base, 7 = Polygon)
        destination_address: Адрес получателя в destination chain
    
    Returns:
        bytes: 32-байтовый nonce
    """
    
    # Убираем 0x префикс если есть
    if destination_address.startswith('0x'):
        destination_address = destination_address[2:]
    
    # Проверяем длину адреса
    if len(destination_address) != 40:
        raise ValueError(f"Invalid address length: {len(destination_address)}, expected 40")
    
    # 4 байта для domain (big-endian uint32)
    domain_bytes = struct.pack('>I', destination_domain)
    
    # 20 байт для address
    address_bytes = bytes.fromhex(destination_address)
    
    # 8 байт случайных данных
    random_bytes = secrets.token_bytes(8)
    
    # Собираем nonce
    nonce = domain_bytes + address_bytes + random_bytes
    
    return nonce

def parse_cctp_nonce(nonce: bytes) -> dict:
    """
    Парсит CCTP nonce и извлекает информацию
    
    Args:
        nonce: 32-байтовый nonce
    
    Returns:
        dict: Информация из nonce
    """
    
    if len(nonce) != 32:
        raise ValueError(f"Invalid nonce length: {len(nonce)}, expected 32")
    
    # Извлекаем domain (первые 4 байта)
    domain = struct.unpack('>I', nonce[:4])[0]
    
    # Извлекаем address (следующие 20 байт)
    address = '0x' + nonce[4:24].hex()
    
    # Извлекаем случайные данные (последние 8 байт)
    random_data = nonce[24:32].hex()
    
    return {
        'destination_domain': domain,
        'destination_address': address,
        'random_data': random_data
    }

def get_domain_name(domain_id: int) -> str:
    """Возвращает название сети по domain ID"""
    domain_names = {
        0: "Ethereum",
        1: "Avalanche", 
        2: "Optimism",
        3: "Arbitrum",
        6: "Base",
        7: "Polygon"
    }
    return domain_names.get(domain_id, f"Unknown ({domain_id})")

if __name__ == "__main__":
    # Тест
    print("🧪 ТЕСТ CCTP NONCE UTILS")
    print("=" * 40)
    
    # Создаем nonce для Ethereum
    destination_domain = 0  # Ethereum
    destination_address = "0x742d35Cc6634C0532925a3b8D5c9C5e3fBE5e1d4"
    
    nonce = create_cctp_nonce(destination_domain, destination_address)
    
    print(f"📋 Создан nonce:")
    print(f"  Destination Domain: {destination_domain} ({get_domain_name(destination_domain)})")
    print(f"  Destination Address: {destination_address}")
    print(f"  Nonce (hex): 0x{nonce.hex()}")
    print(f"  Nonce length: {len(nonce)} bytes")
    
    # Парсим обратно
    parsed = parse_cctp_nonce(nonce)
    print(f"\n🔍 Парсинг nonce:")
    print(f"  Domain: {parsed['destination_domain']} ({get_domain_name(parsed['destination_domain'])})")
    print(f"  Address: {parsed['destination_address']}")
    print(f"  Random: {parsed['random_data']}")
    
    # Проверяем совпадение
    match = (parsed['destination_domain'] == destination_domain and 
             parsed['destination_address'].lower() == destination_address.lower())
    print(f"  ✅ Совпадение: {match}")
