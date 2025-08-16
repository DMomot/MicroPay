import React, { useState, useEffect, useRef } from 'react';
import { WalletConnection } from './WalletConnection';
import './App.css';

interface Message {
  id: number;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: 'Привет! Я AI бот на основе Gemini. Чем могу помочь?',
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
      // Step 1: Summarize user message to short prompt
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const summarizeResponse = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: `You are a prompt optimizer. Take this user message and reduce it to a short, clear search prompt (max 10 words) that captures the core intent. Focus on key terms and actions. User message: "${inputMessage}"` 
        }),
      });

      if (!summarizeResponse.ok) {
        throw new Error('Failed to summarize prompt');
      }

      const summarizeData = await summarizeResponse.json();
      const shortPrompt = summarizeData.response;

      // Step 2: Search for agents with the short prompt
      const searchResponse = await fetch('http://ai_finder.railway.internal/search', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: shortPrompt,
          max_results: 10,
          min_rating: 0.5
        }),
      });

      if (!searchResponse.ok) {
        throw new Error('Failed to search agents');
      }

      const agentsData = await searchResponse.json();
      
      const botMessage: Message = {
        id: Date.now() + 1,
        content: `Found ${agentsData.length} suitable agents for: "${shortPrompt}"\n\n${JSON.stringify(agentsData, null, 2)}`,
        isUser: false,
        timestamp: new Date()
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

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>AI Бот</h1>
          <p>Powered by Gemini</p>
          <WalletConnection />
        </header>
        
        <div className="chat-container">
          <div className="chat-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.isUser ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  {message.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="typing-indicator">
                <div className="typing-text">AI печатает</div>
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
                placeholder="Введите сообщение..."
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
