from collections import defaultdict

from ralph.config import Config
from ralph.models import db, Event, ConfidenceCalibration


def run_confidence_calibration():
    """
    Analyze historical events and produce advisory confidence calibrations.

    This function:
    - Reads immutable Event data
    - Computes success rates per intent
    - Writes advisory ConfidenceCalibration records
    - NEVER applies changes automatically
    """

    # Pull all events with a confidence score
    events = (
        Event.query
        .filter(Event.confidence_score.isnot(None))
        .all()
    )

    if not events:
        return []

    # Group events by intent
    by_intent = defaultdict(list)
    for e in events:
        by_intent[e.intent].append(e)

    results = []

    for intent, intent_events in by_intent.items():
        observation_count = len(intent_events)

        # Enforce minimum sample size
        if observation_count < Config.MIN_SAMPLE_SIZE:
            continue

        successes = [
            e for e in intent_events
            if e.outcome == "resolved"
        ]

        success_rate = len(successes) / observation_count

        # Start from baseline
        recommended_threshold = Config.CONFIDENCE_BASELINE

        # Simple, conservative adjustment rules
        if success_rate >= 0.95:
            recommended_threshold = max(
                0.75,
                Config.CONFIDENCE_BASELINE - 0.02
            )
        elif success_rate < 0.80:
            recommended_threshold = min(
                0.95,
                Config.CONFIDENCE_BASELINE + 0.05
            )

        # Upsert calibration (advisory only)
        calibration = ConfidenceCalibration.query.filter_by(
            intent=intent
        ).first()

        if calibration:
            calibration.recommended_threshold = recommended_threshold
            calibration.success_rate = success_rate
            calibration.observation_count = observation_count
        else:
            calibration = ConfidenceCalibration(
                intent=intent,
                recommended_threshold=recommended_threshold,
                success_rate=success_rate,
                observation_count=observation_count,
            )
            db.session.add(calibration)

        results.append(
            {
                "intent": intent,
                "recommended_threshold": recommended_threshold,
                "success_rate": success_rate,
                "observation_count": observation_count,
            }
        )

    db.session.commit()
    return results
