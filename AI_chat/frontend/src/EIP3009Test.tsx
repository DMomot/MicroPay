import React, { useState } from 'react';
import { wrapFetchWithPayment } from 'x402-fetch';
import { createWalletClient, custom } from 'viem';
import { base } from 'viem/chains';

// Test component for EIP3009 signature debugging
export const EIP3009Test: React.FC<{ walletAddress: string }> = ({ walletAddress }) => {
  const [isTestingSignature, setIsTestingSignature] = useState(false);
  const [isTestingX402, setIsTestingX402] = useState(false);
  const [testResult, setTestResult] = useState<string>('');
  const [x402Result, setX402Result] = useState<string>('');

  const testEIP3009Signature = async () => {
    if (!window.ethereum || !walletAddress) {
      setTestResult('❌ MetaMask not available');
      return;
    }

    setIsTestingSignature(true);
    setTestResult('');

    try {
      // HARDCODED test data from your message
      const testTypedData = {
        domain: {
          name: "USD Coin",
          version: "2",
          chainId: 8453,
          verifyingContract: "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
        },
        message: {
          from: "0x693f7243e7577a3845364f23d856349f15571856",
          to: "0xce465c087305314f8f0ead5a450898f19efd0e03",
          value: "10000",
          validAfter: "1755362553",
          validBefore: "1755363213",
          nonce: "0x03d296ebdec497645fc70a97df8240318068f0214aa9aefbc7583997d04aaec9"
        },
        primaryType: "TransferWithAuthorization",
        types: {
          EIP712Domain: [
            { name: "name", type: "string" },
            { name: "version", type: "string" },
            { name: "chainId", type: "uint256" },
            { name: "verifyingContract", type: "address" }
          ],
          TransferWithAuthorization: [
            { name: "from", type: "address" },
            { name: "to", type: "address" },
            { name: "value", type: "uint256" },
            { name: "validAfter", type: "uint256" },
            { name: "validBefore", type: "uint256" },
            { name: "nonce", type: "bytes32" }
          ]
        }
      };

      console.log('🧪 HARDCODED test data:', testTypedData);
      console.log('🧪 JSON for signing:', JSON.stringify(testTypedData));

      const signature = await window.ethereum.request({
        method: 'eth_signTypedData_v4',
        params: [walletAddress, JSON.stringify(testTypedData)],
      });

      console.log('✅ HARDCODED signature result:', signature);
      console.log('🔍 Signature details:', {
        signature: signature,
        length: signature.length,
        r: signature.slice(0, 66),
        s: '0x' + signature.slice(66, 130),
        v: '0x' + signature.slice(130, 132)
      });
      
      // Convert signature to base64
      const signatureBase64 = btoa(signature);
      console.log('📋 Signature in base64:', signatureBase64);

      setTestResult(`✅ HARDCODED signature test successful!\n\nHex: ${signature}\n\nBase64: ${signatureBase64}\n\nThis signature should be consistent for the same data.`);

    } catch (error: any) {
      console.error('❌ Test signature failed:', error);
      setTestResult(`❌ EIP3009 signature test failed:\n${error?.message || error}`);
    } finally {
      setIsTestingSignature(false);
    }
  };

  const testX402Payment = async () => {
    if (!window.ethereum) {
      setX402Result('❌ MetaMask not available');
      return;
    }
    
    if (!walletAddress) {
      setX402Result('❌ Wallet not connected. Please connect your wallet first.');
      return;
    }

    setIsTestingX402(true);
    setX402Result('');

    try {
      console.log('🧪 Using YOUR MetaMask wallet...');
      console.log('🔍 Your wallet address:', walletAddress);
      
      // Create account object for MetaMask
      const account = {
        address: walletAddress as `0x${string}`,
        type: 'json-rpc' as const,
      };

      // Create wallet client using YOUR MetaMask with account
      const client = createWalletClient({
        account,
        transport: custom(window.ethereum),
        chain: base,
      });

      console.log('🔍 MetaMask client created:', client);
      console.log('💰 Using your real wallet with USDC balance!');

      // Wrap fetch with payment handling ТОЧНО как в примере
      const fetchWithPay = wrapFetchWithPayment(fetch, client);

      console.log('🚀 Making request with x402-fetch (should handle payment automatically)...');
      
      // Make request to paid endpoint (exactly like in the example)
      const response = await fetchWithPay('https://priceagent-production.up.railway.app/api/prices?query=Bitcoin%20price%20for%20last%month', {
        method: 'GET',
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        // Log the response body to see what the server says
        const errorBody = await response.text();
        console.log('❌ Server error response:', errorBody);
        throw new Error(`HTTP ${response.status}: ${response.statusText}\nServer response: ${errorBody}`);
      }

      const responseData = await response.text();
      console.log('📊 Response data:', responseData);

      setX402Result(`✅ SIMPLE x402-fetch payment successful!\n\nAPI Response (${response.status}):\n${responseData.slice(0, 500)}${responseData.length > 500 ? '...' : ''}\n\nPayment handled automatically by x402-fetch library!`);

    } catch (error: any) {
      console.error('❌ x402 payment failed:', error);
      setX402Result(`❌ x402 payment failed:\n${error?.message || error}\n\nCheck console for details.`);
    } finally {
      setIsTestingX402(false);
    }
  };

  return (
    <div style={{ 
      margin: '20px 0', 
      padding: '15px', 
      border: '1px solid #ddd', 
      borderRadius: '8px',
      backgroundColor: '#f9f9f9'
    }}>
      <h3>🧪 x402 Payment Testing</h3>
      <p>Test EIP3009 signature and x402 payment flow</p>
      
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button 
          onClick={testEIP3009Signature}
          disabled={isTestingSignature || !walletAddress}
          style={{
            padding: '10px 20px',
            backgroundColor: isTestingSignature ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isTestingSignature ? 'not-allowed' : 'pointer'
          }}
        >
          {isTestingSignature ? 'Testing...' : 'Test EIP3009 Signature'}
        </button>

        <button 
          onClick={testX402Payment}
          disabled={isTestingX402 || !walletAddress}
          style={{
            padding: '10px 20px',
            backgroundColor: isTestingX402 ? '#ccc' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isTestingX402 ? 'not-allowed' : 'pointer'
          }}
        >
          {isTestingX402 ? 'Sending...' : 'Test x402 Payment (Real API)'}
        </button>
      </div>

      {testResult && (
        <div style={{
          marginTop: '15px',
          padding: '10px',
          backgroundColor: testResult.startsWith('✅') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${testResult.startsWith('✅') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          whiteSpace: 'pre-wrap',
          fontSize: '14px'
        }}>
          <strong>EIP3009 Test Result:</strong><br />
          {testResult}
        </div>
      )}

      {x402Result && (
        <div style={{
          marginTop: '15px',
          padding: '10px',
          backgroundColor: x402Result.startsWith('✅') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${x402Result.startsWith('✅') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          whiteSpace: 'pre-wrap',
          fontSize: '14px'
        }}>
          <strong>x402 Payment Test Result:</strong><br />
          {x402Result}
        </div>
      )}
    </div>
  );
};
