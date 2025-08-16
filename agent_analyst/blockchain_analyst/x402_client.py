import os
import httpx
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class X402Client:
    """Client for making x402 micropayment requests to other agents"""
    
    def __init__(self):
        self.timeout = 30.0
        
    async def make_paid_request(
        self, 
        agent_url: str, 
        query: str, 
        payment_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Make a paid request to an x402 agent
        
        Args:
            agent_url: URL of the agent endpoint
            query: Query to send to the agent
            payment_info: Payment information (price, network, asset, pay_to)
            
        Returns:
            Response data from the agent or None if failed
        """
        try:
            # Clean agent_url and add user query
            logger.info(f"🔍 Original agent_url: {agent_url}")
            logger.info(f"🔍 Query to add: {query}")
            
            # Remove existing query parameters from agent_url
            if "?" in agent_url:
                base_url = agent_url.split("?")[0]
            else:
                base_url = agent_url
                
            # Add only our query parameter
            request_url = f"{base_url}?query={query}"
            
            logger.info(f"🔍 Cleaned base_url: {base_url}")
            logger.info(f"🔍 Final request_url: {request_url}")
            
            logger.info(f"🔗 Making x402 request to: {request_url}")
            logger.info(f"💰 Payment info: {payment_info}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First, try to make a HEAD request to get payment requirements
                try:
                    head_response = await client.head(request_url)
                    logger.info(f"📋 HEAD response status: {head_response.status_code}")
                    logger.info(f"📋 HEAD response headers: {dict(head_response.headers)}")
                except Exception as e:
                    logger.warning(f"⚠️ HEAD request failed: {e}")
                
                # Make the actual GET request (this should trigger x402 payment requirement)
                response = await client.get(request_url)
                
                logger.info(f"📡 Response status: {response.status_code}")
                logger.info(f"📡 Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    # Success - got the data
                    try:
                        data = response.json()
                        logger.info(f"✅ Successfully received data from agent")
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Failed to parse JSON response: {e}")
                        return {"error": f"Invalid JSON response: {e}", "raw_response": response.text}
                
                elif response.status_code == 402:
                    # Payment required - this is expected for x402 agents
                    logger.info(f"💳 Payment required (402) - this is normal for x402 agents")
                    try:
                        payment_data = response.json()
                        logger.info(f"💳 Payment requirements: {payment_data}")
                        
                        # For now, we'll return the payment requirements
                        # In a full implementation, we would handle the actual payment here
                        return {
                            "payment_required": True,
                            "payment_info": payment_data,
                            "message": "This agent requires x402 payment. Payment handling not implemented in this demo."
                        }
                    except json.JSONDecodeError:
                        return {
                            "payment_required": True,
                            "message": "Payment required but couldn't parse payment info",
                            "raw_response": response.text
                        }
                
                else:
                    # Other error
                    logger.error(f"❌ Request failed with status {response.status_code}")
                    try:
                        error_data = response.json()
                        return {"error": f"Request failed: {response.status_code}", "details": error_data}
                    except json.JSONDecodeError:
                        return {"error": f"Request failed: {response.status_code}", "raw_response": response.text}
                        
        except httpx.TimeoutException:
            logger.error(f"⏰ Request timeout to {agent_url}")
            return {"error": "Request timeout", "agent_url": agent_url}
            
        except httpx.RequestError as e:
            logger.error(f"🌐 Network error: {e}")
            return {"error": f"Network error: {str(e)}", "agent_url": agent_url}
            
        except Exception as e:
            logger.error(f"💥 Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}", "agent_url": agent_url}
    
    async def discover_agent_capabilities(self, agent_base_url: str) -> Optional[Dict[str, Any]]:
        """
        Discover agent capabilities via x402 discovery endpoint
        
        Args:
            agent_base_url: Base URL of the agent (e.g., https://agent.com)
            
        Returns:
            Agent capabilities or None if failed
        """
        try:
            discovery_url = f"{agent_base_url}/.well-known/x402"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(discovery_url)
                
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
    
    async def get_agent_info(self, agent_base_url: str) -> Optional[Dict[str, Any]]:
        """
        Get basic agent information from root endpoint
        
        Args:
            agent_base_url: Base URL of the agent
            
        Returns:
            Agent info or None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(agent_base_url)
                
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
