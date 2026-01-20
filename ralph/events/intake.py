from ralph.models import db, Event


def ingest_event(payload: dict) -> Event:
    """
    Validate and persist an incoming event.

    Events are append-only and immutable.
    """

    required_fields = [
        "event_type",
        "source_system",
        "intent",
        "outcome",
    ]

    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    event = Event(
        event_type=payload["event_type"],
        source_system=payload["source_system"],
        intent=payload["intent"],
        confidence_score=payload.get("confidence_score"),
        outcome=payload["outcome"],
    )

    db.session.add(event)
    db.session.commit()

    return event
