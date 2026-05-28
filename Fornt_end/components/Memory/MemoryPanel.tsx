import { MemoryItem } from '@/types';

interface MemoryPanelProps {
  items: MemoryItem[];
}

export const MemoryPanel = ({ items }: MemoryPanelProps) => {
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.title} className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-6 shadow-soft backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-lg font-semibold text-white">{item.title}</p>
              <p className="mt-2 text-sm text-slate-400">{item.detail}</p>
            </div>
            <span className="rounded-full bg-slate-900/80 px-3 py-1 text-xs uppercase tracking-[0.24em] text-slate-400">{item.date}</span>
          </div>
        </div>
      ))}
    </div>
  );
};
