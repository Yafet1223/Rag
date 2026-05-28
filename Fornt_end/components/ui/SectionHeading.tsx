interface SectionHeadingProps {
  title: string;
  description?: string;
}

export const SectionHeading = ({ title, description }: SectionHeadingProps) => {
  return (
    <div className="space-y-1">
      <p className="text-sm uppercase tracking-[0.24em] text-violet-300/80">{title}</p>
      {description ? <p className="text-base text-slate-300">{description}</p> : null}
    </div>
  );
};
