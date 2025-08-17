const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CCTPTransferBurn - Simple Tests", function () {
  let cctp, usdc, tokenMinter;
  let owner, user;
  
  // BASE network addresses
  const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // USDC on BASE
  const TOKEN_MINTER_ADDRESS = "0x1682Ae6375C4E4A97e4B583BC394c861A46D8962"; // CCTP TokenMinter on BASE
  
  const TRANSFER_AMOUNT = ethers.utils.parseUnits("100", 6); // 100 USDC
  
  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();
    
    // Get contract instances
    usdc = await ethers.getContractAt("IEIP3009", USDC_ADDRESS);
    tokenMinter = await ethers.getContractAt("ITokenMinter", TOKEN_MINTER_ADDRESS);
    
    // Deploy our contract
    const CCTPTransferBurn = await ethers.getContractFactory("CCTPTransferBurn");
    cctp = await CCTPTransferBurn.deploy(USDC_ADDRESS, TOKEN_MINTER_ADDRESS);
    await cctp.deployed();
    
    console.log("✅ CCTP Contract deployed to:", cctp.address);
  });

  describe("Contract Deployment", function () {
    it("Should deploy successfully", async function () {
      expect(cctp.address).to.not.equal(ethers.constants.AddressZero);
      console.log("✅ Contract deployed successfully");
    });
    
    it("Should have correct USDC and TokenMinter addresses", async function () {
      expect(await cctp.usdcToken()).to.equal(USDC_ADDRESS);
      expect(await cctp.tokenMinter()).to.equal(TOKEN_MINTER_ADDRESS);
      console.log("✅ Contract addresses configured correctly");
    });
  });

  describe("EIP3009 Signature Creation", function () {
    it("Should create valid EIP3009 signature", async function () {
      // Generate secure nonce on frontend (как должно быть)
      const timestamp = Math.floor(Date.now() / 1000);
      const random = ethers.utils.randomBytes(16);
      const nonce = ethers.utils.keccak256(
        ethers.utils.defaultAbiCoder.encode(
          ["address", "uint256", "uint256", "bytes16"],
          [user.address, 8453, timestamp, random]
        )
      );
      const validAfter = 0;
      const validBefore = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now
      
      // Create EIP3009 signature
      const domain = {
        name: "USD Coin",
        version: "2",
        chainId: 8453, // BASE chain ID
        verifyingContract: USDC_ADDRESS
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
      
      const value = {
        from: user.address,
        to: cctp.address,
        value: TRANSFER_AMOUNT,
        validAfter: validAfter,
        validBefore: validBefore,
        nonce: nonce
      };
      
      const signature = await user._signTypedData(domain, types, value);
      const { v, r, s } = ethers.utils.splitSignature(signature);
      
      console.log("✅ EIP3009 signature created:");
      console.log("  v:", v);
      console.log("  r:", r.substring(0, 10) + "...");
      console.log("  s:", s.substring(0, 10) + "...");
      
      expect(v).to.be.oneOf([27, 28]);
      expect(r).to.not.equal(ethers.constants.HashZero);
      expect(s).to.not.equal(ethers.constants.HashZero);
    });
  });

  describe("Mock Transfer Test", function () {
    it("Should handle transferAndBurn call (will revert without USDC)", async function () {
      // Generate nonce on frontend
      const nonce = ethers.utils.keccak256(
        ethers.utils.defaultAbiCoder.encode(
          ["address", "uint256", "uint256"],
          [user.address, 8453, Math.floor(Date.now() / 1000)]
        )
      );
      const validAfter = 0;
      const validBefore = Math.floor(Date.now() / 1000) + 3600;
      
      // This will fail because user doesn't have USDC, but we test the signature creation
      await expect(
        cctp.transferAndBurn(
          user.address,
          TRANSFER_AMOUNT,
          validAfter,
          validBefore,
          nonce,
          27, // mock v
          ethers.constants.HashZero, // mock r
          ethers.constants.HashZero, // mock s
        )
      ).to.be.reverted;
      
      console.log("✅ transferAndBurn function exists and reverts as expected without valid signature");
    });
  });

  describe("Contract Information", function () {
    it("Should display contract setup info", async function () {
      console.log("\n📋 Contract Setup Information:");
      console.log("  Contract Address:", cctp.address);
      console.log("  USDC Address:", USDC_ADDRESS);
      console.log("  TokenMinter Address:", TOKEN_MINTER_ADDRESS);
      console.log("  Owner Address:", owner.address);
      console.log("  Test User Address:", user.address);
      console.log("\n🔧 To test with real USDC:");
      console.log("  1. Fund test user with USDC from a whale address");
      console.log("  2. Create valid EIP3009 signature");
      console.log("  3. Call transferAndBurn with valid signature");
      console.log("  4. Verify USDC transfer and CCTP burn");
    });
  });
});
