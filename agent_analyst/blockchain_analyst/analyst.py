import os
import httpx
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from .x402_client import X402Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BlockchainAnalyst:
    """Professional blockchain analyst that gathers data from various agents and provides analysis"""
    
    def __init__(self):
        # Configure Gemini
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
            
        self.finder_url = "https://aifinder-production.up.railway.app"
        self.x402_client = X402Client()
        
        # System prompt for the analyst
        self.system_prompt = """
        You are a senior blockchain analyst and crypto market expert with 10+ years of experience. 
        You provide institutional-grade analysis with deep technical insights and market intelligence.
        
        🎯 ANALYSIS STYLE:
        - Professional, detailed, and data-driven
        - Use specific numbers, percentages, and calculations
        - Identify clear trends, patterns, and anomalies
        - Provide actionable insights and recommendations
        - Include risk assessment and market outlook
        
        📊 REQUIRED ANALYSIS SECTIONS:
        
        1. **EXECUTIVE SUMMARY** (2-3 sentences)
           - Key finding and overall trend direction
           - Most significant price movement or pattern
        
        2. **PRICE ANALYSIS**
           - Current price vs period high/low with percentages
           - Price trend: bullish/bearish/sideways with evidence
           - Key support and resistance levels from data
           - Volatility analysis (calculate price swings)
        
        3. **VOLUME ANALYSIS** 
           - Volume trends: increasing/decreasing/stable (in BTC and USD)
           - Calculate USD volume for each day: BTC_Volume × ((Open + High + Low + Close) / 4)
           - Show both BTC volume and calculated USD volume for each significant day
           - Volume-price correlation insights
           - Identify volume spikes and their significance (both BTC and USD)
           - Average daily volume vs recent activity (both BTC and USD)
           - Total trading volume for the period in USD (sum of all daily USD volumes)
        
        4. **TECHNICAL INDICATORS** (calculate from data)
           - Moving averages (if enough data points)
           - Price momentum and velocity
           - Volatility metrics (daily ranges)
           - Breakout or breakdown patterns
        
        5. **KEY METRICS & STATISTICS**
           - Period high/low prices and dates
           - Largest single-day gains/losses (both price and USD volume)
           - Average daily price change
           - Price distribution analysis
           - Top 5 days by USD trading volume with specific calculations
           - Show calculation example: Day X: Volume=1000 BTC, Avg_Price=$50k → USD_Volume=$50M
        
        6. **MARKET INSIGHTS**
           - What the data reveals about market sentiment
           - Unusual patterns or anomalies detected
           - Comparison to typical market behavior
           - Institutional vs retail activity signals
        
        7. **RISK ASSESSMENT**
           - Volatility risk level (Low/Medium/High)
           - Key risk factors identified from data
           - Potential downside scenarios
           - Risk-reward analysis
        
        8. **OUTLOOK & RECOMMENDATIONS**
           - Short-term trend prediction based on data
           - Key levels to watch (support/resistance)
           - Trading/investment recommendations
           - Catalysts that could change the trend
        
        🔢 CALCULATION REQUIREMENTS:
        - Always calculate percentage changes
        - Show price ranges and volatility metrics
        - Compute volume-weighted averages when possible
        - Calculate USD volume: Volume_BTC × Average_Daily_Price for each period
        - Average Daily Price = (Open + High + Low + Close) / 4 OR (High + Low + Close) / 3
        - Show total USD volume for the entire period
        - Compare daily USD volumes to identify significant trading days
        - Calculate average daily USD volume
        - Identify statistical outliers in both BTC and USD volumes
        
        📈 TREND IDENTIFICATION:
        - Use terms like "strong uptrend", "consolidation", "bearish reversal"
        - Quantify trends with specific data points
        - Identify trend strength and sustainability
        - Note any trend changes or inflection points
        
        ⚠️ CRITICAL RULES:
        - Base analysis ONLY on provided real data
        - Reference specific data points and timestamps
        - No speculation without data backing
        - If insufficient data, clearly state limitations
        - Always include disclaimer about market volatility
        
        Format with clear headers, bullet points, and professional language.
        Make the analysis engaging and insightful for both technical and non-technical readers.
        """
    
    async def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """Main analysis function that processes user query and returns comprehensive report"""
        
        logger.info(f"🚀 STARTING ANALYSIS for query: '{user_query}'")
        
        try:
            # Step 1: Analyze what data we need
            logger.info("📋 STEP 1: Identifying data requirements...")
            data_requirements = await self._identify_data_needs(user_query)
            logger.info(f"✅ Data requirements identified: {data_requirements}")
            
            # Step 2: Find appropriate agents
            logger.info("🔍 STEP 2: Finding relevant agents...")
            relevant_agents = await self._find_agents(data_requirements)
            agent_names = [agent.get("name", "Unknown") for agent in relevant_agents]
            logger.info(f"✅ Found {len(relevant_agents)} agents: {agent_names}")
            
            # Step 2.5: Get x402 metadata and optimize agent selection
            logger.info("🔍 STEP 2.5: Getting x402 metadata and optimizing agent selection...")
            optimized_agents = await self._get_x402_metadata_and_optimize(relevant_agents)
            optimized_names = [agent.get("name", "Unknown") for agent in optimized_agents]
            logger.info(f"✅ Optimized to {len(optimized_agents)} agents: {optimized_names}")
            
            # Step 3: Gather data from agents
            logger.info("📡 STEP 3: Gathering data from agents...")
            # Transform user query for price agents
            price_query = self._transform_query_for_prices(user_query)
            collected_data = await self._gather_data(optimized_agents, price_query)
            successful_data = sum(1 for data in collected_data.values() if "error" not in data)
            logger.info(f"📊 Data collection complete: {successful_data}/{len(collected_data)} successful")
            
            # Check if we have any successful data
            if successful_data == 0:
                logger.error("❌ No data collected successfully - cannot generate analysis")
                return {
                    "query": user_query,
                    "error": "Failed to collect data from any agents",
                    "data_collection_status": f"{successful_data}/{len(collected_data)} successful",
                    "collected_errors": collected_data,
                    "timestamp": self._get_timestamp()
                }
            
            # Step 4: Generate analysis
            logger.info("🧠 STEP 4: Generating analysis with Gemini...")
            analysis = await self._generate_analysis(user_query, collected_data)
            logger.info("✅ Analysis generation complete")
            
            result = {
                "query": user_query,
                "data_requirements": data_requirements,
                "data_sources": agent_names,
                "data_collection_status": f"{successful_data}/{len(collected_data)} successful",
                "analysis": analysis,
                "timestamp": self._get_timestamp()
            }
            
            logger.info("🎉 ANALYSIS COMPLETED SUCCESSFULLY")
            return result
            
        except Exception as e:
            logger.error(f"❌ ANALYSIS FAILED: {str(e)}")
            return {
                "query": user_query,
                "error": f"Analysis failed: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    async def _identify_data_needs(self, query: str) -> List[str]:
        """Always return only price_data for analysis"""
        
        logger.info(f"🔍 Analyzing query to identify data needs: '{query}'")
        logger.info("📈 Using only price data for analysis")
        
        return ["price_data"]
    
    async def _find_agents(self, data_requirements: List[str]) -> List[Dict[str, Any]]:
        """Find agents that can provide the required data using the finder service"""
        
        relevant_agents = []
        
        # Search for price-related agents only
        search_query = "cryptocurrency price historical data"
        logger.info(f"🔍 Searching for price agents with query: '{search_query}'")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.finder_url}/search",
                    json={
                        "prompt": search_query,
                        "max_results": 5,
                        "min_rating": 0.8  # Increase for stricter matching
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                logger.info(f"📡 Finder response status: {response.status_code}")
                
                if response.status_code == 200:
                    search_result = response.json()
                    found_agents = search_result.get("agents", [])
                    logger.info(f"✅ Found {len(found_agents)} price agents")
                    
                    for agent in found_agents:
                        relevant_agents.append(agent)
                        logger.info(f"➕ Added price agent: {agent['name']} - {agent.get('description', 'No description')[:100]}...")
                else:
                    logger.error(f"❌ Finder search failed with status {response.status_code}: {response.text}")
                        
            except Exception as e:
                logger.error(f"❌ Error searching for price agents: {e}")
        
        logger.info(f"📊 Total unique agents found: {len(relevant_agents)}")
        return relevant_agents[:10]  # Increase limit to get more data sources
    
    def _transform_query_for_prices(self, user_query: str) -> str:
        """Transform user query into a price data request"""
        
        # Extract cryptocurrency from query - expanded list
        crypto_tokens = [
            "bitcoin", "btc", 
            "ethereum", "eth", 
            "solana", "sol", 
            "dogecoin", "doge",
            "cardano", "ada",
            "polygon", "matic",
            "chainlink", "link",
            "avalanche", "avax",
            "polkadot", "dot",
            "uniswap", "uni",
            "litecoin", "ltc",
            "bitcoin cash", "bch",
            "stellar", "xlm",
            "cosmos", "atom",
            "algorand", "algo",
            "tezos", "xtz",
            "filecoin", "fil",
            "aave", "aave",
            "compound", "comp",
            "maker", "mkr",
            "sushi", "sushi",
            "yearn", "yfi"
        ]
        found_token = "bitcoin"  # default
        
        query_lower = user_query.lower()
        for token in crypto_tokens:
            if token in query_lower:
                found_token = token
                break
        
        # Extract time period
        time_period = "2 months"  # default
        if "week" in query_lower:
            time_period = "1 week"
        elif "month" in query_lower:
            if "two month" in query_lower or "2 month" in query_lower or "two months" in query_lower or "2 months" in query_lower:
                time_period = "2 months"
            else:
                time_period = "1 month"
        elif "year" in query_lower:
            time_period = "1 year"
        
        # Create price query in format that price agent understands better
        token_mapping = {
            "bitcoin": "BTC", "btc": "BTC",
            "ethereum": "ETH", "eth": "ETH", 
            "solana": "SOL", "sol": "SOL",
            "dogecoin": "DOGE", "doge": "DOGE",
            "cardano": "ADA", "ada": "ADA",
            "polygon": "MATIC", "matic": "MATIC",
            "chainlink": "LINK", "link": "LINK",
            "avalanche": "AVAX", "avax": "AVAX",
            "polkadot": "DOT", "dot": "DOT",
            "uniswap": "UNI", "uni": "UNI",
            "litecoin": "LTC", "ltc": "LTC",
            "bitcoin cash": "BCH", "bch": "BCH",
            "stellar": "XLM", "xlm": "XLM",
            "cosmos": "ATOM", "atom": "ATOM",
            "algorand": "ALGO", "algo": "ALGO",
            "tezos": "XTZ", "xtz": "XTZ",
            "filecoin": "FIL", "fil": "FIL",
            "aave": "AAVE",
            "compound": "COMP", "comp": "COMP",
            "maker": "MKR", "mkr": "MKR",
            "sushi": "SUSHI",
            "yearn": "YFI", "yfi": "YFI"
        }
        
        crypto_symbol = token_mapping.get(found_token.lower(), "BTC")  # default to Bitcoin
            
        price_query = f"Get {crypto_symbol} price data for {time_period}"
        logger.info(f"🔄 Transformed query: '{user_query}' → '{price_query}'")
        
        return price_query
    
    async def _get_x402_metadata_and_optimize(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get x402 metadata for each agent and optimize selection based on capabilities and cost
        
        Args:
            agents: List of agents from finder
            
        Returns:
            Optimized list of agents with x402 metadata
        """
        optimized_agents = []
        
        logger.info(f"🔍 Getting x402 metadata for {len(agents)} agents...")
        
        for agent in agents:
            agent_name = agent.get("name", "Unknown Agent")
            try:
                # Extract base URL from resource
                resource = agent.get("resource", "")
                if not resource:
                    logger.warning(f"❌ {agent_name}: No resource URL provided")
                    continue
                
                # Construct base URL for x402 discovery
                if resource.startswith("http"):
                    # Extract domain from full URL
                    from urllib.parse import urlparse
                    parsed = urlparse(resource)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                else:
                    # Handle different resource formats
                    if resource.startswith("/"):
                        logger.warning(f"⚠️ {agent_name}: Resource is path only: {resource}")
                        continue
                    else:
                        base_url = f"https://{resource.split('/')[0]}"
                
                logger.info(f"🔍 {agent_name}: Getting x402 metadata from {base_url}")
                
                # Get x402 metadata using our client
                x402_metadata = self.x402_client.discover_agent_capabilities(base_url)
                
                if x402_metadata:
                    # Log raw x402 metadata for debugging
                    logger.info(f"🔍 {agent_name}: Raw x402 metadata: {x402_metadata}")
                    
                    # Enrich agent data with x402 metadata
                    enriched_agent = agent.copy()
                    enriched_agent["x402_metadata"] = x402_metadata
                    
                    # Extract payment information from x402 metadata
                    # x402 metadata structure can vary, let's handle different formats
                    accepts = x402_metadata.get("accepts", [])
                    if not accepts:
                        # Try alternative structure - endpoints with accepts
                        endpoints = x402_metadata.get("endpoints", [])
                        if endpoints:
                            accepts = [endpoints[0].get("accepts", {})]
                        else:
                            # Try resources structure
                            accepts = x402_metadata.get("resources", [])
                    
                    if accepts:
                        payment_option = accepts[0]  # Use first payment option
                        enriched_agent["payment_required"] = int(payment_option.get("maxAmountRequired", payment_option.get("amount", "0")))
                        enriched_agent["payment_network"] = payment_option.get("network", "base")
                        enriched_agent["payment_asset"] = payment_option.get("asset", payment_option.get("currency", ""))
                        enriched_agent["pay_to"] = payment_option.get("payTo", payment_option.get("address", ""))
                        enriched_agent["description"] = payment_option.get("description", agent.get("description", ""))
                        
                        # Log detailed payment info for debugging
                        logger.info(f"💰 {agent_name}: Payment details from x402:")
                        logger.info(f"   - Amount: {enriched_agent['payment_required']} wei")
                        logger.info(f"   - Network: {enriched_agent['payment_network']}")
                        logger.info(f"   - Asset: {enriched_agent['payment_asset']}")
                        logger.info(f"   - Pay to: {enriched_agent['pay_to']}")
                    else:
                        # No payment info found, set defaults
                        enriched_agent["payment_required"] = 0
                        enriched_agent["payment_network"] = "base"
                        enriched_agent["payment_asset"] = ""
                        enriched_agent["pay_to"] = ""
                        logger.warning(f"⚠️ {agent_name}: No payment info found in x402 metadata")
                    
                    optimized_agents.append(enriched_agent)
                    logger.info(f"✅ {agent_name}: x402 metadata retrieved successfully")
                else:
                    logger.warning(f"⚠️ {agent_name}: Failed to get x402 metadata")
                    # Still include agent but without x402 metadata
                    agent_copy = agent.copy()
                    agent_copy["x402_metadata"] = None
                    optimized_agents.append(agent_copy)
                    
            except Exception as e:
                logger.error(f"❌ {agent_name}: Error getting x402 metadata - {e}")
                # Include agent without metadata
                agent_copy = agent.copy()
                agent_copy["x402_metadata"] = None
                optimized_agents.append(agent_copy)
                continue
        
        # Sort agents by payment cost (cheaper first) and capabilities
        def agent_score(agent):
            # Prefer agents with x402 metadata
            if agent.get("x402_metadata"):
                payment_cost = agent.get("payment_required", float('inf'))
                # Lower cost = better score
                return payment_cost
            else:
                # Agents without x402 metadata get lower priority
                return float('inf')
        
        optimized_agents.sort(key=agent_score)
        
        # Limit to top 3 agents to control costs
        optimized_agents = optimized_agents[:3]
        
        logger.info(f"🎯 Optimized agent selection:")
        for i, agent in enumerate(optimized_agents, 1):
            name = agent.get("name", "Unknown")
            cost = agent.get("payment_required", "unknown")
            network = agent.get("payment_network", "unknown")
            logger.info(f"  {i}. {name}: {cost} wei on {network}")
        
        return optimized_agents
    
    async def _gather_data(self, agents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Gather data from the found agents using x402 payments"""
        
        collected_data = {}
        
        if not agents:
            logger.warning("⚠️ No agents found to gather data from")
            return collected_data
        
        logger.info(f"📡 Attempting to gather data from {len(agents)} agents")
        
        for agent in agents:
            agent_name = agent.get("name", "Unknown Agent")
            try:
                # Extract agent URL and endpoint
                resource = agent.get("resource", "")
                if not resource:
                    logger.warning(f"❌ {agent_name}: No resource URL provided")
                    collected_data[agent_name] = {"error": "No resource URL provided"}
                    continue
                
                # Construct agent URL
                if resource.startswith("http"):
                    agent_url = resource
                else:
                    # Handle different resource formats
                    if resource.startswith("/"):
                        # Resource is a path, need to extract domain from somewhere
                        logger.warning(f"⚠️ {agent_name}: Resource is path only: {resource}")
                        collected_data[agent_name] = {"error": "Cannot construct URL from path-only resource"}
                        continue
                    else:
                        # Assume format like "domain.com/path" or just "domain.com"
                        if "/" in resource:
                            agent_url = f"https://{resource}"
                        else:
                            agent_url = f"https://{resource}"
                
                logger.info(f"🔗 {agent_name}: Attempting to connect to {agent_url}")
                
                # Use enriched payment info from x402 metadata if available
                if agent.get("x402_metadata"):
                    payment_info = {
                        "amount": agent.get("payment_required", "0"),
                        "network": agent.get("payment_network", "base"),
                        "asset": agent.get("payment_asset", ""),
                        "pay_to": agent.get("pay_to", "")
                    }
                    logger.info(f"💰 {agent_name}: Using x402 metadata - {payment_info['amount']} wei on {payment_info['network']}")
                else:
                    # Fallback to finder data
                    payment_info = {
                        "price": agent.get("price_usdc", "0.01"),
                        "network": agent.get("network", "base"),
                        "asset": agent.get("asset_address", ""),
                        "pay_to": agent.get("pay_to_address", "")
                    }
                    logger.info(f"💰 {agent_name}: Using finder data - fallback payment info")
                
                result = self.x402_client.make_paid_request(
                    agent_url, 
                    query, 
                    payment_info
                )
                
                if result:
                    logger.info(f"✅ {agent_name}: Data collected successfully")
                    collected_data[agent_name] = result
                else:
                    logger.warning(f"❌ {agent_name}: Failed to get data")
                    collected_data[agent_name] = {"error": "Failed to get data from agent"}
                    
            except Exception as e:
                logger.error(f"❌ {agent_name}: Error - {e}")
                collected_data[agent_name] = {"error": str(e)}
                continue
        
        successful_requests = sum(1 for data in collected_data.values() if "error" not in data)
        logger.info(f"📊 Data collection complete: {successful_requests}/{len(agents)} successful")
        
        return collected_data
    
    async def _generate_analysis(self, query: str, data: Dict[str, Any]) -> str:
        """Generate comprehensive analysis based on collected data"""
        
        data_summary = self._summarize_data(data)
        
        analysis_prompt = f"""
        {self.system_prompt}
        
        🎯 USER REQUEST: "{query}"
        
        📊 COLLECTED DATA:
        {data_summary}
        
        🔍 ANALYSIS INSTRUCTIONS:
        
        IF REAL DATA IS AVAILABLE:
        - Perform comprehensive analysis using the 8-section structure above
        - IMPORTANT: The "volume" field in data is BTC volume, NOT USD volume
        - MUST calculate USD volume: For each day, USD_Volume = BTC_Volume × ((Open+High+Low+Close)/4)
        - Calculate specific metrics: price changes, volatility, volume trends
        - Identify patterns: trends, support/resistance, breakouts
        - Provide concrete numbers and percentages
        - Make data-driven predictions and recommendations
        - Include risk assessment with specific risk levels
        
        IF NO DATA AVAILABLE:
        - Clearly state data limitations
        - Explain what analysis would be possible with proper data
        - Suggest specific data sources needed
        - Do NOT provide speculative analysis
        
        📈 FOCUS AREAS FOR ANALYSIS:
        - Price momentum and trend direction
        - Volume patterns and market participation (BTC and USD volumes)
        - Dollar volume analysis: For each day calculate USD_Volume = BTC_Volume × Average_Price
        - CRITICAL: Volume field is in BTC, you MUST convert to USD
        - Example calculation: If volume=1000 BTC, Open=$50k, High=$52k, Low=$49k, Close=$51k
          Step 1: Average_Price = (50000+52000+49000+51000)/4 = $50,500
          Step 2: USD_Volume = 1000 BTC × $50,500 = $50,500,000 USD
        - Always show this calculation for top volume days
        - Volume-weighted average prices (VWAP) when possible
        - Volatility analysis and risk metrics
        - Key support/resistance levels
        - Market sentiment indicators from volume/price correlation
        - Trading opportunities and risks based on volume patterns
        
        🎨 OUTPUT STYLE:
        - Use professional financial language
        - Include specific numbers and calculations
        - Format with clear sections and bullet points
        - Make it engaging for both technical and general audiences
        - End with actionable recommendations
        
        Remember: This analysis will be used for investment decisions, so be thorough and precise.
        """
        
        try:
            if not self.model:
                logger.error("❌ Gemini model not configured")
                raise Exception("Gemini model not configured")
            
            logger.info("🧠 Generating analysis with Gemini Flash 2.0...")
            
            # Run Gemini in thread pool since it's not async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    f"You are a professional blockchain analyst.\n\n{analysis_prompt}",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=2000,
                        temperature=0.3
                    )
                )
            )
            
            logger.info("✅ Gemini analysis generated successfully")
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Analysis generation failed: {str(e)}")
            return f"Analysis generation failed: {str(e)}"
    
    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """Create a summary of collected data for analysis"""
        
        if not data:
            return "CRITICAL: No data collected from agents. Analysis cannot proceed without real data."
        
        summary = []
        successful_data = 0
        
        for agent_name, agent_data in data.items():
            if isinstance(agent_data, dict) and "error" in agent_data:
                summary.append(f"- {agent_name}: FAILED - {agent_data['error']}")
            else:
                summary.append(f"- {agent_name}: SUCCESS - Data collected")
                successful_data += 1
                
                # Include the actual data in the summary for analysis
                if isinstance(agent_data, dict):
                    # Format the data nicely for Gemini
                    data_str = json.dumps(agent_data, indent=2)
                    summary.append(f"  ACTUAL DATA FROM {agent_name}:")
                    summary.append(f"  {data_str}")
                else:
                    summary.append(f"  ACTUAL DATA FROM {agent_name}: {str(agent_data)}")
        
        if successful_data == 0:
            summary.insert(0, "CRITICAL: All data collection attempts failed. Cannot provide analysis without real data.")
        else:
            summary.insert(0, f"Data Collection Status: {successful_data}/{len(data)} agents provided data successfully.")
            summary.insert(1, "")
            summary.insert(2, "=== COLLECTED DATA FOR ANALYSIS ===")
        
        return "\n".join(summary)
    
    def _get_timestamp(self) -> int:
        """Get current timestamp"""
        import time
        return int(time.time())
