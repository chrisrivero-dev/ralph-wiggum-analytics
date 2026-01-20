from ralph.models import db, Event, ConfidenceCalibration
from sqlalchemy import distinct


def detect_missing_guardrails():
    """
    Governance loop:
    Detect intents that appear in events but are missing required guardrails.

    Guardrails checked (v1):
    - Confidence calibration exists

    Advisory only. Read-only.
    """

    # Intents seen in events
    event_intents = {
        row[0]
        for row in db.session.query(distinct(Event.intent))
        .filter(Event.intent.isnot(None))
        .all()
    }

    # Intents with confidence calibration
    calibrated_intents = {
        row[0]
        for row in db.session.query(distinct(ConfidenceCalibration.intent)).all()
    }

    missing = sorted(event_intents - calibrated_intents)

    insights = []
    for intent in missing:
        insights.append(
            {
                "insight_type": "missing_guardrail",
                "intent": intent,
                "missing": ["confidence_calibration"],
                "message": (
                    f"Intent '{intent}' has events but no confidence calibration defined."
                ),
                "actionable": False,
                "requires_approval": True,
            }
        )

    return insights
