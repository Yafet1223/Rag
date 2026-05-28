"use client";

import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { ChatBubble } from './ChatBubble';
import { useAutoScroll } from '@/hooks/useAutoScroll';
import { fetchChatResponse } from '@/services/api';
import type { Message } from '@/types';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

const initialMessages: Message[] = [
  {
    id: 'assistant-1',
    role: 'assistant',
    content: 'Welcome back. Tell me what you want to focus on today, and I will help you build momentum.',
    createdAt: new Date().toISOString()
  }
];

export const ChatShell = () => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useAutoScroll();

  const lastMessage = messages[messages.length - 1];

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      createdAt: new Date().toISOString()
    };

    setMessages((current) => [...current, userMessage]);
    setInput('');
    setIsTyping(true);

    const response = await fetchChatResponse(userMessage.content);
    setTimeout(() => {
      setMessages((current) => [...current, response]);
      setIsTyping(false);
    }, 850);
  };

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, scrollRef]);

  const history = useMemo(
    () => [
      { id: 'history-1', title: 'Weekly focus plan', summary: 'Build a study routine for Monday.' },
      { id: 'history-2', title: 'Deep work session', summary: 'Stay on task for 90 minutes.' },
      { id: 'history-3', title: 'Habit insight', summary: 'Track screen time and productivity.' }
    ],
    []
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"
    >
      <div className="space-y-5">
        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-soft backdrop-blur-xl">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-violet-300 uppercase tracking-[0.24em]">AI Chat</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Real-time assistant for your daily flow</h2>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge label="Streaming" tone="success" />
              <Badge label="Markdown" tone="neutral" />
            </div>
          </div>

          <div className="mt-6 space-y-4 rounded-[2rem] border border-white/5 bg-slate-950/90 p-5">
            <div className="space-y-4 overflow-hidden rounded-[1.75rem] bg-slate-900/70 p-4">
              {messages.map((message) => (
                <ChatBubble message={message} key={message.id} />
              ))}
              {isTyping ? (
                <div className="inline-flex items-center gap-2 rounded-[1.5rem] bg-slate-900/90 px-4 py-3 text-slate-300">
                  <span className="inline-flex h-2.5 w-2.5 animate-pulse rounded-full bg-violet-400" />
                  AI is typing...
                </div>
              ) : null}
            </div>

            <div ref={scrollRef} />
          </div>

          <div className="mt-6 flex flex-col gap-3 rounded-[1.75rem] border border-white/10 bg-slate-900/75 p-4 sm:flex-row sm:items-center">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              rows={2}
              placeholder="Ask your assistant anything..."
              className="min-h-[80px] w-full resize-none rounded-2xl border border-slate-800 bg-slate-950/95 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20"
            />
            <Button onClick={handleSend} className="w-full sm:w-auto sm:shrink-0">
              Send message
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-soft backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-violet-300 uppercase tracking-[0.24em]">Conversation history</p>
              <h3 className="mt-2 text-xl font-semibold text-white">Recent sessions</h3>
            </div>
            <Badge label="Saved" tone="neutral" />
          </div>
          <div className="mt-6 space-y-4">
            {history.map((item) => (
              <div key={item.id} className="rounded-3xl border border-white/10 bg-slate-900/80 p-4">
                <p className="font-semibold text-slate-100">{item.title}</p>
                <p className="mt-1 text-sm text-slate-400">{item.summary}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-soft backdrop-blur-xl">
          <p className="text-violet-300 uppercase tracking-[0.24em]">Insights</p>
          <div className="mt-5 grid gap-4">
            <div className="rounded-3xl bg-slate-900/80 p-4">
              <p className="text-sm text-slate-300">Focus streak</p>
              <p className="mt-2 text-3xl font-semibold text-white">8 days</p>
            </div>
            <div className="rounded-3xl bg-slate-900/80 p-4">
              <p className="text-sm text-slate-300">Current priority</p>
              <p className="mt-2 text-xl font-semibold text-white">Deep work session</p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
