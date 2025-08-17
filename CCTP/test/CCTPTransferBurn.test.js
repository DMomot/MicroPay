const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CCTPTransferBurn", function () {
  let cctp, usdc, tokenMinter;
  let owner, user, otherAccount;
  let userPrivateKey;
  
  // BASE network addresses
  const USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // USDC on BASE
  const TOKEN_MINTER_ADDRESS = "0x1682Ae6375C4E4A97e4B583BC394c861A46D8962"; // CCTP TokenMinter on BASE
  
  const TRANSFER_AMOUNT = ethers.utils.parseUnits("100", 6); // 100 USDC
  
  beforeEach(async function () {
    [owner, user, otherAccount] = await ethers.getSigners();
    
    // Generate a test private key for EIP3009 signing
    const wallet = ethers.Wallet.createRandom();
    userPrivateKey = wallet.privateKey;
    user = wallet.connect(ethers.provider);
    
    // Get USDC contract instance
    usdc = await ethers.getContractAt("IEIP3009", USDC_ADDRESS);
    
    // Get TokenMinter contract instance  
    tokenMinter = await ethers.getContractAt("ITokenMinter", TOKEN_MINTER_ADDRESS);
    
    // Deploy our contract
    const CCTPTransferBurn = await ethers.getContractFactory("CCTPTransferBurn");
    cctp = await CCTPTransferBurn.deploy(USDC_ADDRESS, TOKEN_MINTER_ADDRESS);
    await cctp.deployed();
    
    console.log("CCTP Contract deployed to:", cctp.address);
    console.log("Test user address:", user.address);
  });

  describe("Setup and Balance", function () {
    it("Should fund test user with USDC", async function () {
      // Impersonate a USDC whale to transfer tokens to test user
      const whaleAddress = "0x4c80E24119CFB836cdF0a6b53dc23F04F7e652CA"; // Known USDC holder on BASE
      
      await network.provider.request({
        method: "hardhat_impersonateAccount",
        params: [whaleAddress],
      });
      
      const whale = await ethers.getSigner(whaleAddress);
      
      // Fund the whale with ETH for gas
      await owner.sendTransaction({
        to: whaleAddress,
        value: ethers.utils.parseEther("1.0")
      });
      
      // Transfer USDC to test user
      const usdcWhale = await ethers.getContractAt("IERC20", USDC_ADDRESS, whale);
      await usdcWhale.transfer(user.address, TRANSFER_AMOUNT);
      
      const balance = await usdcWhale.balanceOf(user.address);
      expect(balance).to.equal(TRANSFER_AMOUNT);
      
      console.log(`User USDC balance: ${ethers.utils.formatUnits(balance, 6)} USDC`);
      
      await network.provider.request({
        method: "hardhat_stopImpersonatingAccount",
        params: [whaleAddress],
      });
    });
  });

  describe("EIP3009 Signature", function () {
    it("Should create valid EIP3009 signature", async function () {
      // Fund user first
      await this.parent.ctx.test.fn(); // Run the funding test
      
      const nonce = ethers.utils.randomBytes(32);
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
      
      console.log("EIP3009 signature created:");
      console.log("v:", v);
      console.log("r:", r);
      console.log("s:", s);
      
      expect(v).to.be.oneOf([27, 28]);
      expect(r).to.not.equal(ethers.constants.HashZero);
      expect(s).to.not.equal(ethers.constants.HashZero);
    });
  });

  describe("Transfer and Burn", function () {
    it("Should execute transferAndBurn successfully", async function () {
      // Setup: Fund user with USDC
      const whaleAddress = "0x4c80E24119CFB836cdF0a6b53dc23F04F7e652CA";
      
      await network.provider.request({
        method: "hardhat_impersonateAccount",
        params: [whaleAddress],
      });
      
      const whale = await ethers.getSigner(whaleAddress);
      await owner.sendTransaction({
        to: whaleAddress,
        value: ethers.utils.parseEther("1.0")
      });
      
      const usdcWhale = await ethers.getContractAt("IERC20", USDC_ADDRESS, whale);
      await usdcWhale.transfer(user.address, TRANSFER_AMOUNT);
      
      // Create EIP3009 signature
      const nonce = ethers.utils.randomBytes(32);
      const validAfter = 0;
      const validBefore = Math.floor(Date.now() / 1000) + 3600;
      
      const domain = {
        name: "USD Coin",
        version: "2", 
        chainId: 8453,
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
      
      // Check initial balances
      const initialUserBalance = await usdcWhale.balanceOf(user.address);
      const initialContractBalance = await usdcWhale.balanceOf(cctp.address);
      
      console.log(`Initial user balance: ${ethers.utils.formatUnits(initialUserBalance, 6)} USDC`);
      console.log(`Initial contract balance: ${ethers.utils.formatUnits(initialContractBalance, 6)} USDC`);
      
      // Execute transferAndBurn
      const tx = await cctp.transferAndBurn(
        user.address,
        TRANSFER_AMOUNT,
        validAfter,
        validBefore,
        nonce,
        v,
        r,
        s
      );
      
      const receipt = await tx.wait();
      console.log("Transaction hash:", receipt.hash);
      
      // Check final balances
      const finalUserBalance = await usdcWhale.balanceOf(user.address);
      const finalContractBalance = await usdcWhale.balanceOf(cctp.address);
      
      console.log(`Final user balance: ${ethers.utils.formatUnits(finalUserBalance, 6)} USDC`);
      console.log(`Final contract balance: ${ethers.utils.formatUnits(finalContractBalance, 6)} USDC`);
      
      // Verify transfer occurred
      expect(finalUserBalance).to.equal(initialUserBalance - TRANSFER_AMOUNT);
      
      // Check for TransferAndBurn event
      const events = receipt.logs.filter(log => {
        try {
          return cctp.interface.parseLog(log);
        } catch {
          return false;
        }
      });
      
      expect(events.length).to.be.greaterThan(0);
      console.log("TransferAndBurn executed successfully!");
      
      await network.provider.request({
        method: "hardhat_stopImpersonatingAccount", 
        params: [whaleAddress],
      });
    });
    
    it("Should fail with invalid signature", async function () {
      const nonce = ethers.utils.randomBytes(32);
      const validAfter = 0;
      const validBefore = Math.floor(Date.now() / 1000) + 3600;
      
      // Use invalid signature values
      await expect(
        cctp.transferAndBurn(
          user.address,
          TRANSFER_AMOUNT,
          validAfter,
          validBefore,
          nonce,
          27, // invalid v
          ethers.constants.HashZero, // invalid r
          ethers.constants.HashZero, // invalid s
        )
      ).to.be.reverted;
    });
  });
});
