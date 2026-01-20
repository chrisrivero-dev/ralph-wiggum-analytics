from datetime import datetime, timedelta

from sqlalchemy import func

from ralph.models import Event, ConfidenceCalibration
from ralph.models import db



def generate_weekly_executive_summary(days: int = 7):
    """
    Weekly executive summary.
    Reporting-only. No judgments. No recommendations auto-applied.
    JSON-safe output.
    """

    now = datetime.utcnow()
    start = now - timedelta(days=days)

    summary = {
        "time_window_days": days,
        "generated_at": now.isoformat(),
        "top_intents": [],
        "intent_increases": [],
        "intents_missing_approval": [],
        "calibration_advisories": [],
    }

    # -------------------------------------------------
    # Top intents by volume
    # -------------------------------------------------
    top_intents = (
        db.session.query(
            Event.intent,
            func.count(Event.id).label("event_count"),
        )
        .filter(Event.created_at >= start)
        .group_by(Event.intent)
        .order_by(func.count(Event.id).desc())
        .limit(5)
        .all()
    )

    for row in top_intents:
        summary["top_intents"].append(
            {
                "intent": row.intent,
                "event_count": row.event_count,
            }
        )

    # -------------------------------------------------
    # Intent increases vs previous period
    # -------------------------------------------------
    prev_start = start - timedelta(days=days)

    def counts_between(start_ts, end_ts):
        return {
            r.intent: r.count
            for r in (
                db.session.query(
                    Event.intent,
                    func.count(Event.id).label("count"),
                )
                .filter(Event.created_at >= start_ts)
                .filter(Event.created_at < end_ts)
                .group_by(Event.intent)
                .all()
            )
        }

    current_counts = counts_between(start, now)
    previous_counts = counts_between(prev_start, start)

    all_intents = set(current_counts) | set(previous_counts)

    for intent in sorted(all_intents):
        current = current_counts.get(intent, 0)
        previous = previous_counts.get(intent, 0)

        if current > previous:
            summary["intent_increases"].append(
                {
                    "intent": intent,
                    "previous_count": previous,
                    "current_count": current,
                    "delta": current - previous,
                }
            )

    # -------------------------------------------------
    # Intents missing approval (events exist, no decision log)
    # -------------------------------------------------
    approved_intents = {
        r.intent
        for r in db.session.query(ConfidenceCalibration.intent).all()
    }

    for intent, count in current_counts.items():
        if intent not in approved_intents:
            summary["intents_missing_approval"].append(
                {
                    "intent": intent,
                    "event_count": count,
                }
            )

    # -------------------------------------------------
    # Calibration advisory snapshot (read-only)
    # -------------------------------------------------
    calibrations = ConfidenceCalibration.query.all()
    for cal in calibrations:
        summary["calibration_advisories"].append(
            {
                "intent": cal.intent,
                "recommended_threshold": cal.recommended_threshold,
                "success_rate": cal.success_rate,
                "observation_count": cal.observation_count,
            }
        )

    return summary
