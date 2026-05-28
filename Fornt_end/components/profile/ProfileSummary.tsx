import { ProfileTrait } from '@/types';
import { Badge } from '@/components/ui/Badge';

interface ProfileSummaryProps {
  traits: readonly ProfileTrait[];
}

export const ProfileSummary = ({ traits }: ProfileSummaryProps) => {
  return (
    <div className="space-y-6 rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-violet-300/90">Profile traits</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Strengths and growth signals</h2>
        </div>
        <Badge label="Personalized" tone="success" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {traits.map((trait) => (
          <div key={trait.title} className="rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-5">
            <p className="text-sm uppercase tracking-[0.24em] text-slate-400">{trait.title}</p>
            <p className="mt-3 text-2xl font-semibold text-white">{trait.value}</p>
            <p className="mt-2 text-sm text-slate-400">{trait.tone === 'strength' ? 'Key strength' : trait.tone === 'focus' ? 'Focus area' : 'Growth area'}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
