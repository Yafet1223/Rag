interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export const Input = ({ label, className, ...props }: InputProps) => {
  return (
    <label className="block text-sm text-slate-200">
      <span className="mb-2 inline-block font-medium text-slate-300">{label}</span>
      <input
        className={
          'w-full rounded-2xl border border-slate-800 bg-slate-900/95 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-400/20 ' +
          (className ?? '')
        }
        {...props}
      />
    </label>
  );
};
