import { ChatShell } from '@/components/Chat/ChatShell';

export default function ChatPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-soft backdrop-blur-xl">
        <h1 className="text-2xl font-semibold text-white">AI Chat assistant</h1>
        <p className="mt-2 text-slate-400">Ask questions, refine routines, and get instant AI guidance.</p>
      </div>
      <ChatShell />
    </div>
  );
}
