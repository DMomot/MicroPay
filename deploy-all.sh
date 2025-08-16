#!/bin/bash

# Deploy all Railway services
echo "🚂 Deploying Coinbase Price Agent to Railway..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m' 
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Deploying Demo Server...${NC}"
railway up --service demo --detach
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Demo server deployed successfully${NC}"
else
    echo -e "${RED}❌ Demo server deployment failed${NC}"
fi

echo -e "${BLUE}💰 Deploying x402 Server...${NC}"
railway up --service x402 --detach  
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ x402 server deployed successfully${NC}"
else
    echo -e "${RED}❌ x402 server deployment failed${NC}"
fi

echo -e "${BLUE}🤖 Deploying MCP Server...${NC}"
railway up --service mcp --detach
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ MCP server deployed successfully${NC}"
else
    echo -e "${RED}❌ MCP server deployment failed${NC}"
fi

echo -e "${GREEN}🎉 All deployments completed!${NC}"
echo -e "${BLUE}Check your Railway dashboard for URLs${NC}"
