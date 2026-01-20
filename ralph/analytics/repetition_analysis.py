from datetime import datetime, timedelta
from sqlalchemy import func

from ralph.models import db, Event


def analyze_intent_frequency(days=7):
    """
    Analytics-only loop:
    Count how often each intent appears within a time window.
    Descriptive only. Read-only.
    """

    since = datetime.utcnow() - timedelta(days=days)

    results = (
        db.session.query(
            Event.intent,
            func.count(Event.id).label("event_count"),
        )
        .filter(
            Event.intent.isnot(None),
            Event.created_at >= since,
        )
        .group_by(Event.intent)
        .order_by(func.count(Event.id).desc())
        .all()
    )

    insights = []
    for intent, count in results:
        insights.append(
            {
                "insight_type": "intent_frequency",
                "intent": intent,
                "event_count": count,
                "time_window_days": days,
                "message": (
                    f"Intent '{intent}' appeared {count} times "
                    f"in the last {days} days."
                ),
                "actionable": False,
                "requires_approval": False,
            }
        )

    return insights
