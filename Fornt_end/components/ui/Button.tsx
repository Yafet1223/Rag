import clsx from 'classnames';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost';
}

export const Button = ({ variant = 'primary', className, ...props }: ButtonProps) => {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center rounded-2xl px-4 py-2 text-sm font-semibold transition-all duration-200',
        variant === 'primary' && 'bg-violet-500 text-slate-950 shadow-soft hover:bg-violet-400',
        variant === 'ghost' && 'border border-slate-700 bg-slate-900/80 text-slate-200 hover:bg-slate-800',
        className
      )}
      {...props}
    />
  );
};
