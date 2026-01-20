from datetime import datetime, timedelta

from sqlalchemy import func, case

from ralph.models import db, Event


def analyze_draft_outcome_trends(days=7):
    """
    Analytics insight:
    Draft outcome quality trends (follow-ups & resolutions).
    Trend-only. Advisory. Non-actionable.
    """

    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    previous_start = current_start - timedelta(days=days)

    def aggregate(start, end):
        return (
            db.session.query(
                Event.intent.label("intent"),
                func.avg(Event.follow_up_count).label("avg_followups"),
                func.sum(
                    case(
                        (Event.outcome == "resolved", 1),
                        else_=0,
                    )
                ).label("resolved_count"),
                func.sum(
                    case(
                        (Event.outcome == "escalated", 1),
                        else_=0,
                    )
                ).label("escalated_count"),
                func.count(Event.id).label("event_count"),
            )
            .filter(Event.created_at >= start, Event.created_at < end)
            .group_by(Event.intent)
            .all()
        )

    current = {row.intent: row for row in aggregate(current_start, now)}
    previous = {row.intent: row for row in aggregate(previous_start, current_start)}

    insights = []

    for intent in sorted(set(current) | set(previous)):
        cur = current.get(intent)
        prev = previous.get(intent)

        cur_count = cur.event_count if cur else 0
        prev_count = prev.event_count if prev else 0

        insights.append(
            {
                "insight_type": "draft_outcome_trend",
                "intent": intent,
                "current_event_count": cur_count,
                "previous_event_count": prev_count,
                "delta": cur_count - prev_count,
                "avg_followups": round(cur.avg_followups, 2) if cur and cur.avg_followups is not None else 0,
                "resolved_count": cur.resolved_count if cur else 0,
                "escalated_count": cur.escalated_count if cur else 0,
                "actionable": False,
                "requires_approval": False,
                "time_window_days": days,
            }
        )

    return insights
