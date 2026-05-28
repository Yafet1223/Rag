"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { SectionHeading } from '@/components/ui/SectionHeading';
import { Input } from '@/components/ui/Input';

export default function SettingsPage() {
  const [theme, setTheme] = useState('dark');
  const [voice, setVoice] = useState('Calm');
  const [notifications, setNotifications] = useState(true);

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
        <SectionHeading title="Settings" description="Fine-tune how your assistant supports productivity and focus." />
      </section>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
          <div className="space-y-6">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-violet-300/90">Theme</p>
              <div className="mt-4 flex flex-wrap gap-3">
                {['dark', 'soft', 'minimal'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setTheme(option)}
                    className={`rounded-2xl border px-4 py-2 text-sm transition ${theme === option ? 'border-violet-400 bg-violet-500/10 text-violet-200' : 'border-white/10 bg-slate-900/80 text-slate-300 hover:border-violet-400/30'}`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-violet-300/90">AI personality</p>
              <div className="mt-4 flex flex-wrap gap-3">
                {['Calm', 'Direct', 'Coach'].map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setVoice(option)}
                    className={`rounded-2xl border px-4 py-2 text-sm transition ${voice === option ? 'border-violet-400 bg-violet-500/10 text-violet-200' : 'border-white/10 bg-slate-900/80 text-slate-300 hover:border-violet-400/30'}`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-violet-300/90">Notifications</p>
                  <p className="text-sm text-slate-400">Receive reminders and focus pulse updates.</p>
                </div>
                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={notifications}
                    onChange={() => setNotifications((current) => !current)}
                    className="peer sr-only"
                  />
                  <div className="w-11 rounded-full bg-slate-600 p-1 transition peer-checked:bg-violet-500"></div>
                  <div className={`absolute left-1 top-1 h-4 w-4 rounded-full bg-white transition peer-checked:translate-x-5`}></div>
                </label>
              </div>
            </div>

            <div className="space-y-4 rounded-[1.75rem] border border-white/10 bg-slate-900/80 p-6">
              <Input label="Personal reminder email" placeholder="you@example.com" value="" onChange={() => undefined} />
              <Input label="Daily summary time" placeholder="08:00 AM" value="" onChange={() => undefined} />
            </div>

            <div className="mt-2">
              <Button>Save changes</Button>
            </div>
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-8 shadow-soft backdrop-blur-xl">
          <p className="text-sm uppercase tracking-[0.24em] text-violet-300/90">System status</p>
          <div className="mt-6 space-y-4">
            <div className="rounded-3xl bg-slate-900/80 p-4">
              <p className="text-sm text-slate-300">Theme mode:</p>
              <p className="mt-2 text-lg font-semibold text-white">{theme}</p>
            </div>
            <div className="rounded-3xl bg-slate-900/80 p-4">
              <p className="text-sm text-slate-300">Assistant tone:</p>
              <p className="mt-2 text-lg font-semibold text-white">{voice}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
