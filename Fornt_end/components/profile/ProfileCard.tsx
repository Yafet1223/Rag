import { Badge } from '@/components/ui/Badge';

interface ProfileCardProps {
  title: string;
  value: string;
  tone: 'strength' | 'growth' | 'focus';
}

const toneMap = {
  strength: { label: 'Strength', color: 'success' },
  growth: { label: 'Growth', color: 'warning' },
  focus: { label: 'Focus', color: 'neutral' }
};

export const ProfileCard = ({ title, value, tone }: ProfileCardProps) => {
  return (
    <div className="rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-5 shadow-soft">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-300">{title}</p>
        <Badge label={toneMap[tone].label} tone={toneMap[tone].color} />
      </div>
      <p className="mt-4 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
};
