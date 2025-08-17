// EIP3009 Frontend Implementation Example
// Правильная генерация подписи на фронтенде

import { ethers } from 'ethers';

class EIP3009Signer {
  constructor(provider, usdcAddress, chainId = 8453) {
    this.provider = provider;
    this.usdcAddress = usdcAddress;
    this.chainId = chainId;
    
    // EIP712 Domain для USDC на BASE
    this.domain = {
      name: "USD Coin",
      version: "2",
      chainId: chainId,
      verifyingContract: usdcAddress
    };
    
    // EIP712 Types для transferWithAuthorization
    this.types = {
      TransferWithAuthorization: [
        { name: "from", type: "address" },
        { name: "to", type: "address" },
        { name: "value", type: "uint256" },
        { name: "validAfter", type: "uint256" },
        { name: "validBefore", type: "uint256" },
        { name: "nonce", type: "bytes32" }
      ]
    };
  }

  /**
   * Генерация nonce с destination информацией для CCTP
   * @param userAddress Address of the user
   * @param destinationDomain CCTP destination domain (e.g., 1 for Ethereum, 2 for Avalanche)
   * @param destinationAddress Destination address on target chain
   */
  generateDestinationNonce(userAddress, destinationDomain, destinationAddress) {
    const timestamp = Math.floor(Date.now() / 1000);
    
    // Encode destination info in nonce
    // First 4 bytes: destination domain
    // Next 20 bytes: destination address (if Ethereum address)
    // Last 8 bytes: timestamp for uniqueness
    const nonce = ethers.utils.solidityPack(
      ["uint32", "address", "uint64"],
      [destinationDomain, destinationAddress, timestamp]
    );
    
    return nonce;
  }

  /**
   * Генерация безопасного nonce с адресом пользователя и chain ID (старый метод)
   */
  generateSecureNonce(userAddress) {
    const timestamp = Math.floor(Date.now() / 1000);
    const random = ethers.utils.randomBytes(16);
    
    // Включаем адрес пользователя, chain ID, timestamp и случайность
    const nonce = ethers.utils.keccak256(
      ethers.utils.defaultAbiCoder.encode(
        ["address", "uint256", "uint256", "bytes16"],
        [userAddress, this.chainId, timestamp, random]
      )
    );
    
    return nonce;
  }

  /**
   * Создание EIP3009 подписи для transferWithAuthorization
   */
  async createTransferAuthorization(signer, to, amount, validAfter = 0, validBefore = null) {
    const userAddress = await signer.getAddress();
    
    // Генерируем безопасный nonce
    const nonce = this.generateSecureNonce(userAddress);
    
    // Если validBefore не указан, устанавливаем на 1 час
    if (!validBefore) {
      validBefore = Math.floor(Date.now() / 1000) + 3600;
    }
    
    // Данные для подписи
    const value = {
      from: userAddress,
      to: to,
      value: amount,
      validAfter: validAfter,
      validBefore: validBefore,
      nonce: nonce
    };
    
    console.log('🔐 Signing EIP3009 authorization:', {
      from: userAddress,
      to: to,
      amount: ethers.utils.formatUnits(amount, 6) + ' USDC',
      nonce: nonce.substring(0, 10) + '...'
    });
    
    // Создаем подпись
    const signature = await signer._signTypedData(this.domain, this.types, value);
    const { v, r, s } = ethers.utils.splitSignature(signature);
    
    return {
      from: userAddress,
      to: to,
      value: amount,
      validAfter: validAfter,
      validBefore: validBefore,
      nonce: nonce,
      v: v,
      r: r,
      s: s
    };
  }

  /**
   * Создание EIP3009 подписи с destination информацией для CCTP
   */
  async createCCTPTransferAuthorization(
    signer, 
    to, 
    amount, 
    destinationDomain, 
    destinationAddress, 
    validAfter = 0, 
    validBefore = null
  ) {
    const userAddress = await signer.getAddress();
    
    // Генерируем nonce с destination информацией
    const nonce = this.generateDestinationNonce(userAddress, destinationDomain, destinationAddress);
    
    // Если validBefore не указан, устанавливаем на 1 час
    if (!validBefore) {
      validBefore = Math.floor(Date.now() / 1000) + 3600;
    }
    
    // Данные для подписи
    const value = {
      from: userAddress,
      to: to,
      value: amount,
      validAfter: validAfter,
      validBefore: validBefore,
      nonce: nonce
    };
    
    console.log('🔐 Signing CCTP EIP3009 authorization:', {
      from: userAddress,
      to: to,
      amount: ethers.utils.formatUnits(amount, 6) + ' USDC',
      destinationDomain: destinationDomain,
      destinationAddress: destinationAddress,
      nonce: nonce.substring(0, 10) + '...'
    });
    
    // Создаем подпись
    const signature = await signer._signTypedData(this.domain, this.types, value);
    const { v, r, s } = ethers.utils.splitSignature(signature);
    
    return {
      from: userAddress,
      to: to,
      value: amount,
      validAfter: validAfter,
      validBefore: validBefore,
      nonce: nonce,
      destinationDomain: destinationDomain,
      destinationAddress: destinationAddress,
      v: v,
      r: r,
      s: s
    };
  }

  /**
   * Проверка статуса nonce (использован ли уже)
   */
  async checkNonceStatus(nonce, authorizer) {
    const usdcContract = new ethers.Contract(
      this.usdcAddress,
      ['function authorizationState(address authorizer, bytes32 nonce) view returns (bool)'],
      this.provider
    );
    
    return await usdcContract.authorizationState(authorizer, nonce);
  }
}

// Пример использования
async function example() {
  // Настройка
  const provider = new ethers.providers.Web3Provider(window.ethereum);
  const signer = provider.getSigner();
  const usdcAddress = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // USDC на BASE
  const cctpContractAddress = "0x..."; // Адрес нашего CCTP контракта
  
  // Создаем signer
  const eip3009 = new EIP3009Signer(provider, usdcAddress, 8453);
  
  // Сумма для перевода (100 USDC)
  const amount = ethers.utils.parseUnits("100", 6);
  
  try {
    // 1. Создаем EIP3009 подпись
    const authorization = await eip3009.createTransferAuthorization(
      signer,
      cctpContractAddress, // to - наш CCTP контракт
      amount
    );
    
    console.log('✅ EIP3009 Authorization created:', authorization);
    
    // 2. Вызываем transferAndBurn на нашем контракте
    const cctpContract = new ethers.Contract(
      cctpContractAddress,
      ['function transferAndBurn(address,uint256,uint256,uint256,bytes32,uint8,bytes32,bytes32) returns (uint64)'],
      signer
    );
    
    const tx = await cctpContract.transferAndBurn(
      authorization.from,
      authorization.value,
      authorization.validAfter,
      authorization.validBefore,
      authorization.nonce,
      authorization.v,
      authorization.r,
      authorization.s
    );
    
    console.log('🔥 Transfer and Burn transaction:', tx.hash);
    
    const receipt = await tx.wait();
    console.log('✅ Transaction confirmed:', receipt);
    
  } catch (error) {
    console.error('❌ Error:', error);
  }
}

export { EIP3009Signer, example };
