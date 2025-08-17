"""
Create valid EIP3009 signature for USDC transfer
"""

import os
from web3 import Web3
from eth_account import Account
from eth_utils import keccak
from eth_abi import encode
from dotenv import load_dotenv
from domain_separator_utils import get_base_sepolia_usdc_domain_separator
from nonce_utils import create_cctp_nonce, parse_cctp_nonce, get_domain_name
import time
import struct

# Load environment variables
load_dotenv()

def create_valid_eip3009_signature():
    """Create valid EIP3009 signature for USDC"""
    
    # Get user private key
    user_key = os.getenv("PRIVATE_KEY_USER")
    if not user_key:
        print("❌ PRIVATE_KEY_USER not found")
        return None
    
    if not user_key.startswith('0x'):
        user_key = '0x' + user_key
    
    user_account = Account.from_key(user_key)
    print(f"👤 User address: {user_account.address}")
    
    # Contract addresses on Base Sepolia
    usdc_address = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    contract_address = "0x4F26A0466F08BA8Ee601C661C0B2e8d75996a48c"
    chain_id = 84532  # Base Sepolia
    
    # Transaction parameters
    amount = 1000000  # 1 USDC (6 decimals)
    valid_after = 0
    valid_before = int(time.time()) + 3600  # Valid for 1 hour
    
    # Create CCTP nonce with destination info
    destination_domain = 0  # Ethereum mainnet
    destination_address = "0x742d35Cc6634C0532925a3b8D5c9C5e3fBE5e1d4"
    
    # Create proper CCTP nonce (32 bytes: 4 bytes domain + 20 bytes address + 8 bytes random)
    nonce_bytes = create_cctp_nonce(destination_domain, destination_address)
    nonce_hex = f"0x{nonce_bytes.hex()}"
    
    # Parse nonce for display
    nonce_info = parse_cctp_nonce(nonce_bytes)
    
    print(f"\n📋 Transaction details:")
    print(f"  From: {user_account.address}")
    print(f"  To: {contract_address}")
    print(f"  Amount: {amount / 1000000} USDC")
    print(f"  Valid until: {valid_before}")
    print(f"  Nonce: {nonce_hex}")
    print(f"  📍 CCTP Destination:")
    print(f"    Domain: {nonce_info['destination_domain']} ({get_domain_name(nonce_info['destination_domain'])})")
    print(f"    Address: {nonce_info['destination_address']}")
    print(f"    Random: {nonce_info['random_data']}")
    
    # EIP712 Domain Separator for USDC on Base Sepolia - правильное вычисление
    domain_separator = get_base_sepolia_usdc_domain_separator()
    
    # TransferWithAuthorization typehash (из контракта)
    typehash = bytes.fromhex("7c7c6cdb67a18743f49ec6fa9b35f50d52ed05cbed4cc592e13b44501c1a2267")
    
    # Encode message используя abi.encode как в Solidity
    message_encoded = encode(
        ['bytes32', 'address', 'address', 'uint256', 'uint256', 'uint256', 'bytes32'],
        [typehash, user_account.address, contract_address, amount, valid_after, valid_before, nonce_bytes]
    )
    message_hash = keccak(message_encoded)
    
    # Final hash to sign
    digest = keccak(b"\x19\x01" + domain_separator + message_hash)
    
    # Sign the digest
    from eth_account.messages import _hash_eip191_message
    signature = user_account._key_obj.sign_msg_hash(digest)
    
    # Adjust v value to be >= 27 (Ethereum standard)
    v_value = signature.v + 27 if signature.v < 27 else signature.v
    
    print(f"\n🔐 EIP3009 Signature:")
    print(f"  v: {v_value}")
    print(f"  r: 0x{signature.r:064x}")
    print(f"  s: 0x{signature.s:064x}")
    
    # Create transfer request
    transfer_request = {
        "signature": {
            "from": user_account.address,
            "to": contract_address,
            "amount": str(amount),
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce_hex,
            "v": v_value,
            "r": f"0x{signature.r:064x}",
            "s": f"0x{signature.s:064x}"
        },
        "destination_domain": destination_domain,
        "destination_address": destination_address,
        "network": "sepolia"
    }
    
    return transfer_request

async def test_valid_signature():
    """Test with valid EIP3009 signature"""
    import httpx
    
    transfer_request = create_valid_eip3009_signature()
    if not transfer_request:
        return
    
    print(f"\n🚀 Sending transfer with valid signature...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8000/transfer", json=transfer_request, timeout=60)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Transaction successful!")
                print(f"  TX Hash: {result['tx_hash']}")
                print(f"  Burn Nonce: {result['burn_nonce']}")
                print(f"  🔗 View on Base Sepolia: https://sepolia.basescan.org/tx/{result['tx_hash']}")
            else:
                try:
                    error = response.json()
                    print(f"❌ Transaction failed: {error['detail']}")
                    
                    if "TX:" in error['detail']:
                        tx_hash = error['detail'].split("TX: ")[1].strip()
                        print(f"  🔗 Failed TX: https://sepolia.basescan.org/tx/{tx_hash}")
                        
                except:
                    print(f"❌ Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    import asyncio
    
    print("🧪 Creating Valid EIP3009 Signature for CCTP Transfer")
    print("=" * 60)
    
    try:
        asyncio.run(test_valid_signature())
    except Exception as e:
        print(f"❌ Test failed: {e}")
