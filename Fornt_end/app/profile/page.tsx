import { ProfileSection } from '@/components/profile/ProfileSection';
import { SectionHeading } from '@/components/ui/SectionHeading';

export default function ProfilePage() {
  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
        <SectionHeading title="Profile" description="Your preferences, habits, and productivity strengths." />
        <p className="mt-5 text-sm leading-7 text-slate-300">
          Facts are loaded from your assistant memory. Tell the chat something like &quot;I prefer studying at night&quot; to add more.
        </p>
      </section>

      <ProfileSection />
    </div>
  );
}
