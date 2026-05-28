import { MemoryPanel } from '@/components/Memory/MemoryPanel';
import { SectionHeading } from '@/components/ui/SectionHeading';

const insights = [
  { title: 'Morning review', detail: 'Saved your energy peak habits and self-reflection notes.', date: 'May 24' },
  { title: 'Study session debrief', detail: 'Captured focus triggers and distraction patterns.', date: 'May 23' },
  { title: 'Weekly behavior check', detail: 'Reviewed consistency and habit alignment.', date: 'May 21' }
];

export default function MemoryPage() {
  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
        <SectionHeading title="Memory Visualization" description="Inspect your stored habits, recent events, and retrieved context." />
        <p className="mt-5 text-sm leading-7 text-slate-300">
          This panel helps you stay transparent with the AI assistant by exposing the signals it uses for recommendations.
        </p>
      </section>

      <MemoryPanel items={insights} />
    </div>
  );
}
