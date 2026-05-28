import Link from 'next/link';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/chat', label: 'Chat' },
  { href: '/memory', label: 'Memory' },
  { href: '/profile', label: 'Profile' },
  { href: '/settings', label: 'Settings' }
];

export const AppShell = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col gap-6 px-5 py-5 lg:px-10 lg:py-8">
        <header className="flex flex-col gap-5 rounded-[2rem] border border-white/10 bg-slate-950/80 p-5 shadow-soft backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-violet-300/90">AI Life Assistant</p>
            <h1 className="mt-2 text-3xl font-semibold text-white sm:text-4xl">Modern AI productivity for daily flow.</h1>
          </div>
          <nav className="flex flex-wrap items-center gap-3">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-2xl border border-white/10 bg-slate-900/70 px-4 py-2 text-sm text-slate-200 transition hover:border-violet-400/40 hover:bg-slate-800"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>

        <main className="flex w-full flex-col gap-6">{children}</main>
      </div>
    </div>
  );
};
