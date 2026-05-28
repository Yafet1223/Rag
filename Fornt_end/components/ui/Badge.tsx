interface BadgeProps {
  label: string;
  tone?: 'neutral' | 'success' | 'warning';
}

const toneClasses: Record<string, string> = {
  neutral: 'bg-slate-800/90 text-slate-200',
  success: 'bg-emerald-500/10 text-emerald-300 ring-1 ring-emerald-400/20',
  warning: 'bg-amber-500/10 text-amber-300 ring-1 ring-amber-400/20'
};

export const Badge = ({ label, tone = 'neutral' }: BadgeProps) => {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${toneClasses[tone]}`}>{label}</span>;
};
