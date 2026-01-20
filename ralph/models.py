from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# Single shared DB instance for the Ralph service
db = SQLAlchemy()


class Event(db.Model):
    """
    Immutable event log.

    Each row represents a single observed outcome from
    FutureHub or Help Scout. Events are append-only.
    """

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    event_type = db.Column(db.String(64), nullable=False)
    source_system = db.Column(db.String(64), nullable=False)

    intent = db.Column(db.String(128), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)

    outcome = db.Column(db.String(64), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class ConfidenceCalibration(db.Model):
    """
    Advisory confidence calibration output.

    These records are derived from Event data and are
    NEVER applied automatically.
    """

    __tablename__ = "confidence_calibrations"

    id = db.Column(db.Integer, primary_key=True)

    intent = db.Column(db.String(128), nullable=False, unique=True)

    recommended_threshold = db.Column(db.Float, nullable=False)
    success_rate = db.Column(db.Float, nullable=False)
    observation_count = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
