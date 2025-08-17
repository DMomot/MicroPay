"""
Утилиты для правильного вычисления domainSeparator
"""

from eth_utils import keccak
from eth_abi import encode

def calculate_domain_separator(name: str, version: str, chain_id: int, verifying_contract: str) -> bytes:
    """
    Правильно вычисляет domainSeparator согласно EIP-712 и Solidity коду
    
    Args:
        name: Имя контракта (например, "USDC")
        version: Версия контракта (например, "2")
        chain_id: ID сети (например, 84532 для Base Sepolia)
        verifying_contract: Адрес контракта (например, "0x036CbD53842c5426634e7929541eC2318f3dCF7e")
    
    Returns:
        bytes: domainSeparator
    """
    
    # EIP712Domain typehash
    # keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
    type_hash = bytes.fromhex("8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f")
    
    # Вычисляем хеши name и version
    name_hash = keccak(name.encode('utf-8'))
    version_hash = keccak(version.encode('utf-8'))
    
    # Используем abi.encode как в Solidity
    encoded_data = encode(
        ['bytes32', 'bytes32', 'bytes32', 'uint256', 'address'],
        [type_hash, name_hash, version_hash, chain_id, verifying_contract]
    )
    
    return keccak(encoded_data)

def get_usdc_domain_separator(chain_id: int, usdc_address: str) -> bytes:
    """
    Получает domainSeparator для USDC контракта
    
    Args:
        chain_id: ID сети
        usdc_address: Адрес USDC контракта
    
    Returns:
        bytes: domainSeparator для USDC
    """
    return calculate_domain_separator("USDC", "2", chain_id, usdc_address)

# Константы для Base Sepolia
BASE_SEPOLIA_CHAIN_ID = 84532
BASE_SEPOLIA_USDC_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"

def get_base_sepolia_usdc_domain_separator() -> bytes:
    """Получает domainSeparator для USDC на Base Sepolia"""
    return get_usdc_domain_separator(BASE_SEPOLIA_CHAIN_ID, BASE_SEPOLIA_USDC_ADDRESS)

if __name__ == "__main__":
    # Тест
    domain_sep = get_base_sepolia_usdc_domain_separator()
    expected = bytes.fromhex("71f17a3b2ff373b803d70a5a07c046c1a2bc8e89c09ef722fcb047abe94c9818")
    
    print(f"Calculated: 0x{domain_sep.hex()}")
    print(f"Expected:   0x{expected.hex()}")
    print(f"Match: {'✅' if domain_sep == expected else '❌'}")
