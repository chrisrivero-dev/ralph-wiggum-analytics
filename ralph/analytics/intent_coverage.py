from ralph.models import db, Event, ConfidenceCalibration
from sqlalchemy import distinct


def detect_uncovered_intents():
    """
    Governance loop:
    Detect intents that appear in events but have no confidence calibration.
    Advisory only. Read-only.
    """

    # All intents seen in events
    event_intents = {
        row[0]
        for row in db.session.query(distinct(Event.intent))
        .filter(Event.intent.isnot(None))
        .all()
    }

    # All intents with confidence calibration
    calibrated_intents = {
        row[0]
        for row in db.session.query(distinct(ConfidenceCalibration.intent))
        .all()
    }

    uncovered = sorted(event_intents - calibrated_intents)

    insights = []
    for intent in uncovered:
        insights.append(
            {
                "insight_type": "intent_coverage_gap",
                "intent": intent,
                "message": (
                    f"Intent '{intent}' has observed events but no "
                    "confidence calibration governance."
                ),
                "actionable": False,
                "requires_approval": True,
            }
        )

    return insights
