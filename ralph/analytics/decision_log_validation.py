import json
from pathlib import Path
from sqlalchemy import distinct
from pathlib import Path


from ralph.models import db, Event


REPO_ROOT = Path(__file__).resolve().parents[2]
DECISION_LOG_PATH = REPO_ROOT / "data" / "decision_log.json"



def detect_missing_decisions():
    """
    Governance loop:
    Detect intents that appear in events but have no recorded decision approval.

    Advisory only. Read-only.
    """

    # Load decision log
    if not DECISION_LOG_PATH.exists():
        approved_intents = set()
    else:
        with open(DECISION_LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            approved_intents = {
                item["intent"] for item in data.get("approved_intents", [])
            }

    # Intents seen in events
    event_intents = {
        row[0]
        for row in db.session.query(distinct(Event.intent))
        .filter(Event.intent.isnot(None))
        .all()
    }

    missing = sorted(event_intents - approved_intents)

    insights = []
    for intent in missing:
        insights.append(
            {
                "insight_type": "decision_log_missing",
                "intent": intent,
                "message": (
                    f"Intent '{intent}' has events but no recorded approval "
                    "in the decision log."
                ),
                "actionable": False,
                "requires_approval": True,
            }
        )

    return insights
