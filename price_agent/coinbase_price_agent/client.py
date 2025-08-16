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
        
        # List of trading pairs to try in order of preference
        pairs_to_try = [f"{symbol}-USD", f"{symbol}-USDC", f"{symbol}-BTC"]
        last_error = None
        
        for pair in pairs_to_try:
            try:
                print(f"🔍 Trying to fetch data for {pair}...")
                response = self.client.get_candles(
                    product_id=pair,
                    start=start_unix,
                    end=end_unix,
                    granularity=cb_granularity
                )
                print(f"✅ Successfully fetched data for {pair}")
                return response
                
            except Exception as e:
                print(f"❌ Failed to fetch data for {pair}: {str(e)}")
                last_error = e
                continue
                    
        # If all pairs failed, provide helpful error message
        error_msg = f"Failed to get data for {symbol}. "
        if "INVALID_ARGUMENT" in str(last_error) or "ProductID is invalid" in str(last_error):
            error_msg += f"The symbol '{symbol}' is not available on Coinbase. "
            error_msg += "Please check the symbol name or try a different cryptocurrency."
        else:
            error_msg += f"Last error: {str(last_error)}"
            
        raise Exception(error_msg)
