from datetime import datetime, timedelta
from sqlalchemy import func

from ralph.models import db, Event


def compute_intent_trend_deltas(days=7):
    """
    Analytics-only loop:
    Compare intent frequency between two adjacent time windows.

    Example:
    - Last 7 days vs previous 7 days

    Emits descriptive, non-actionable insights only.
    """

    now = datetime.utcnow()
    current_start = now - timedelta(days=days)
    previous_start = now - timedelta(days=days * 2)

    # Current window counts
    current_counts = dict(
        db.session.query(
            Event.intent,
            func.count(Event.id)
        )
        .filter(Event.created_at >= current_start)
        .group_by(Event.intent)
        .all()
    )

    # Previous window counts
    previous_counts = dict(
        db.session.query(
            Event.intent,
            func.count(Event.id)
        )
        .filter(
            Event.created_at >= previous_start,
            Event.created_at < current_start
        )
        .group_by(Event.intent)
        .all()
    )

    insights = []

    for intent, current_count in current_counts.items():
        previous_count = previous_counts.get(intent, 0)
        delta = current_count - previous_count

        insights.append(
            {
                "insight_type": "intent_trend_delta",
                "intent": intent,
                "current_period_count": current_count,
                "previous_period_count": previous_count,
                "delta": delta,
                "time_window_days": days,
                "message": (
                    f"Intent '{intent}' count changed from "
                    f"{previous_count} to {current_count} "
                    f"over the last {days} days."
                ),
                "actionable": False,
                "requires_approval": False,
            }
        )

    return insights
