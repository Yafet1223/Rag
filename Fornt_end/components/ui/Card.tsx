import clsx from 'classnames';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'surface' | 'panel';
}

export const Card = ({ variant = 'surface', className, ...props }: CardProps) => {
  return (
    <div
      className={clsx(
        'rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6 shadow-soft backdrop-blur-xl',
        variant === 'panel' && 'bg-slate-900/80',
        className
      )}
      {...props}
    />
  );
};
