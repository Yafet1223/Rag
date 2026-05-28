import type { Message } from '@/types';
import { formatTime } from '@/lib/format';

interface ChatBubbleProps {
  message: Message;
}

export const ChatBubble = ({ message }: ChatBubbleProps) => {
  const isUser = message.role === 'user';

  return (
    <div className={`group flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[78%] rounded-[1.5rem] px-5 py-4 text-sm leading-6 ${isUser ? 'bg-violet-500/15 text-slate-100' : 'bg-slate-900/90 text-slate-200'}`}>
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        <div className="mt-3 flex items-center justify-end text-[11px] uppercase tracking-[0.24em] text-slate-500">
          {formatTime(message.createdAt)}
        </div>
      </div>
    </div>
  );
};
