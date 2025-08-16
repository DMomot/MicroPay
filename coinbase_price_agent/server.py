import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel
from typing import Any, Sequence
from .client import CoinbaseClient
from .parser import QueryParser


class GetHistoricalPricesArgs(BaseModel):
    index: str
    granularity: str = "ONE_DAY"
    start: str
    end: str | None = None


class QueryPricesArgs(BaseModel):
    query: str


server = Server("coinbase-price-agent")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_historical_prices",
            description="Get historical prices from Coinbase for specified index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Index name (e.g., COIN50)"
                    },
                    "granularity": {
                        "type": "string",
                        "enum": ["ONE_DAY", "ONE_HOUR"],
                        "description": "Time interval for aggregation",
                        "default": "ONE_DAY"
                    },
                    "start": {
                        "type": "string",
                        "description": "Start date in ISO 8601 format (e.g., 2024-01-01T00:00:00Z)"
                    },
                    "end": {
                        "type": "string",
                        "description": "End date in ISO 8601 format (optional)"
                    }
                },
                "required": ["index", "start"]
            }
        ),
        Tool(
            name="query_prices",
            description="Get historical prices using natural language text query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query (e.g., 'Show me BTC prices for last week')"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    if name == "query_prices":
        return await handle_query_prices(arguments)
    elif name == "get_historical_prices":
        return await handle_get_historical_prices(arguments)
    else:
        raise ValueError(f"Неизвестный инструмент: {name}")


async def handle_query_prices(arguments: dict[str, Any]) -> Sequence[TextContent]:
    args = QueryPricesArgs(**arguments)
    parser = QueryParser()
    
    # Parse query
    parsed_params = parser.parse_query(args.query)
    
    if not parsed_params["start"]:
        return [TextContent(
            type="text",
            text=f"Failed to parse date from query: '{args.query}'"
        )]
    
    # Call main function with parsed parameters
    return await handle_get_historical_prices(parsed_params)


async def handle_get_historical_prices(arguments: dict[str, Any]) -> Sequence[TextContent]:
    args = GetHistoricalPricesArgs(**arguments)
    api_key = os.getenv("COINBASE_API_KEY")
    private_key = os.getenv("COINBASE_PRIVATE_KEY")
    
    if not api_key or not private_key:
        return [TextContent(
            type="text",
            text="Error: COINBASE_API_KEY and COINBASE_PRIVATE_KEY environment variables not set"
        )]
    
    client = CoinbaseClient(api_key, private_key)
    
    try:
        data = await client.get_historical_prices(
            symbol=args.index,
            start=args.start,
            granularity=args.granularity,
            end=args.end
        )
        
        return [TextContent(
            type="text",
            text=f"Historical data for {args.index}:\n{data}"
        )]
    
    except Exception as e:
        return [TextContent(
            type="text", 
            text=f"Error fetching data: {str(e)}"
        )]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
