import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Agent {
  name?: string;
  resource: string;
  description: string;
  price_usdc: string;
  network: string;
  rating: number;
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
        } else {
          content += `\n\n🤖 No suitable agents found for: "${data.optimized_prompt}"`;
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
    
    return (
      <div className="agent-card">
        <div className="agent-header">
          <h3>{name}</h3>
        </div>
        <p className="agent-description">{agent.description}</p>
        <div className="agent-details">
          <span className="agent-price">{price}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <div className="container">
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
                  {message.content.split('\n').map((line, index) => (
                    <React.Fragment key={index}>
                      {line}
                      {index < message.content.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
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
