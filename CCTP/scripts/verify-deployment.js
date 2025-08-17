const { ethers } = require("hardhat");

async function main() {
  console.log("🔍 Verifying deployed contract...");
  
  // Deployed contract address
  const contractAddress = "0x4F26A0466F08BA8Ee601C661C0B2e8d75996a48c";
  
  // Get network info
  const network = await ethers.provider.getNetwork();
  console.log(`📡 Network: ${network.name} (Chain ID: ${network.chainId})`);
  
  // Connect to deployed contract
  const cctp = await ethers.getContractAt("CCTPTransferBurn", contractAddress);
  console.log(`📍 Contract Address: ${contractAddress}`);
  
  try {
    // Check basic contract info
    console.log("\n🔍 Reading contract state...");
    
    const usdcAddress = await cctp.usdcToken();
    console.log(`✅ USDC Token: ${usdcAddress}`);
    
    const tokenMinterAddress = await cctp.tokenMinter();
    console.log(`✅ Token Minter: ${tokenMinterAddress}`);
    
    const owner = await cctp.owner();
    console.log(`✅ Owner: ${owner}`);
    
    // Test destination extraction function
    console.log("\n🧪 Testing destination extraction...");
    const testNonce = ethers.utils.solidityPack(
      ["uint32", "address", "uint64"],
      [1, "0x693f7243e7577A3845364F23d856349f15571856", Math.floor(Date.now() / 1000)]
    );
    
    const [domain, destAddress] = await cctp.extractDestinationFromNonce(testNonce);
    console.log(`✅ Destination Domain: ${domain}`);
    console.log(`✅ Destination Address: ${destAddress}`);
    
    console.log("\n🎉 Contract verification completed successfully!");
    console.log("\n📋 Contract is ready for use:");
    console.log(`- Network: BASE Sepolia`);
    console.log(`- Contract: ${contractAddress}`);
    console.log(`- Explorer: https://sepolia.basescan.org/address/${contractAddress}`);
    
  } catch (error) {
    console.error("❌ Verification failed:", error.message);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Script failed:", error);
    process.exit(1);
  });
