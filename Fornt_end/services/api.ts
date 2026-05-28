import type { Message } from '@/types';

export const fetchChatResponse = async (message: string): Promise<Message> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: `This is a demo reply to: ${message}`,
        createdAt: new Date().toISOString()
      });
    }, 800);
  });
};

export const fetchDashboardStats = async () => {
  return {
    uptime: '21 days',
    streak: '12 sessions',
    focus: '82%',
    tasks: '8 completed'
  };
};
