"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Send, ArrowRight, Brain, Clock } from 'lucide-react';
import { fetchApi } from '@/lib/api-client';

interface Message {
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
  suggestions?: string[];
  sources?: string[];
}

interface AIAssistantProps {
  title?: string;
  context?: any;
  initialMessage?: string;
}

export function AIAssistant({ title = "Ask Operations", context, initialMessage }: AIAssistantProps) {
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([
      { 
        role: 'ai', 
        text: initialMessage || "I'm monitoring the supply chain. What would you like to know?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, [initialMessage]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = { 
      role: 'user', 
      text, 
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    };
    setMessages(prev => [...prev, userMsg]);
    setChatInput('');
    setIsTyping(true);

    try {
      const res = await fetchApi<{response: string, suggested_actions?: string[], sources?: string[]}>('/chat/query', {
        method: 'POST',
        body: JSON.stringify({ 
          message: text,
          context: context ? { active_context: context } : undefined
        })
      });

      const aiMsg: Message = { 
        role: 'ai', 
        text: res.response, 
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestions: res.suggested_actions,
        sources: res.sources
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: "Sorry, I'm having trouble connecting to the intelligence engine.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-2 text-indigo-600">
          <Brain size={18} />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900">{title}</h2>
        </div>
        <div className="flex items-center gap-1 text-[10px] font-bold text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100 animate-pulse">
          <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
          LIVE
        </div>
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-5 scroll-smooth">
        {messages.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[95%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
              msg.role === 'ai' 
                ? 'bg-slate-50 text-slate-700 border border-slate-100 rounded-tl-none' 
                : 'bg-indigo-600 text-white border border-indigo-500 rounded-tr-none'
            }`}>
              {msg.role === 'ai' && (
                <div className="flex items-center gap-1.5 mb-1.5 opacity-50">
                   <Sparkles size={12} className="text-indigo-500" />
                   <span className="text-[10px] font-bold uppercase tracking-widest">Intelligence</span>
                </div>
              )}
              <p className="leading-relaxed">{msg.text}</p>
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-200/50 flex flex-wrap gap-2">
                   <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter self-center">Sources:</span>
                   {msg.sources.map((src, sIdx) => (
                     <span key={sIdx} className="text-[9px] bg-white/50 border border-slate-200 text-slate-500 px-1.5 py-0.5 rounded-sm font-medium">
                       {src}
                     </span>
                   ))}
                </div>
              )}

              <div className={`text-[10px] mt-2 opacity-40 font-medium ${msg.role === 'user' ? 'text-right' : ''}`}>
                {msg.timestamp}
              </div>
            </div>
            
            {msg.suggestions && msg.suggestions.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {msg.suggestions.map((suggestion, idx) => (
                  <button 
                    key={idx}
                    onClick={() => handleSendMessage(suggestion)}
                    className="text-[11px] font-medium bg-white border border-slate-200 text-slate-600 px-3 py-1.5 rounded-full hover:border-indigo-400 hover:text-indigo-600 transition-all flex items-center gap-1 group shadow-sm"
                  >
                    {suggestion}
                    <ArrowRight size={10} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex flex-col items-start">
            <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-tl-none px-4 py-2.5 shadow-sm">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"></span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-slate-100 bg-slate-50/30">
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage(chatInput);
          }}
          className="relative"
        >
          <input 
            type="text" 
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Ask a question..." 
            className="w-full bg-white border border-slate-200 rounded-xl pl-4 pr-10 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm"
          />
          <button 
            type="submit"
            disabled={!chatInput.trim() || isTyping}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors disabled:opacity-30"
          >
            <Send size={16} />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-400 mt-2 font-medium uppercase tracking-tighter">
          Seed OI Real-time Intelligence
        </p>
      </div>
    </div>
  );
}
