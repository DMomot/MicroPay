from coinbase.rest import RESTClient
from typing import Dict, Optional
from datetime import datetime


class CoinbaseClient:
    def __init__(self, api_key: str, private_key: str):
        self.client = RESTClient(
            api_key=api_key,
            api_secret=private_key
        )
        
    def iso_to_unix(self, iso_date: str) -> int:
        """Convert ISO date to Unix timestamp"""
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return int(dt.timestamp())
        
    async def get_historical_prices(
        self, 
        symbol: str, 
        start: str,
        granularity: str = "ONE_DAY",
        end: Optional[str] = None
    ) -> Dict:
        # Convert dates to Unix timestamp
        start_unix = self.iso_to_unix(start)
        end_unix = self.iso_to_unix(end) if end else None
        
        # Map granularity to Coinbase Advanced API format
        granularity_map = {
            "ONE_DAY": "ONE_DAY",
            "ONE_HOUR": "ONE_HOUR"
        }
        
        cb_granularity = granularity_map.get(granularity, "ONE_DAY")
        
        try:
            # Get historical data via official library
            response = self.client.get_candles(
                product_id=f"{symbol}-USD",
                start=start_unix,
                end=end_unix,
                granularity=cb_granularity
            )
            
            return response
            
        except Exception as e:
            # If USD pair fails, try alternative pairs
            alt_pairs = [f"{symbol}-USDC", f"{symbol}-BTC"]
            
            for pair in alt_pairs:
                try:
                    response = self.client.get_candles(
                        product_id=pair,
                        start=start_unix,
                        end=end_unix,
                        granularity=cb_granularity
                    )
                    return response
                except:
                    continue
                    
            raise Exception(f"Failed to get data for {symbol}: {str(e)}")
