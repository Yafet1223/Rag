import { ProfileSummary } from '@/components/profile/ProfileSummary';
import { ProfileCard } from '@/components/profile/ProfileCard';
import { SectionHeading } from '@/components/ui/SectionHeading';

const traits = [
  { title: 'Resilience', value: 'High', tone: 'strength' },
  { title: 'Focus balance', value: 'Moderate', tone: 'growth' },
  { title: 'Routine strength', value: 'Growing', tone: 'focus' }
] as const;

export default function ProfilePage() {
  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
        <SectionHeading title="Profile" description="Your preferences, habits, and productivity strengths." />
        <p className="mt-5 text-sm leading-7 text-slate-300">
          Use this page to track what works best for you and where the AI can offer personalized suggestions.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.9fr_0.7fr]">
        <ProfileSummary traits={traits} />
        <ProfileCard />
      </div>
    </div>
  );
}
