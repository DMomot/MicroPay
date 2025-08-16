import React, { useState, useEffect, useRef } from 'react';
import { wrapFetchWithPayment } from 'x402-fetch';
import { createWalletClient, custom } from 'viem';
import { base } from 'viem/chains';
import AnalysisDisplay from './AnalysisDisplay';

import './App.css';

// Extend Window interface for ethereum
declare global {
  interface Window {
    ethereum?: any;
  }
}

interface Agent {
  name?: string;
  resource: string;
  description: string;
  price_usdc: string;
  network: string;
  rating: number;
  timeout_seconds?: number;
  asset_address?: string;
  pay_to_address?: string;
}

interface Message {
  id: number;
  content: string;
  isUser: boolean;
  timestamp: Date;
  agents?: Agent[];
  optimizedPrompt?: string;
}

function App() {
  // Wallet state
  const [walletAddress, setWalletAddress] = useState<string>('');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [currentNetwork, setCurrentNetwork] = useState<string>('');

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: 'Hello! I am an AI bot powered by Gemini. How can I help you?',
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Network checking function
  const checkNetwork = async () => {
    if (window.ethereum) {
      try {
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        const networkNames: { [key: string]: string } = {
          '0x2105': 'Base Mainnet',
          '0x14a34': 'Base Sepolia',
          '0x1': 'Ethereum Mainnet',
          '0x89': 'Polygon'
        };
        const networkName = networkNames[chainId] || `Unknown (${chainId})`;
        setCurrentNetwork(networkName);
        
        // Check if we're on Base network (required for x402)
        if (chainId !== '0x2105' && chainId !== '0x14a34') {
          console.warn('⚠️ Not on Base network. x402 payments require Base network.');
        }
        
        return chainId;
      } catch (error) {
        console.error('Error checking network:', error);
        return null;
      }
    }
    return null;
  };

  // MetaMask functions
  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({
          method: 'eth_requestAccounts',
        });
        setWalletAddress(accounts[0]);
        setIsConnected(true);
        await checkNetwork();
      } catch (error) {
        console.error('Error connecting to MetaMask:', error);
      }
    } else {
      alert('MetaMask is not installed!');
    }
  };

  const disconnectWallet = () => {
    setWalletAddress('');
    setIsConnected(false);
  };



  // Check if wallet is already connected
  useEffect(() => {
    const checkConnection = async () => {
      if (typeof window.ethereum !== 'undefined') {
        try {
          const accounts = await window.ethereum.request({
            method: 'eth_accounts',
          });
          if (accounts.length > 0) {
            setWalletAddress(accounts[0]);
            setIsConnected(true);
            await checkNetwork();
          } else {
            await checkNetwork(); // Check network even if not connected
          }
        } catch (error) {
          console.error('Error checking connection:', error);
        }
      }
    };
    checkConnection();

    // Listen for network changes
    if (window.ethereum) {
      window.ethereum.on('chainChanged', () => {
        checkNetwork();
      });
      
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length === 0) {
          setIsConnected(false);
          setWalletAddress('');
        } else {
          setWalletAddress(accounts[0]);
          setIsConnected(true);
        }
      });
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error('Network error');
      }

      const data = await response.json();
      
      // Create main response message
      let content = data.response;
      
      // Prepare agents data for the message
      let agents: Agent[] = [];
      let optimizedPrompt = '';
      
              if (data.needs_agents && data.agents && data.agents.agents) {
          const actualAgentsCount = data.agents.agents.length;
          if (actualAgentsCount > 0) {
            agents = data.agents.agents;
            optimizedPrompt = data.optimized_prompt;
            content += `\n\n🤖 **Found ${actualAgentsCount} suitable agents for:** "${data.optimized_prompt}"`;
          }
        }
      
      // Add error message if agent search failed
      if (data.agent_search_error) {
        content += `\n\n⚠️ Agent search error: ${data.agent_search_error}`;
      }

      const botMessage: Message = {
        id: Date.now() + 1,
        content: content,
        isUser: false,
        timestamp: new Date(),
        agents: agents,
        optimizedPrompt: optimizedPrompt
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        content: 'Sorry, an error occurred. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const AgentCard = ({ agent }: { agent: Agent }) => {
    const name = agent.name || 'Unknown Agent';
    const price = agent.price_usdc ? `${(parseInt(agent.price_usdc) / 1000000).toFixed(2)} USDC` : 'Free';
    const [isPaying, setIsPaying] = useState(false);
    
    const handlePay = async () => {
      if (!isConnected) {
        alert('Please connect your wallet first!');
        return;
      }
      
      if (!walletAddress) {
        alert('❌ Wallet not connected. Please connect your wallet first.');
        return;
      }
      
      setIsPaying(true);
      
      try {
        console.log('🧪 Using YOUR MetaMask wallet...');
        console.log('🔍 Your wallet address:', walletAddress);
        console.log('🚀 Calling agent API with x402-fetch:', agent.resource);
        console.log('💰 Expected price:', price);
        console.log('🌐 Network:', agent.network || 'base');
        
        // Create account object for MetaMask (transferred from EIP3009Test)
        const account = {
          address: walletAddress as `0x${string}`,
          type: 'json-rpc' as const,
        };

        // Create wallet client using YOUR MetaMask with account (transferred from EIP3009Test)
        const client = createWalletClient({
          account,
          transport: custom(window.ethereum),
          chain: base,
        });

        console.log('🔍 MetaMask client created:', client);
        console.log('💰 Using your real wallet with USDC balance!');

        // Wrap fetch with payment handling ТОЧНО как в EIP3009Test
        const fetchWithPay = wrapFetchWithPayment(fetch, client);

        console.log('🚀 Making request with x402-fetch (should handle payment automatically)...');
        
        // Make request to agent API (x402-fetch handles payment automatically)
        const response = await fetchWithPay(agent.resource, {
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
        
        // Payment successful - no need for alert, response will be shown in chat
        
        // Add response to chat
        const agentMessage: Message = {
          id: Date.now() + 1,
          content: responseData,
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, agentMessage]);
        
      } catch (error: any) {
        console.error('❌ x402 payment failed:', error);
        console.error('Agent resource:', agent.resource);
        console.error('Full error:', error);
        
        let errorMessage = error?.message || error;
        
        // Check for specific error types (enhanced error handling)
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('CORS')) {
          errorMessage = `CORS error - Сервер ${agent.resource} не настроен для браузерных запросов.\nЭто проблема конфигурации сервера, не фронтенда.`;
        } else if (errorMessage.includes('User rejected') || errorMessage.includes('User denied')) {
          errorMessage = 'Пользователь отклонил подписание транзакции';
        } else if (errorMessage.includes('insufficient funds')) {
          errorMessage = 'Недостаточно средств для оплаты';
        } else if (errorMessage.includes('network')) {
          errorMessage = 'Ошибка сети. Проверьте подключение к правильной сети (Base)';
        } else if (errorMessage.includes('signature') || errorMessage.includes('sign')) {
          errorMessage = `Ошибка подписания EIP3009 транзакции: ${errorMessage}`;
        } else if (errorMessage.includes('402')) {
          errorMessage = `Сервер вернул 402 - возможно проблема с обработкой платежа на сервере`;
        }
        
        alert(`❌ x402 payment failed:\n${errorMessage}\n\nURL: ${agent.resource}\n\nCheck console for details.`);
      } finally {
        setIsPaying(false);
      }
    };
    
    return (
      <div className="agent-card">
        <div className="agent-header">
          <h3>{name}</h3>
        </div>
        <p className="agent-description">{agent.description}</p>
        <div className="agent-details">
          <span className="agent-price">{price}</span>
          <button 
            className="pay-button" 
            onClick={handlePay}
            disabled={!isConnected || isPaying}
          >
            {isPaying ? 'Calling...' : 'Pay'}
          </button>
        </div>
      </div>
    );
  };

  const WalletButton = () => {
    if (isConnected && walletAddress) {
      const isBaseNetwork = currentNetwork.includes('Base');
      return (
        <div className="wallet-info">
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span className="wallet-address">
              {`${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`}
            </span>
            <span 
              className="network-info" 
              style={{ 
                fontSize: '12px', 
                color: isBaseNetwork ? '#28a745' : '#dc3545',
                marginTop: '2px'
              }}
            >
              {currentNetwork || 'Unknown Network'}
              {!isBaseNetwork && ' ⚠️'}
            </span>
          </div>
          <button onClick={disconnectWallet} className="disconnect-btn">
            Disconnect
          </button>
        </div>
      );
    }

    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
        <button 
          onClick={connectWallet} 
          className="connect-wallet-btn"
        >
          Connect MetaMask
        </button>
        {currentNetwork && (
          <span 
            style={{ 
              fontSize: '12px', 
              color: '#666', 
              marginTop: '5px' 
            }}
          >
            Current: {currentNetwork}
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="app">
      <div className="container">
        <WalletButton />
        <header className="header">
          <div className="header-content">
            <div className="header-text">
              <h1>AI Agent Finder</h1>
              <p>Powered by Gemini</p>
            </div>
          </div>
        </header>
        
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  {/* Always use AnalysisDisplay for bot messages, regular text for user messages */}
                  {message.isUser ? (
                    message.content.split('\n').map((line, index) => (
                      <React.Fragment key={index}>
                        {line}
                        {index < message.content.split('\n').length - 1 && <br />}
                      </React.Fragment>
                    ))
                  ) : (
                    <AnalysisDisplay content={message.content} />
                  )}
                </div>
                {message.agents && message.agents.length > 0 && (
                  <div className="agents-container">
                    {message.agents.map((agent, index) => (
                      <AgentCard key={index} agent={agent} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="typing-indicator">
                <div className="typing-text">AI is typing</div>
                <div className="typing-dots">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chat-input-container">
            <div className="chat-input">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter message..."
                disabled={isLoading}
                autoComplete="off"
              />
              <button 
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="send-button"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="m22 2-7 20-4-9-9-4z"/>
                  <path d="m22 2-11 11"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
