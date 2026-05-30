"""
Derives coaching insights by combining event analytics with stored profile facts.
"""

from __future__ import annotations

from typing import List

from Event.event_manager import EventManager
from Profile.memory.profile_manager import ProfileManager
from Profile.models.user_profile import ProfileFact


class BehaviourAnalyzer:
    def __init__(
        self,
        event_manager: EventManager,
        profile_manager: ProfileManager,
    ):
        self.event_manager = event_manager
        self.profile_manager = profile_manager

    def analyze(self, user_id: str, days: int = 30) -> dict:
        analytics = self.event_manager.get_behavioral_analytics(user_id, days=days)
        profile_summary = self.profile_manager.get_profile_summary(user_id)
        facts = self.profile_manager.get_facts(user_id)

        insights: List[str] = []
        alignments: List[str] = []
        gaps: List[str] = []
        recommendations: List[str] = []

        total_events = analytics.get("total_events", 0)
        study_pct = analytics.get("study_consistency_percent", 0) or 0
        bible_streak = analytics.get("bible_streak_days", 0) or 0
        avg_sleep = analytics.get("avg_sleep_duration_hours")
        dominant_mood = analytics.get("dominant_mood")

        if total_events == 0 and not facts:
            insights.append("No behavioral data yet — start by logging an event or sharing a preference.")
            recommendations.append(
                "Tell the assistant something you did today (study, sleep, mood) or a habit you want tracked."
            )
        elif total_events == 0 and facts:
            gaps.append(
                "You have profile preferences saved but no logged events in this period."
            )
            recommendations.append(
                "Log daily activities so the assistant can compare what you say vs what you do."
            )

        if study_pct >= 60:
            insights.append(
                f"Strong study consistency: active on {study_pct}% of days in the last {days} days."
            )
        elif study_pct > 0:
            gaps.append(
                f"Study consistency is {study_pct}% — room to build a steadier routine."
            )
            recommendations.append(
                "Pick two fixed study blocks per week and log them after each session."
            )

        if bible_streak >= 3:
            insights.append(f"Bible reading streak: {bible_streak} consecutive day(s).")
        elif any(f.topic == "spirituality" for f in facts) and bible_streak == 0:
            gaps.append("Spirituality is in your profile, but no recent bible-reading events were logged.")

        if avg_sleep is not None:
            if avg_sleep < 7:
                gaps.append(
                    f"Average sleep is {avg_sleep}h — below the 7h recovery target."
                )
                recommendations.append(
                    "Set a consistent wind-down time and log sleep/wake for one week."
                )
            elif avg_sleep >= 7.5:
                alignments.append(f"Sleep averaging {avg_sleep}h supports recovery and focus.")

        if dominant_mood:
            insights.append(f"Most frequent mood in this period: {dominant_mood}.")

        self._compare_profile_to_behavior(facts, analytics, alignments, gaps, recommendations)

        summary_md = self._format_summary(
            days=days,
            insights=insights,
            alignments=alignments,
            gaps=gaps,
            recommendations=recommendations,
            analytics=analytics,
            profile_total=profile_summary.get("total_facts", 0),
        )

        return {
            "period_days": days,
            "total_events": total_events,
            "profile_facts": len(facts),
            "insights": insights,
            "alignments": alignments,
            "gaps": gaps,
            "recommendations": recommendations,
            "analytics": {
                "study_consistency_percent": study_pct,
                "bible_streak_days": bible_streak,
                "avg_sleep_duration_hours": avg_sleep,
                "dominant_mood": dominant_mood,
                "total_study_hours": analytics.get("total_study_hours"),
            },
            "summary_markdown": summary_md,
        }

    def _compare_profile_to_behavior(
        self,
        facts: List[ProfileFact],
        analytics: dict,
        alignments: List[str],
        gaps: List[str],
        recommendations: List[str],
    ) -> None:
        study_keywords = ("study", "studying", "learn", "focus", "productive")
        night_keywords = ("night", "late", "evening")

        study_prefs = [
            f
            for f in facts
            if f.topic == "productivity"
            or any(k in f.statement.lower() for k in study_keywords)
        ]
        night_prefs = [
            f for f in facts if any(k in f.statement.lower() for k in night_keywords)
        ]

        study_pct = analytics.get("study_consistency_percent", 0) or 0

        if study_prefs and study_pct >= 40:
            alignments.append(
                "Logged study activity supports your stated study-related preferences."
            )
        elif study_prefs and study_pct < 20 and analytics.get("total_events", 0) > 0:
            gaps.append(
                "You describe study preferences in your profile, but few study sessions were logged recently."
            )
            recommendations.append(
                "Schedule one small study block that matches your preferred time and log it right after."
            )

        if night_prefs and study_pct >= 30:
            alignments.append(
                "Your activity pattern is compatible with a preference for evening or late study."
            )

        for fact in facts:
            if fact.trait_type == "weakness":
                recommendations.append(f"Growth focus: {fact.statement}")
            elif fact.trait_type == "goal":
                recommendations.append(f"Goal to track: {fact.statement}")

    def _format_summary(
        self,
        *,
        days: int,
        insights: List[str],
        alignments: List[str],
        gaps: List[str],
        recommendations: List[str],
        analytics: dict,
        profile_total: int,
    ) -> str:
        md = f"### Behaviour & Coaching Insights (Past {days} Days)\n"
        md += f"* **Events logged**: {analytics.get('total_events', 0)}\n"
        md += f"* **Profile facts**: {profile_total}\n\n"

        if insights:
            md += "#### Observations\n"
            for item in insights:
                md += f"* {item}\n"
            md += "\n"

        if alignments:
            md += "#### Alignments (profile ↔ behavior)\n"
            for item in alignments:
                md += f"* {item}\n"
            md += "\n"

        if gaps:
            md += "#### Gaps & opportunities\n"
            for item in gaps:
                md += f"* {item}\n"
            md += "\n"

        if recommendations:
            md += "#### Recommended next steps\n"
            for item in recommendations[:6]:
                md += f"* {item}\n"

        if not insights and not alignments and not gaps and not recommendations:
            md += "_Keep logging events and sharing preferences to unlock personalized coaching._\n"

        return md.strip()
