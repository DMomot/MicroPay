// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// CCTP TokenMinter interface
interface ITokenMinter {
    function burn(uint256 amount) external returns (uint64);
    
    function depositForBurn(
        uint256 amount,
        uint32 destinationDomain,
        bytes32 mintRecipient,
        address burnToken
    ) external returns (uint64);
    
    function burnLimitsPerMessage(address token) external view returns (uint256);
    
    function localToken() external view returns (address);
}
