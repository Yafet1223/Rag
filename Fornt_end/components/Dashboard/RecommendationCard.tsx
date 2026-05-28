interface RecommendationCardProps {
  title: string;
  summary: string;
  note: string;
}

export const RecommendationCard = ({ title, summary, note }: RecommendationCardProps) => {
  return (
    <div className="rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-5 shadow-soft transition hover:border-violet-400/20">
      <p className="text-sm font-semibold text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-300">{summary}</p>
      <p className="mt-4 text-xs uppercase tracking-[0.24em] text-slate-500">{note}</p>
    </div>
  );
};
