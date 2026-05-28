import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { SectionHeading } from '@/components/ui/SectionHeading';

const cards = [
  { title: 'Chat', description: 'Ask your assistant for productivity, plans, and context.', href: '/chat' },
  { title: 'Dashboard', description: 'Track behavior, focus, and consistency at a glance.', href: '/dashboard' },
  { title: 'Memory', description: 'Review stored moments, habits, and insights.', href: '/memory' },
  { title: 'Profile', description: 'View your strengths, routines, and settings.', href: '/profile' }
];

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-6">
            <p className="text-sm uppercase tracking-[0.3em] text-violet-300/90">Welcome back</p>
            <h2 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Your AI life assistant for focus, memory, and daily flow.
            </h2>
            <p className="max-w-2xl text-base leading-8 text-slate-300">
              Build momentum with a calm, modern workspace that keeps your habits, summaries, and behavior insights visible.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/chat">
                <Button>Start a chat</Button>
              </Link>
              <Link href="/dashboard">
                <Button variant="ghost">View dashboard</Button>
              </Link>
            </div>
          </div>
          <div className="rounded-[2rem] border border-white/10 bg-slate-900/90 p-6 shadow-soft">
            <div className="space-y-5">
              <div className="rounded-[1.75rem] bg-slate-950/80 p-5">
                <p className="text-sm text-violet-300 uppercase tracking-[0.24em]">Today</p>
                <p className="mt-3 text-2xl font-semibold text-white">Deep work + habit momentum</p>
                <p className="mt-2 text-sm text-slate-400">Leverage AI prompts, memory context, and mood-aware guidance for your next session.</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-3xl bg-slate-900/80 p-4">
                  <p className="text-sm text-slate-300">Streak</p>
                  <p className="mt-2 text-lg font-semibold text-white">12 sessions</p>
                </div>
                <div className="rounded-3xl bg-slate-900/80 p-4">
                  <p className="text-sm text-slate-300">Focus</p>
                  <p className="mt-2 text-lg font-semibold text-white">82%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <Link key={card.href} href={card.href} className="group rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6 transition hover:border-violet-400/30 hover:bg-slate-900/90">
            <div>
              <p className="text-lg font-semibold text-white">{card.title}</p>
              <p className="mt-3 text-sm text-slate-400">{card.description}</p>
            </div>
            <div className="mt-6 text-xs uppercase tracking-[0.3em] text-violet-300/90">Open</div>
          </Link>
        ))}
      </section>

      <SectionHeading title="Your workspace" description="The assistant is ready to support your next session, growth plan, and memory review." />
    </div>
  );
}
