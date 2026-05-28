interface StatCardProps {
  label: string;
  value: string;
  detail: string;
}

export const StatCard = ({ label, value, detail }: StatCardProps) => {
  return (
    <div className="rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-5 shadow-soft">
      <p className="text-sm uppercase tracking-[0.24em] text-violet-300/90">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
      <p className="mt-2 text-sm text-slate-400">{detail}</p>
    </div>
  );
};
