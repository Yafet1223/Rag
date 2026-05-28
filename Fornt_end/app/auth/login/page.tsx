"use client";

import Link from 'next/link';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <section className="rounded-[2rem] border border-white/10 bg-slate-950/80 p-10 shadow-soft backdrop-blur-xl">
        <p className="text-sm uppercase tracking-[0.3em] text-violet-300/90">Sign in</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">Access your AI assistant.</h1>
        <p className="mt-3 text-slate-400">Secure login to keep your habits, history, and memory context personal.</p>

        <div className="mt-8 space-y-5">
          <Input label="Email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} />
          <Input label="Password" type="password" placeholder="••••••••" value={password} onChange={(event) => setPassword(event.target.value)} />
          <Button className="w-full">Continue</Button>
        </div>

        <p className="mt-6 text-center text-sm text-slate-400">
          New here?{' '}
          <Link href="/auth/signup" className="font-semibold text-violet-300 hover:text-violet-200">
            Create an account
          </Link>
        </p>
      </section>
    </div>
  );
}
