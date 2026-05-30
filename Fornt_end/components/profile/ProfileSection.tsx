'use client';

import { useEffect, useState } from 'react';
import { ProfileSummary } from '@/components/profile/ProfileSummary';
import { ProfileCard } from '@/components/profile/ProfileCard';
import { fetchProfileMemory, profileFactsToTraits } from '@/services/api';
import type { ProfileTrait } from '@/types';

const fallbackTraits: ProfileTrait[] = [
  { title: 'Getting started', value: 'Share a preference in chat', tone: 'focus' }
];

export const ProfileSection = () => {
  const [traits, setTraits] = useState<ProfileTrait[]>(fallbackTraits);
  const [factCount, setFactCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProfileMemory()
      .then((data) => {
        setFactCount(data.summary.total_facts ?? data.facts.length);
        if (data.facts.length > 0) {
          setTraits(profileFactsToTraits(data.facts));
        }
      })
      .catch((err: Error) => {
        setError(err.message);
      });
  }, []);

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_0.7fr]">
      <ProfileSummary traits={traits} />
      <div className="space-y-4">
        <ProfileCard title="Stored facts" value={String(factCount)} tone="focus" />
        {error ? (
          <p className="text-sm text-amber-300/90">
            Could not load profile from API. Run <code className="text-violet-200">python api/main.py</code>.
          </p>
        ) : null}
      </div>
    </div>
  );
};
