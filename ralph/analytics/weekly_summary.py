from datetime import datetime, timedelta
from sqlalchemy import func

from ralph.models import db, Event


def analyze_draft_outcome_trends(time_window_days: int = 7):
    """
    Analytics loop (trend-only, advisory):

    Compares draft outcomes across two adjacent time windows:
    - Current period: last N days
    - Previous period: N days before that

    Signals:
    - Average follow-up count
    - Resolution vs escalation counts

    Emits descriptive insights only.
    No judgments. No recommendations. No automation.
    """

    now = datetime.utcnow()
    current_start = now - timedelta(days=time_window_days)
    previous_start = current_start - timedelta(days=time_window_days)

    insights = []

    # Aggregate outcomes per intent for both windows
    def aggregate(start, end):
        return (
            db.session.query(
                Event.intent.label("intent"),
                func.avg(Event.follow_up_count).label("avg_followups"),
                func.sum(
                    func.case((Event.outcome == "resolved", 1), else_=0)
                ).label("resolved_count"),
                func.sum(
                    func.case((Event.outcome == "escalated", 1), else_=0)
                ).label("escalated_count"),
                func.count(Event.id).label("event_count"),
            )
            .filter(
                Event.created_at >= start,
                Event.created_at < end,
                Event.intent.isnot(None),
            )
            .group_by(Event.intent)
            .all()
        )

    current = {row.intent: row for row in aggregate(current_start, now)}
    previous = {row.intent: row for row in aggregate(previous_start, current_start)}

    all_intents = set(current.keys()) | set(previous.keys())

    for intent in sorted(all_intents):
        curr = current.get(intent)
        prev = previous.get(intent)

        curr_avg = float(curr.avg_followups) if curr and curr.avg_followups is not None else 0.0
        prev_avg = float(prev.avg_followups) if prev and prev.avg_followups is not None else 0.0
        delta = round(curr_avg - prev_avg, 2)

        insights.append(
            {
                "insight_type": "draft_outcome_trend",
                "intent": intent,
                "current_followups_avg": curr_avg,
                "previous_followups_avg": prev_avg,
                "delta": delta,
                "message": (
                    f"Follow-up activity changed for intent '{intent}' "
                    f"from {prev_avg} to {curr_avg} over the last {time_window_days} days."
                ),
                "actionable": False,
                "requires_approval": False,
            }
        )

    return insights
