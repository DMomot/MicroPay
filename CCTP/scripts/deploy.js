const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Starting CCTP Transfer Burn deployment...");
  
  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Network: ${network.name} (Chain ID: ${network.chainId})`);
  
  // Get deployer account
  const signers = await ethers.getSigners();
  if (signers.length === 0) {
    throw new Error("❌ No signers found. Please set PRIVATE_KEY in .env file");
  }
  
  const [deployer] = signers;
  console.log(`👤 Deployer: ${deployer.address}`);
  
  // Check balance
  const balance = await deployer.getBalance();
  console.log(`💰 Balance: ${ethers.utils.formatEther(balance)} ETH`);
  
  // Contract addresses for different networks
  const networkConfig = {
    // BASE Sepolia Testnet
    84532: {
      name: "BASE Sepolia",
      usdc: "0x036CbD53842c5426634e7929541eC2318f3dCF7e", // USDC on BASE Sepolia
      tokenMinter: "0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5" // CCTP TokenMinter on BASE Sepolia
    },
    // BASE Mainnet
    8453: {
      name: "BASE Mainnet", 
      usdc: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", // USDC on BASE
      tokenMinter: "0x1682Ae6375C4E4A97e4B583BC394c861A46D8962" // CCTP TokenMinter on BASE
    },
    // Ethereum Sepolia (for testing)
    11155111: {
      name: "Ethereum Sepolia",
      usdc: "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238", // USDC on Sepolia
      tokenMinter: "0xBd3fa81B58Ba92a82136038B25aDec7066af3155" // CCTP TokenMinter on Sepolia
    }
  };
  
  const config = networkConfig[network.chainId];
  if (!config) {
    throw new Error(`❌ Unsupported network: ${network.chainId}`);
  }
  
  console.log(`🌐 Deploying to ${config.name}`);
  console.log(`📍 USDC Address: ${config.usdc}`);
  console.log(`📍 TokenMinter Address: ${config.tokenMinter}`);
  
  // Deploy contract
  console.log("\n📦 Deploying CCTPTransferBurn contract...");
  
  const CCTPTransferBurn = await ethers.getContractFactory("CCTPTransferBurn");
  const cctp = await CCTPTransferBurn.deploy(config.usdc, config.tokenMinter);
  
  console.log("⏳ Waiting for deployment...");
  await cctp.deployed();
  
  console.log(`✅ CCTPTransferBurn deployed to: ${cctp.address}`);
  console.log(`🔗 Transaction hash: ${cctp.deployTransaction.hash}`);
  
  // Wait for a few confirmations
  console.log("⏳ Waiting for confirmations...");
  await cctp.deployTransaction.wait(3);
  
  // Verify contract setup
  console.log("\n🔍 Verifying contract setup...");
  const usdcAddress = await cctp.usdcToken();
  const tokenMinterAddress = await cctp.tokenMinter();
  const owner = await cctp.owner();
  
  console.log(`✅ USDC Token: ${usdcAddress}`);
  console.log(`✅ Token Minter: ${tokenMinterAddress}`);
  console.log(`✅ Owner: ${owner}`);
  
  // Test destination extraction
  console.log("\n🧪 Testing destination extraction...");
  const testNonce = ethers.utils.solidityPack(
    ["uint32", "address", "uint64"],
    [1, deployer.address, Math.floor(Date.now() / 1000)]
  );
  
  const [domain, destAddress] = await cctp.extractDestinationFromNonce(testNonce);
  console.log(`✅ Test extraction - Domain: ${domain}, Address: ${destAddress}`);
  
  console.log("\n🎉 Deployment completed successfully!");
  console.log("\n📋 Contract Info:");
  console.log(`Network: ${config.name}`);
  console.log(`Contract: ${cctp.address}`);
  console.log(`USDC: ${config.usdc}`);
  console.log(`TokenMinter: ${config.tokenMinter}`);
  
  // Save deployment info
  const deploymentInfo = {
    network: config.name,
    chainId: network.chainId,
    contract: cctp.address,
    usdc: config.usdc,
    tokenMinter: config.tokenMinter,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
    txHash: cctp.deployTransaction.hash
  };
  
  console.log("\n💾 Deployment info saved to console. Copy this for your records:");
  console.log(JSON.stringify(deploymentInfo, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
