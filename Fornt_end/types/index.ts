export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
}

export interface StatItem {
  label: string;
  value: string;
  description: string;
}

export interface MemoryItem {
  title: string;
  detail: string;
  date: string;
}

export interface ProfileTrait {
  title: string;
  value: string;
  tone: 'strength' | 'growth' | 'focus';
}
