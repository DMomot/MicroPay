// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IEIP3009.sol";
import "./interfaces/ITokenMinter.sol";

/**
 * @title CCTPTransferBurn
 * @dev Contract that combines EIP3009 transfer with CCTP burn in a single transaction
 */
contract CCTPTransferBurn is ReentrancyGuard, Ownable {
    IEIP3009 public immutable usdcToken;
    ITokenMinter public immutable tokenMinter;
    
    event TransferAndBurn(
        address indexed from,
        address indexed to,
        uint256 amount,
        uint32 destinationDomain,
        bytes32 destinationAddress,
        uint64 burnNonce
    );
    
    constructor(address _usdcToken, address _tokenMinter) {
        usdcToken = IEIP3009(_usdcToken);
        tokenMinter = ITokenMinter(_tokenMinter);
    }
    
    /**
     * @dev Extract destination info from encoded nonce
     * @param nonce Encoded nonce containing destination domain and address
     * @return destinationDomain CCTP destination domain
     * @return destinationAddress Destination address on target chain
     */
    function extractDestinationFromNonce(bytes32 nonce) 
        public 
        pure 
        returns (uint32 destinationDomain, bytes32 destinationAddress) 
    {
        // Extract first 4 bytes as destination domain
        destinationDomain = uint32(bytes4(nonce));
        
        // Extract remaining 28 bytes as destination address (padded)
        destinationAddress = bytes32(uint256(nonce) << 32);
    }
    
    /**
     * @dev Execute EIP3009 transfer and CCTP burn in one transaction
     * @param from Address to transfer from
     * @param amount Amount to transfer and burn
     * @param validAfter Timestamp after which the authorization is valid
     * @param validBefore Timestamp before which the authorization is valid
     * @param nonce Unique nonce for the authorization (contains destination info)
     * @param destinationDomain CCTP destination domain (chain ID mapping)
     * @param destinationAddress Destination address on target chain
     * @param v Recovery byte of the signature
     * @param r First 32 bytes of the signature
     * @param s Second 32 bytes of the signature
     */
    function transferAndBurn(
        address from,
        uint256 amount,
        uint256 validAfter,
        uint256 validBefore,
        bytes32 nonce,
        uint32 destinationDomain,
        bytes32 destinationAddress,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external nonReentrant returns (uint64) {
        // Execute EIP3009 transfer to this contract
        usdcToken.transferWithAuthorization(
            from,
            address(this),
            amount,
            validAfter,
            validBefore,
            nonce,
            v,
            r,
            s
        );
        
        // Approve TokenMinter to spend USDC
        usdcToken.approve(address(tokenMinter), amount);
        
        // Burn and bridge tokens via CCTP to destination
        uint64 burnNonce = tokenMinter.depositForBurn(
            amount,
            destinationDomain,
            destinationAddress,
            address(usdcToken)
        );
        
        emit TransferAndBurn(from, address(this), amount, destinationDomain, destinationAddress, burnNonce);
        
        return burnNonce;
    }
    
    /**
     * @dev Execute EIP3009 transfer and CCTP burn with destination extracted from nonce
     * @param from Address to transfer from
     * @param amount Amount to transfer and burn
     * @param validAfter Timestamp after which the authorization is valid
     * @param validBefore Timestamp before which the authorization is valid
     * @param nonce Encoded nonce containing destination info
     * @param v Recovery byte of the signature
     * @param r First 32 bytes of the signature
     * @param s Second 32 bytes of the signature
     */
    function transferAndBurnFromNonce(
        address from,
        uint256 amount,
        uint256 validAfter,
        uint256 validBefore,
        bytes32 nonce,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external nonReentrant returns (uint64) {
        // Extract destination info from nonce
        (uint32 destinationDomain, bytes32 destinationAddress) = extractDestinationFromNonce(nonce);
        
        // Execute EIP3009 transfer to this contract
        usdcToken.transferWithAuthorization(
            from,
            address(this),
            amount,
            validAfter,
            validBefore,
            nonce,
            v,
            r,
            s
        );
        
        // Approve TokenMinter to spend USDC
        usdcToken.approve(address(tokenMinter), amount);
        
        // Burn and bridge tokens via CCTP to destination
        uint64 burnNonce = tokenMinter.depositForBurn(
            amount,
            destinationDomain,
            destinationAddress,
            address(usdcToken)
        );
        
        emit TransferAndBurn(from, address(this), amount, destinationDomain, destinationAddress, burnNonce);
        
        return burnNonce;
    }
    
    /**
     * @dev Emergency function to recover any stuck tokens (only owner)
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        // Emergency nonce - simple timestamp + sender
        bytes32 emergencyNonce = keccak256(abi.encodePacked(block.timestamp, msg.sender));
        
        IEIP3009(token).transferWithAuthorization(
            address(this),
            owner(),
            amount,
            0,
            type(uint256).max,
            emergencyNonce,
            0,
            bytes32(0),
            bytes32(0)
        );
    }
}
