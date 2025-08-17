"""
CCTP Transfer Facilitator API
Accepts EIP3009 signatures and executes transferAndBurn through our contract
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from web3 import Web3
from loguru import logger
import json
from dotenv import load_dotenv
# Rate limiting removed for MVP simplicity

# Load environment variables
load_dotenv()

# Rate limiting removed for MVP

# FastAPI app
app = FastAPI(
    title="CCTP Facilitator API",
    description="API for executing CCTP transfers via EIP3009 signatures",
    version="1.0.0"
)

# Rate limiting middleware removed for MVP

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production specify concrete domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    # Network settings
    BASE_SEPOLIA_RPC = os.getenv("BASE_SEPOLIA_RPC", "https://sepolia.base.org")
    BASE_MAINNET_RPC = os.getenv("BASE_MAINNET_RPC", "https://mainnet.base.org")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    
    # Contract addresses
    CCTP_CONTRACT_SEPOLIA = "0x4F26A0466F08BA8Ee601C661C0B2e8d75996a48c"
    CCTP_CONTRACT_MAINNET = os.getenv("CCTP_CONTRACT_MAINNET", "")
    
    # USDC addresses
    USDC_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    USDC_MAINNET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    
    # Chain IDs
    BASE_SEPOLIA_CHAIN_ID = 84532
    BASE_MAINNET_CHAIN_ID = 8453

config = Config()

# Contract ABI (main functions)
CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
            {"name": "destinationDomain", "type": "uint32"},
            {"name": "destinationAddress", "type": "bytes32"},
            {"name": "v", "type": "uint8"},
            {"name": "r", "type": "bytes32"},
            {"name": "s", "type": "bytes32"}
        ],
        "name": "transferAndBurn",
        "outputs": [{"name": "", "type": "uint64"}],
        "type": "function"
    },
    {
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
            {"name": "v", "type": "uint8"},
            {"name": "r", "type": "bytes32"},
            {"name": "s", "type": "bytes32"}
        ],
        "name": "transferAndBurnFromNonce",
        "outputs": [{"name": "", "type": "uint64"}],
        "type": "function"
    },
    {
        "inputs": [{"name": "nonce", "type": "bytes32"}],
        "name": "extractDestinationFromNonce",
        "outputs": [
            {"name": "destinationDomain", "type": "uint32"},
            {"name": "destinationAddress", "type": "bytes32"}
        ],
        "type": "function"
    }
]

# Pydantic models
class EIP3009Signature(BaseModel):
    from_address: str = Field(..., alias="from")
    to_address: str = Field(..., alias="to")
    amount: str = Field(..., description="Amount in wei (USDC has 6 decimals)")
    valid_after: int = Field(0, alias="validAfter")
    valid_before: int = Field(..., alias="validBefore")
    nonce: str = Field(..., description="32-byte hex string")
    v: int = Field(..., ge=27, le=28)
    r: str = Field(..., description="32-byte hex string")
    s: str = Field(..., description="32-byte hex string")

class TransferRequest(BaseModel):
    signature: EIP3009Signature
    destination_domain: int = Field(..., description="CCTP destination domain")
    destination_address: str = Field(..., description="Destination address")
    network: str = Field("sepolia", description="Network: sepolia or mainnet")

class TransferFromNonceRequest(BaseModel):
    signature: EIP3009Signature
    network: str = Field("sepolia", description="Network: sepolia or mainnet")

class TransferResponse(BaseModel):
    success: bool
    tx_hash: str
    burn_nonce: int
    message: str

# Web3 connections
def get_web3(network: str) -> Web3:
    """Get Web3 instance for specified network"""
    if network == "sepolia":
        rpc_url = config.BASE_SEPOLIA_RPC
    elif network == "mainnet":
        rpc_url = config.BASE_MAINNET_RPC
    else:
        raise ValueError(f"Unsupported network: {network}")
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to {network}")
    
    return w3

def get_contract(w3: Web3, network: str):
    """Get contract instance"""
    if network == "sepolia":
        contract_address = config.CCTP_CONTRACT_SEPOLIA
    elif network == "mainnet":
        contract_address = config.CCTP_CONTRACT_MAINNET
    else:
        raise ValueError(f"Unsupported network: {network}")
    
    return w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=CONTRACT_ABI
    )

def get_account(w3: Web3):
    """Get account from private key"""
    if not config.PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY not set")
    
    return w3.eth.account.from_key(config.PRIVATE_KEY)

# API Routes
@app.get("/")
async def root():
    return {
        "service": "CCTP Facilitator API",
        "version": "1.0.0",
        "status": "running",
        "contract_sepolia": config.CCTP_CONTRACT_SEPOLIA,
        "supported_networks": ["sepolia", "mainnet"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test connection to sepolia
        w3 = get_web3("sepolia")
        block = w3.eth.get_block("latest")
        
        return {
            "status": "healthy",
            "network_connected": True,
            "latest_block": block.number,
            "timestamp": block.timestamp
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/transfer", response_model=TransferResponse)
async def transfer_and_burn(transfer_request: TransferRequest, request: Request):
    """
    Execute transferAndBurn with explicit destination parameters
    """
    try:
        remote_addr = request.client.host
        logger.info(f"Transfer request from {remote_addr}: {transfer_request.signature.amount} USDC")
        
        # Get Web3 and contract
        w3 = get_web3(transfer_request.network)
        contract = get_contract(w3, transfer_request.network)
        account = get_account(w3)
        
        # Prepare transaction parameters
        nonce_hex = transfer_request.signature.nonce.replace('0x', '')
        dest_hex = transfer_request.destination_address.replace('0x', '').lower()
        r_hex = transfer_request.signature.r.replace('0x', '')
        s_hex = transfer_request.signature.s.replace('0x', '')
        
        # Ensure proper hex formatting
        if len(dest_hex) < 40:
            dest_hex = dest_hex.ljust(40, '0')
        dest_bytes32 = dest_hex.ljust(64, '0')
        
        logger.info(f"Nonce: {nonce_hex}, Dest: {dest_bytes32}, R: {r_hex[:10]}..., S: {s_hex[:10]}...")
        
        tx_data = contract.functions.transferAndBurn(
            Web3.to_checksum_address(transfer_request.signature.from_address),
            int(transfer_request.signature.amount),
            transfer_request.signature.valid_after,
            transfer_request.signature.valid_before,
            bytes.fromhex(nonce_hex),
            transfer_request.destination_domain,
            bytes.fromhex(dest_bytes32),
            transfer_request.signature.v,
            bytes.fromhex(r_hex),
            bytes.fromhex(s_hex)
        )
        
        # Build transaction
        tx = tx_data.build_transaction({
            'from': account.address,
            'gas': 300000,  # Estimate gas
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, config.PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check if transaction was successful
        if receipt.status == 0:
            logger.error(f"Transaction failed: {tx_hash.hex()}")
            raise Exception(f"Transaction failed in blockchain. TX: {tx_hash.hex()}")
        
        # Extract burn nonce from logs (simplified)
        burn_nonce = 0  # TODO: Parse from event logs
        
        logger.info(f"Transfer successful: {tx_hash.hex()}")
        
        return TransferResponse(
            success=True,
            tx_hash=tx_hash.hex(),
            burn_nonce=burn_nonce,
            message="Transfer completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transfer-from-nonce", response_model=TransferResponse)
async def transfer_and_burn_from_nonce(transfer_request: TransferFromNonceRequest, request: Request):
    """
    Execute transferAndBurnFromNonce (destination extracted from nonce)
    """
    try:
        remote_addr = request.client.host
        logger.info(f"Transfer from nonce request from {remote_addr}")
        
        # Get Web3 and contract
        w3 = get_web3(transfer_request.network)
        contract = get_contract(w3, transfer_request.network)
        account = get_account(w3)
        
        # Prepare transaction
        tx_data = contract.functions.transferAndBurnFromNonce(
            Web3.to_checksum_address(transfer_request.signature.from_address),
            int(transfer_request.signature.amount),
            transfer_request.signature.valid_after,
            transfer_request.signature.valid_before,
            bytes.fromhex(transfer_request.signature.nonce.replace('0x', '')),
            transfer_request.signature.v,
            bytes.fromhex(transfer_request.signature.r.replace('0x', '')),
            bytes.fromhex(transfer_request.signature.s.replace('0x', ''))
        )
        
        # Build transaction
        tx = tx_data.build_transaction({
            'from': account.address,
            'gas': 300000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, config.PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check if transaction was successful
        if receipt.status == 0:
            logger.error(f"Transfer from nonce failed: {tx_hash.hex()}")
            raise Exception(f"Transaction failed in blockchain. TX: {tx_hash.hex()}")
        
        burn_nonce = 0  # TODO: Parse from event logs
        
        logger.info(f"Transfer from nonce successful: {tx_hash.hex()}")
        
        return TransferResponse(
            success=True,
            tx_hash=tx_hash.hex(),
            burn_nonce=burn_nonce,
            message="Transfer completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Transfer from nonce failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/extract-destination/{nonce}")
async def extract_destination(nonce: str, network: str = "sepolia"):
    """
    Extract destination info from nonce
    """
    try:
        w3 = get_web3(network)
        contract = get_contract(w3, network)
        
        # Call contract function
        result = contract.functions.extractDestinationFromNonce(
            bytes.fromhex(nonce.replace('0x', ''))
        ).call()
        
        return {
            "destination_domain": result[0],
            "destination_address": result[1].hex(),
            "nonce": nonce
        }
        
    except Exception as e:
        logger.error(f"Extract destination failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
