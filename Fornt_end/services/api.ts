import type { Message, ProfileTrait } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';
const DEFAULT_USER = 'default_user';

export interface RouteInfo {
  type: string;
  source: string;
  reason: string;
  confidence: number;
}

export interface AssistantResponse {
  route: RouteInfo;
  action: 'chat_reply' | 'event_saved' | 'profile_saved' | 'ignored';
  message: string;
  data: Record<string, unknown>;
}

export interface InsightsResponse {
  period_days: number;
  total_events: number;
  profile_facts: number;
  insights: string[];
  alignments: string[];
  gaps: string[];
  recommendations: string[];
  summary_markdown: string;
  analytics: {
    study_consistency_percent?: number;
    bible_streak_days?: number;
    avg_sleep_duration_hours?: number | null;
    dominant_mood?: string | null;
    total_study_hours?: number;
  };
}

export interface ProfileMemoryResponse {
  facts: Array<{
    id?: number;
    statement: string;
    topic: string;
    trait_type: string;
    polarity?: string | null;
  }>;
  summary: {
    total_facts: number;
    strengths?: string[];
    weaknesses?: string[];
    goals?: string[];
  };
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    try {
      const body = JSON.parse(text) as { detail?: string | { msg?: string }[] };
      if (typeof body.detail === 'string') {
        throw new Error(body.detail);
      }
    } catch (e) {
      if (e instanceof Error && e.message !== text) {
        throw e;
      }
    }
    if (response.status === 429) {
      throw new Error(
        'Gemini quota exceeded (free tier). Wait about a minute, then try again. Check: https://ai.dev/rate-limit'
      );
    }
    throw new Error(text || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const sendMessage = async (message: string, userId = DEFAULT_USER): Promise<AssistantResponse> => {
  const response = await fetch(`${API_BASE}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message })
  });
  return parseJson<AssistantResponse>(response);
};

export const queryMemory = async (question: string, userId = DEFAULT_USER): Promise<string> => {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, question })
  });
  const data = await parseJson<{ answer: string }>(response);
  return data.answer;
};

export const fetchInsights = async (userId = DEFAULT_USER): Promise<InsightsResponse> => {
  const response = await fetch(`${API_BASE}/insights?user_id=${encodeURIComponent(userId)}`, {
    cache: 'no-store'
  });
  return parseJson<InsightsResponse>(response);
};

export const fetchProfileMemory = async (userId = DEFAULT_USER): Promise<ProfileMemoryResponse> => {
  const response = await fetch(`${API_BASE}/memory/profile?user_id=${encodeURIComponent(userId)}`, {
    cache: 'no-store'
  });
  return parseJson<ProfileMemoryResponse>(response);
};

export const formatAssistantMessage = (payload: AssistantResponse): string => {
  // Backend sets full coaching / chat text on `message` for all actions
  if (payload.message?.trim()) {
    return payload.message;
  }
  if (payload.action === 'event_saved') {
    const event = payload.data.event as { event_type?: string; study_hours?: number; mood?: string } | undefined;
    const parts = [`Saved to your activity log: ${event?.event_type ?? 'event'}.`];
    if (event?.study_hours != null) parts.push(`Study: ${event.study_hours}h.`);
    if (event?.mood) parts.push(`Mood: ${event.mood}.`);
    return parts.join(' ');
  }
  if (payload.action === 'profile_saved') {
    const profile = payload.data.profile as { statement?: string } | undefined;
    return `Saved to your profile: ${profile?.statement ?? 'Done.'}`;
  }
  if (payload.action === 'ignored') {
    return 'Got it — I skipped saving that (low memory value).';
  }
  return 'Done.';
};

export const fetchChatResponse = async (message: string): Promise<Message> => {
  const payload = await sendMessage(message);
  return {
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content: formatAssistantMessage(payload),
    createdAt: new Date().toISOString()
  };
};

export const fetchDashboardStats = async () => {
  try {
    const insights = await fetchInsights();
    const a = insights.analytics;
    return {
      uptime: `${insights.total_events} events`,
      streak: a.bible_streak_days ? `${a.bible_streak_days} day bible streak` : 'No streak yet',
      focus: a.study_consistency_percent != null ? `${a.study_consistency_percent}% study days` : '—',
      tasks: `${insights.profile_facts} profile facts`,
      insights,
      trendLines: [
        ...insights.insights.slice(0, 2),
        ...insights.recommendations.slice(0, 1)
      ].filter(Boolean)
    };
  } catch {
    return {
      uptime: '—',
      streak: '—',
      focus: '—',
      tasks: '—',
      insights: null,
      trendLines: ['Start the API: python api/main.py', 'Then log events and preferences in chat.']
    };
  }
};

export const profileFactsToTraits = (facts: ProfileMemoryResponse['facts']): ProfileTrait[] => {
  return facts.slice(0, 6).map((fact) => ({
    title: fact.topic,
    value: fact.statement.length > 48 ? `${fact.statement.slice(0, 45)}…` : fact.statement,
    tone:
      fact.trait_type === 'strength'
        ? 'strength'
        : fact.trait_type === 'weakness'
          ? 'growth'
          : 'focus'
  }));
};
