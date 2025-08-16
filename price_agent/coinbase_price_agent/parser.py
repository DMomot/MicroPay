import re
from datetime import datetime, timedelta
from typing import Dict, Optional


class QueryParser:
    def __init__(self):
        self.prompt = """
Extract parameters for Coinbase API from text query.

AVAILABLE PARAMETERS:
- index: index name (COIN50, BTC, ETH, etc.)
- granularity: ONE_DAY or ONE_HOUR
- start: start date in ISO 8601 (2024-01-01T00:00:00Z)
- end: end date in ISO 8601 (optional)

PARSING RULES:
1. If granularity not specified - use ONE_DAY
2. If end not specified - leave empty
3. Convert relative dates to ISO 8601:
   - "yesterday" = yesterday's date
   - "week ago" = 7 days ago
   - "2 weeks" = 14 days ago
   - "month ago" = 30 days ago
   - "2 months" = 60 days ago
4. If index not found - use COIN50

EXAMPLES:
"Show me BTC prices for last week" -> 
{
  "index": "BTC",
  "granularity": "ONE_DAY", 
  "start": "2024-01-01T00:00:00Z",
  "end": ""
}

"BTC prices for 2 last months" ->
{
  "index": "BTC",
  "granularity": "ONE_DAY", 
  "start": "2024-01-01T00:00:00Z",
  "end": ""
}
        """
        
    def parse_query(self, query: str) -> Dict[str, str]:
        result = {
            "index": "COIN50",
            "granularity": "ONE_DAY",
            "start": "",
            "end": ""
        }
        
        # Parse index/symbol
        index_patterns = [
            r'\b(COIN50|BTC|ETH|SOL|DOGE|ADA|DOT|LINK|UNI|AAVE|MATIC|AVAX|LTC|BCH|XLM|ATOM)\b',
            r'\b(Bitcoin|bitcoin|Ethereum|ethereum|etherium|Solana|solana|Dogecoin|dogecoin)\b',
            r'\b(Cardano|cardano|Polkadot|polkadot|Chainlink|chainlink|Uniswap|uniswap)\b',
            r'\b(Polygon|polygon|matic|Avalanche|avalanche|avax|Litecoin|litecoin)\b',
            r'index\s+(\w+)',
            r'for\s+(\w+)',
            r'(\w+)\s+price',
        ]
        
        for pattern in index_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                index = match.group(1).upper()
                # Convert full names and typos to abbreviations
                name_mapping = {
                    "BITCOIN": "BTC",
                    "ETHEREUM": "ETH", 
                    "ETHERIUM": "ETH",  # Handle common typo
                    "SOLANA": "SOL",
                    "DOGECOIN": "DOGE",
                    "CARDANO": "ADA",
                    "POLKADOT": "DOT",
                    "CHAINLINK": "LINK",
                    "UNISWAP": "UNI",
                    "POLYGON": "MATIC",
                    "AVALANCHE": "AVAX",
                    "LITECOIN": "LTC"
                }
                result["index"] = name_mapping.get(index, index)
                break
                
        # Parse granularity
        if any(word in query.lower() for word in ["hour", "hourly", "hrs"]):
            result["granularity"] = "ONE_HOUR"
            
        # Parse dates
        result.update(self._parse_dates(query))
        
        return result
        
    def _parse_dates(self, query: str) -> Dict[str, str]:
        now = datetime.now()
        
        # Relative dates (Russian and English)
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["вчера", "yesterday"]):
            start = now - timedelta(days=1)
            return {
                "start": start.strftime("%Y-%m-%dT00:00:00Z"),
                "end": now.strftime("%Y-%m-%dT00:00:00Z")
            }
        
        # Parse weeks with numbers (e.g., "2 weeks", "last 3 weeks")
        week_match = re.search(r'(\d+)\s*(?:last\s+)?weeks?|last\s+(\d+)\s+weeks?', query_lower)
        if week_match:
            num_weeks = int(week_match.group(1) or week_match.group(2))
            start = now - timedelta(days=7 * num_weeks)
            return {
                "start": start.strftime("%Y-%m-%dT00:00:00Z"),
                "end": now.strftime("%Y-%m-%dT00:00:00Z")
            }
            
        if any(word in query_lower for word in ["неделю", "неделя", "week", "last week"]):
            start = now - timedelta(days=7)
            return {
                "start": start.strftime("%Y-%m-%dT00:00:00Z"),
                "end": now.strftime("%Y-%m-%dT00:00:00Z")
            }
        
        # Parse months with numbers (e.g., "2 months", "last 3 months")
        month_match = re.search(r'(\d+)\s*(?:last\s+)?months?|last\s+(\d+)\s+months?', query_lower)
        if month_match:
            num_months = int(month_match.group(1) or month_match.group(2))
            start = now - timedelta(days=30 * num_months)
            return {
                "start": start.strftime("%Y-%m-%dT00:00:00Z"),
                "end": now.strftime("%Y-%m-%dT00:00:00Z")
            }
            
        if any(word in query_lower for word in ["месяц", "month", "last month"]):
            start = now - timedelta(days=30)
            return {
                "start": start.strftime("%Y-%m-%dT00:00:00Z"),
                "end": now.strftime("%Y-%m-%dT00:00:00Z")
            }
            
        if any(word in query_lower for word in ["год", "year", "last year"]):
            # Limit to 300 days to not exceed Coinbase limit
            start = now - timedelta(days=300)
            return {
                "start": start.strftime("%Y-%m-%dT00:00:00Z"),
                "end": now.strftime("%Y-%m-%dT00:00:00Z")
            }
            
        # Search for specific dates
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, query)
        
        if len(dates) >= 1:
            start_date = f"{dates[0]}T00:00:00Z"
            end_date = f"{dates[1]}T00:00:00Z" if len(dates) > 1 else ""
            return {"start": start_date, "end": end_date}
            
        # Default - last 30 days
        start = now - timedelta(days=30)
        return {
            "start": start.strftime("%Y-%m-%dT00:00:00Z"),
            "end": now.strftime("%Y-%m-%dT00:00:00Z")
        }
