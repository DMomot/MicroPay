# Blockchain Analyst Agent - Deployment Guide

## Quick Deploy to Railway

1. **Preparation**
   ```bash
   cd ScoutPay/agent_analyst
   ```

2. **Railway Deploy**
   ```bash
   railway login
   railway link  # or railway init for new project
   railway up
   ```

3. **Configure Environment Variables in Railway**
   ```bash
   railway variables set GEMINI_API_KEY=your_gemini_key_here
   railway variables set CDP_API_KEY_ID=your_cdp_key_id
   railway variables set CDP_API_KEY_SECRET=your_cdp_secret
   railway variables set WALLET_PRIVATE_KEY=your_wallet_private_key
   railway variables set X402_WALLET_ADDRESS=0xce465C087305314F8f0eaD5A450898f19eFD0E03
   railway variables set X402_NETWORK=base
   railway variables set X402_PRICE=0.05
   ```

## Testing

After deployment, check:

1. **Health Check**
   ```bash
   curl https://your-app.up.railway.app/health
   ```

2. **Agent Info**
   ```bash
   curl https://your-app.up.railway.app/
   ```

3. **x402 Discovery**
   ```bash
   curl https://your-app.up.railway.app/.well-known/x402
   ```

4. **Test Analysis** (requires x402 payment)
   ```bash
   curl "https://your-app.up.railway.app/api/analyze?query=Analyze Bitcoin price trends"
   ```

## Bazaar Registration

After successful deployment, the agent will be automatically discoverable via the `/.well-known/x402` endpoint.

## Monitoring

- Logs: `railway logs`
- Metrics: Railway Dashboard
- Health: `/health` endpoint

## Troubleshooting

- Ensure all environment variables are set
- Verify that GEMINI_API_KEY is valid
- Make sure CDP keys are correct for x402 payments
