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
            
            # Step 3: Gather data from agents
            logger.info("📡 STEP 3: Gathering data from agents...")
            collected_data = await self._gather_data(relevant_agents, user_query)
            successful_data = sum(1 for data in collected_data.values() if "error" not in data)
            logger.info(f"✅ Data collection complete: {successful_data}/{len(collected_data)} successful")
            
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
        """Identify what type of data is needed for the analysis"""
        
        logger.info(f"🔍 Analyzing query to identify data needs: '{query}'")
        
        prompt = f"""
        Analyze this blockchain/crypto query and identify what types of data are needed:
        
        Query: "{query}"
        
        Possible data types:
        - price_data: Historical or current cryptocurrency prices
        - market_data: Market cap, volume, trading data
        - defi_data: DeFi protocol information, yields, TVL
        - nft_data: NFT collection data, floor prices, sales
        - news_data: Recent news and market sentiment
        - technical_data: Technical indicators, chart analysis
        - on_chain_data: Blockchain metrics, transactions, addresses
        
        Return only a JSON list of needed data types, like: ["price_data", "market_data"]
        """
        
        try:
            if not self.model:
                logger.warning("⚠️ Gemini model not configured, using fallback analysis")
                raise Exception("Gemini model not configured")
            
            logger.info("🤖 Using Gemini to identify data requirements...")
            
            # Run Gemini in thread pool since it's not async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    f"You are a data analyst. Return only valid JSON.\n\n{prompt}",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=200,
                        temperature=0.1
                    )
                )
            )
            
            result = response.text.strip()
            logger.info(f"🤖 Gemini response: {result}")
            parsed_result = json.loads(result)
            logger.info(f"✅ Parsed data requirements: {parsed_result}")
            return parsed_result
            
        except Exception as e:
            logger.warning(f"⚠️ Gemini analysis failed ({e}), using keyword-based fallback")
            
            # Fallback to basic analysis
            query_lower = query.lower()
            needs = []
            
            if any(word in query_lower for word in ["price", "cost", "value", "worth"]):
                needs.append("price_data")
                logger.info("📈 Detected need for price data")
            if any(word in query_lower for word in ["market", "volume", "cap"]):
                needs.append("market_data")
                logger.info("📊 Detected need for market data")
            if any(word in query_lower for word in ["defi", "yield", "farming", "protocol"]):
                needs.append("defi_data")
                logger.info("🏦 Detected need for DeFi data")
            if any(word in query_lower for word in ["nft", "collection", "floor"]):
                needs.append("nft_data")
                logger.info("🖼️ Detected need for NFT data")
                
            final_needs = needs if needs else ["price_data"]
            logger.info(f"✅ Fallback analysis result: {final_needs}")
            return final_needs
    
    async def _find_agents(self, data_requirements: List[str]) -> List[Dict[str, Any]]:
        """Find agents that can provide the required data using the finder service"""
        
        relevant_agents = []
        
        # Map data requirements to search queries for finder
        search_queries = {
            "price_data": "cryptocurrency price historical data coinbase bitcoin ethereum",
            "market_data": "market cap volume trading data cryptocurrency",
            "defi_data": "defi protocol yield farming tvl liquidity",
            "nft_data": "nft collection floor price sales opensea",
            "news_data": "crypto news sentiment analysis market",
            "technical_data": "technical analysis indicators charts trading",
            "on_chain_data": "blockchain metrics transactions addresses on-chain"
        }
        
        logger.info(f"🔍 Searching for agents to provide data: {data_requirements}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for data_type in data_requirements:
                if data_type in search_queries:
                    try:
                        search_query = search_queries[data_type]
                        logger.info(f"🔍 Searching finder for '{data_type}' with query: '{search_query}'")
                        
                        response = await client.post(
                            f"{self.finder_url}/search",
                            json={
                                "prompt": search_query,
                                "max_results": 5,
                                "min_rating": 0.3  # Lower threshold to find more agents
                            },
                            headers={"Content-Type": "application/json"}
                        )
                        
                        logger.info(f"📡 Finder response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            search_result = response.json()
                            found_agents = search_result.get("agents", [])
                            logger.info(f"✅ Found {len(found_agents)} agents for {data_type}")
                            
                            for agent in found_agents:
                                # Avoid duplicates
                                if not any(existing["name"] == agent["name"] for existing in relevant_agents):
                                    relevant_agents.append(agent)
                                    logger.info(f"➕ Added agent: {agent['name']} - {agent.get('description', 'No description')[:100]}...")
                        else:
                            logger.error(f"❌ Finder search failed with status {response.status_code}: {response.text}")
                                    
                    except Exception as e:
                        logger.error(f"❌ Error finding agents for {data_type}: {e}")
                        continue
        
        logger.info(f"📊 Total unique agents found: {len(relevant_agents)}")
        return relevant_agents[:10]  # Increase limit to get more data sources
    
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
                
                # Construct full agent URL
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
                
                # Try to make x402 paid request
                payment_info = {
                    "price": agent.get("price_usdc", "0.01"),
                    "network": agent.get("network", "base"),
                    "asset": agent.get("asset_address", ""),
                    "pay_to": agent.get("pay_to_address", "")
                }
                
                result = await self.x402_client.make_paid_request(
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
