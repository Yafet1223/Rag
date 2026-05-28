import { SectionHeading } from '@/components/ui/SectionHeading';
import { StatCard } from '@/components/Dashboard/StatCard';
import { RecommendationCard } from '@/components/Dashboard/RecommendationCard';
import { fetchDashboardStats } from '@/services/api';

const recommendations = [
  {
    title: 'Build a review ritual',
    summary: 'Check your top focus habits each morning to begin with clarity.',
    note: 'Habit planning'
  },
  {
    title: 'Limit distractions',
    summary: 'Create a micro goal for your next 60-minute session.',
    note: 'Deep work'
  },
  {
    title: 'Capture an insight',
    summary: 'Log today’s mood, energy, and productivity drivers.',
    note: 'Reflection'
  }
];

export default async function DashboardPage() {
  const stats = await fetchDashboardStats();

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
          <SectionHeading title="Dashboard" description="Visualize performance, behavior, and your productivity rhythm." />
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <StatCard label="Uptime" value={stats.uptime} detail="Active focus days" />
            <StatCard label="Streak" value={stats.streak} detail="Consecutive goal sessions" />
            <StatCard label="Focus" value={stats.focus} detail="Average attention score" />
            <StatCard label="Tasks" value={stats.tasks} detail="Completed productivity actions" />
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
          <SectionHeading title="Trend signals" description="AI-driven summary of your current productivity patterns." />
          <div className="mt-6 space-y-4">
            <div className="rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">Focus windows are strongest between 9–11AM.</p>
            </div>
            <div className="rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">You maintain momentum best with 45–55 minute cycles.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {recommendations.map((item) => (
          <RecommendationCard key={item.title} title={item.title} summary={item.summary} note={item.note} />
        ))}
      </section>
    </div>
  );
}
