from flask import Blueprint, jsonify, request

from ralph.events.intake import ingest_event

events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("/ingest", methods=["POST"])
def ingest():
    try:
        payload = request.get_json(force=True)
        event = ingest_event(payload)

        return (
            jsonify(
                {
                    "status": "accepted",
                    "event_id": event.id,
                }
            ),
            201,
        )

    except Exception as exc:
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(exc),
                }
            ),
            400,
        )
