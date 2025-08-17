const { ethers } = require("hardhat");

async function main() {
  console.log("📝 CCTP Contract Usage Example");
  
  // Deployed contract address
  const contractAddress = "0x4F26A0466F08BA8Ee601C661C0B2e8d75996a48c";
  
  // Connect to contract
  const cctp = await ethers.getContractAt("CCTPTransferBurn", contractAddress);
  const [signer] = await ethers.getSigners();
  
  console.log(`📍 Contract: ${contractAddress}`);
  console.log(`👤 User: ${signer.address}`);
  
  // Example 1: Generate nonce with destination info
  console.log("\n🔧 Example 1: Generate nonce with destination");
  
  const destinationDomain = 0; // Ethereum mainnet domain
  const destinationAddress = "0x742d35Cc6634C0532925a3b8D5c9C5e3fBE5e1d4"; // Example recipient
  const timestamp = Math.floor(Date.now() / 1000);
  
  const nonce = ethers.utils.solidityPack(
    ["uint32", "address", "uint64"],
    [destinationDomain, destinationAddress, timestamp]
  );
  
  console.log(`✅ Generated nonce: ${nonce}`);
  
  // Test extraction
  const [extractedDomain, extractedAddress] = await cctp.extractDestinationFromNonce(nonce);
  console.log(`✅ Extracted domain: ${extractedDomain}`);
  console.log(`✅ Extracted address: ${extractedAddress}`);
  
  // Example 2: Create EIP3009 signature (for frontend)
  console.log("\n🔧 Example 2: EIP3009 signature creation");
  
  const domain = {
    name: "USD Coin",
    version: "2",
    chainId: 84532, // BASE Sepolia
    verifyingContract: "0x036CbD53842c5426634e7929541eC2318f3dCF7e" // USDC on BASE Sepolia
  };
  
  const types = {
    TransferWithAuthorization: [
      { name: "from", type: "address" },
      { name: "to", type: "address" },
      { name: "value", type: "uint256" },
      { name: "validAfter", type: "uint256" },
      { name: "validBefore", type: "uint256" },
      { name: "nonce", type: "bytes32" }
    ]
  };
  
  const amount = ethers.utils.parseUnits("10", 6); // 10 USDC
  const validAfter = 0;
  const validBefore = Math.floor(Date.now() / 1000) + 3600; // 1 hour
  
  const value = {
    from: signer.address,
    to: contractAddress,
    value: amount,
    validAfter: validAfter,
    validBefore: validBefore,
    nonce: nonce
  };
  
  console.log("📋 EIP3009 signature data:");
  console.log(`  From: ${value.from}`);
  console.log(`  To: ${value.to}`);
  console.log(`  Amount: ${ethers.utils.formatUnits(value.value, 6)} USDC`);
  console.log(`  Valid until: ${new Date(validBefore * 1000).toISOString()}`);
  console.log(`  Nonce: ${value.nonce}`);
  
  // Example 3: Contract call structure
  console.log("\n🔧 Example 3: Contract call structure");
  console.log("To call transferAndBurn, you need:");
  console.log("1. EIP3009 signature (v, r, s)");
  console.log("2. Destination domain and address");
  console.log("3. USDC balance and approval");
  
  console.log("\n📋 Function signatures:");
  console.log("transferAndBurn(address,uint256,uint256,uint256,bytes32,uint32,bytes32,uint8,bytes32,bytes32)");
  console.log("transferAndBurnFromNonce(address,uint256,uint256,uint256,bytes32,uint8,bytes32,bytes32)");
  
  console.log("\n🌐 Network Info:");
  console.log(`BASE Sepolia Chain ID: 84532`);
  console.log(`USDC Address: 0x036CbD53842c5426634e7929541eC2318f3dCF7e`);
  console.log(`TokenMinter: 0x9f3B8679c73C2Fef8b59B4f3444d4e156fb70AA5`);
  console.log(`Explorer: https://sepolia.basescan.org/address/${contractAddress}`);
  
  console.log("\n✅ Example completed! Contract is ready for integration.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Example failed:", error);
    process.exit(1);
  });
