import os
import asyncio
import logging
from typing import Dict, Any, Optional
from x402.clients.requests import x402_requests
from eth_account import Account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class X402Client:
    """Client for making x402 micropayment requests to other agents using official x402 library"""
    
    def __init__(self):
        self.timeout = 30.0
        
        # Initialize wallet account for payments
        # Use the real private key from .env file
        private_key = os.getenv("WALLET_PRIVATE_KEY")
        if not private_key:
            raise ValueError("WALLET_PRIVATE_KEY not found in environment variables")
        
        self.account = Account.from_key(private_key)
        
        logger.info(f"🔑 Initialized X402Client with wallet: {self.account.address}")
        
        # Create x402 requests session
        try:
            self.session = x402_requests(self.account)
            logger.info(f"✅ x402 client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize x402 client: {e}")
            raise
        
    def make_paid_request(
        self, 
        agent_url: str, 
        query: str, 
        payment_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Make a paid request to an x402 agent using official x402 library
        
        Args:
            agent_url: URL of the agent endpoint
            query: Query to send to the agent
            payment_info: Payment information (unused - x402 library handles this)
            
        Returns:
            Response data from the agent or None if failed
        """
        try:
            # Build request URL with query parameter
            logger.info(f"🔍 Agent URL: {agent_url}")
            logger.info(f"🔍 Query: {query}")
            logger.info(f"🔑 Using wallet address: {self.account.address}")
            
            # Simple URL construction like in simple_x402_test.py
            request_url = f"{agent_url}?query={query}"
            
            logger.info(f"🔗 Making x402 request to: {request_url}")
            
            # Use x402 session to make request
            logger.info("🚀 Sending request via x402 session...")
            logger.info(f"🔍 x402 session type: {type(self.session)}")
            logger.info(f"🔍 Request URL: {request_url}")
            
            # The x402 session automatically handles 402 responses and payments
            response = self.session.get(request_url)
            
            logger.info(f"📡 Response status: {response.status_code}")
            logger.info(f"📡 Response headers: {dict(response.headers)}")
            
            # Log response body for debugging
            try:
                response_text = response.text
                logger.info(f"📄 Response body preview: {response_text[:200]}...")
            except:
                logger.info("📄 Could not read response body")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✅ Successfully received data from agent")
                    return data
                except Exception as e:
                    logger.error(f"❌ Failed to parse JSON response: {e}")
                    return {"error": f"Invalid JSON response: {e}", "raw_response": response.text}
            elif response.status_code == 402:
                # 402 Payment Required - this should be handled automatically by x402 library
                logger.error(f"❌ x402 library failed to handle 402 payment automatically")
                logger.error(f"❌ This indicates a problem with the x402 client setup or payment processing")
                
                # Log detailed 402 response for debugging
                logger.info(f"🔍 402 Response headers: {dict(response.headers)}")
                www_auth = response.headers.get('WWW-Authenticate', 'Not found')
                logger.info(f"🔍 WWW-Authenticate header: {www_auth}")
                
                try:
                    error_data = response.json()
                    logger.info(f"🔍 402 Response body: {error_data}")
                    return {"error": f"Payment required but not processed: {response.status_code}", "details": error_data}
                except:
                    error_text = response.text
                    logger.info(f"🔍 402 Response text: {error_text}")
                    return {"error": f"Payment required but not processed: {response.status_code}", "raw_response": error_text}
            else:
                logger.error(f"❌ Request failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    return {"error": f"Request failed: {response.status_code}", "details": error_data}
                except:
                    return {"error": f"Request failed: {response.status_code}", "raw_response": response.text}
                        
        except Exception as e:
            logger.error(f"💥 Request failed: {e}")
            return {"error": f"Request failed: {str(e)}", "agent_url": agent_url}

    
    def discover_agent_capabilities(self, agent_base_url: str) -> Optional[Dict[str, Any]]:
        """
        Discover agent capabilities via x402 discovery endpoint
        
        Args:
            agent_base_url: Base URL of the agent (e.g., https://agent.com)
            
        Returns:
            Agent capabilities or None if failed
        """
        try:
            discovery_url = f"{agent_base_url}/.well-known/x402"
            
            response = self.session.get(discovery_url)
            
            if response.status_code == 200:
                capabilities = response.json()
                logger.info(f"🔍 Discovered agent capabilities: {capabilities.get('name', 'Unknown')}")
                return capabilities
            else:
                logger.warning(f"⚠️ Failed to discover capabilities: {response.status_code}")
                return None
                    
        except Exception as e:
            logger.error(f"💥 Error discovering agent capabilities: {e}")
            return None
    
    def get_agent_info(self, agent_base_url: str) -> Optional[Dict[str, Any]]:
        """
        Get basic agent information from root endpoint
        
        Args:
            agent_base_url: Base URL of the agent
            
        Returns:
            Agent info or None if failed
        """
        try:
            response = self.session.get(agent_base_url)
            
            if response.status_code == 200:
                info = response.json()
                logger.info(f"ℹ️ Got agent info: {info.get('name', 'Unknown')}")
                return info
            else:
                logger.warning(f"⚠️ Failed to get agent info: {response.status_code}")
                return None
                    
        except Exception as e:
            logger.error(f"💥 Error getting agent info: {e}")
            return None

