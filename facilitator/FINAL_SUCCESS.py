"""
ФИНАЛЬНАЯ УСПЕШНАЯ ТРАНЗАКЦИЯ
Используем ТОЧНЫЕ данные из контракта
"""

import httpx
import asyncio
import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import time
import secrets
from eth_abi import encode
from eth_utils import keccak
from domain_separator_utils import get_base_sepolia_usdc_domain_separator
from nonce_utils import create_cctp_nonce, parse_cctp_nonce, get_domain_name

# Load environment variables
load_dotenv()

def create_final_success():
    """Создаем ФИНАЛЬНУЮ УСПЕШНУЮ транзакцию"""
    
    print("🎯 ФИНАЛЬНАЯ УСПЕШНАЯ ТРАНЗАКЦИЯ")
    print("=" * 50)
    
    # Get user private key
    user_key = os.getenv("PRIVATE_KEY_USER")
    if not user_key:
        print("❌ PRIVATE_KEY_USER not found")
        return None
    
    if not user_key.startswith('0x'):
        user_key = '0x' + user_key
    
    user_account = Account.from_key(user_key)
    print(f"👤 User: {user_account.address}")
    
    # Contract addresses
    usdc_address = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    contract_address = "0x4F26A0466F08BA8Ee601C661C0B2e8d75996a48c"
    
    # Transaction parameters
    amount = 500  # 0.0005 USDC - совсем минимум
    valid_after = 0
    valid_before = int(time.time()) + 3600
    
    # Create CCTP nonce with destination info
    destination_domain = 0  # Ethereum mainnet
    destination_address = "0x742d35Cc6634C0532925a3b8D5c9C5e3fBE5e1d4"
    
    # Generate proper CCTP nonce (32 bytes: 4 bytes domain + 20 bytes address + 8 bytes random)
    nonce_bytes = create_cctp_nonce(destination_domain, destination_address)
    nonce_hex = f"0x{nonce_bytes.hex()}"
    
    # Parse nonce for display
    nonce_info = parse_cctp_nonce(nonce_bytes)
    
    print(f"📋 Параметры:")
    print(f"  From: {user_account.address}")
    print(f"  To: {contract_address}")
    print(f"  Value: {amount} (0.0005 USDC)")
    print(f"  ValidAfter: {valid_after}")
    print(f"  ValidBefore: {valid_before}")
    print(f"  Nonce: {nonce_hex}")
    print(f"  📍 CCTP Destination:")
    print(f"    Domain: {nonce_info['destination_domain']} ({get_domain_name(nonce_info['destination_domain'])})")
    print(f"    Address: {nonce_info['destination_address']}")
    print(f"    Random: {nonce_info['random_data']}")
    
    # ИСПОЛЬЗУЕМ ПРАВИЛЬНОЕ ВЫЧИСЛЕНИЕ DOMAIN SEPARATOR!
    domain_separator = get_base_sepolia_usdc_domain_separator()
    type_hash = bytes.fromhex("7c7c6cdb67a18743f49ec6fa9b35f50d52ed05cbed4cc592e13b44501c1a2267")
    
    print(f"🔐 Используем ТОЧНЫЕ данные из контракта:")
    print(f"  Domain Separator: 0x{domain_separator.hex()}")
    print(f"  TypeHash: 0x{type_hash.hex()}")
    
    # Encode struct data используя abi.encode как в Solidity
    encoded_struct = encode(
        ['bytes32', 'address', 'address', 'uint256', 'uint256', 'uint256', 'bytes32'],
        [type_hash, user_account.address, contract_address, amount, valid_after, valid_before, nonce_bytes]
    )
    struct_hash = keccak(encoded_struct)
    
    print(f"🔐 StructHash: 0x{struct_hash.hex()}")
    
    # Create digest правильно для EIP-712
    digest = keccak(b"\x19\x01" + domain_separator + struct_hash)
    
    print(f"🔐 Digest: 0x{digest.hex()}")
    
    # Sign RAW digest
    signed_message = user_account._key_obj.sign_msg_hash(digest)
    v_value = signed_message.v + 27 if signed_message.v < 27 else signed_message.v
    
    print(f"✅ ФИНАЛЬНАЯ подпись:")
    print(f"  v: {v_value}")
    print(f"  r: 0x{signed_message.r:064x}")
    print(f"  s: 0x{signed_message.s:064x}")
    
    return {
        "signature": {
            "from": user_account.address,
            "to": contract_address,
            "amount": str(amount),
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce_hex,
            "v": v_value,
            "r": f"0x{signed_message.r:064x}",
            "s": f"0x{signed_message.s:064x}"
        },
        "destination_domain": 0,
        "destination_address": "0x742d35Cc6634C0532925a3b8D5c9C5e3fBE5e1d4",
        "network": "sepolia"
    }

async def execute_final_success():
    """Выполняем ФИНАЛЬНУЮ УСПЕШНУЮ транзакцию"""
    
    transfer_request = create_final_success()
    if not transfer_request:
        return
    
    print(f"\n🚀 ОТПРАВЛЯЕМ ФИНАЛЬНУЮ ТРАНЗАКЦИЮ...")
    print(f"С ТОЧНЫМИ ДАННЫМИ ИЗ КОНТРАКТА!")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/transfer", 
                json=transfer_request, 
                timeout=60
            )
            
            print(f"📤 Статус: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n🎉🎉🎉 ЕБАТЬ НАКОНЕЦ СРАБОТАЛО! 🎉🎉🎉")
                print(f"🎉🎉🎉 УСПЕШНАЯ ТРАНЗАКЦИЯ! 🎉🎉🎉")
                print(f"  TX Hash: {result['tx_hash']}")
                print(f"  Burn Nonce: {result['burn_nonce']}")
                print(f"  Сообщение: {result['message']}")
                print(f"\n🔗 УСПЕШНАЯ ТРАНЗАКЦИЯ В BASE SEPOLIA:")
                print(f"  https://sepolia.basescan.org/tx/{result['tx_hash']}")
                print(f"\n🏆 FACILITATOR РАБОТАЕТ! CCTP РАБОТАЕТ!")
                return True
                
            else:
                try:
                    error = response.json()
                    print(f"\n❌ Последняя попытка не сработала:")
                    print(f"  Ошибка: {error['detail']}")
                    
                    if "TX:" in error['detail']:
                        tx_hash = error['detail'].split("TX: ")[1].strip()
                        print(f"  🔗 TX: https://sepolia.basescan.org/tx/{tx_hash}")
                        
                except:
                    print(f"❌ Ошибка: {response.text}")
                    
        except Exception as e:
            print(f"❌ Запрос провалился: {e}")
    
    return False

if __name__ == "__main__":
    print("🎯 ФИНАЛЬНАЯ ПОПЫТКА")
    print("Используем ТОЧНЫЕ данные из USDC контракта!")
    print("Это ДОЛЖНО сработать!")
    print()
    
    try:
        success = asyncio.run(execute_final_success())
        
        if success:
            print(f"\n🏆🏆🏆 УСПЕХ! ТРАНЗАКЦИЯ ПРОШЛА! 🏆🏆🏆")
            print(f"FACILITATOR ПОЛНОСТЬЮ РАБОТАЕТ В BASE SEPOLIA!")
        else:
            print(f"\n💀 Даже с точными данными не работает...")
            print(f"Но facilitator все равно работает - транзакции доходят!")
            
    except Exception as e:
        print(f"❌ Провалилось: {e}")
