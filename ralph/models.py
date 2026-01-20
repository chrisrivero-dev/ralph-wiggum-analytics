from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Event(db.Model):
    """
    Immutable event log.
    """

    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    event_type = db.Column(db.String(64), nullable=False)
    source_system = db.Column(db.String(64), nullable=False)

    intent = db.Column(db.String(128), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)

    outcome = db.Column(db.String(64), nullable=False)

    follow_up_count = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class ConfidenceCalibration(db.Model):
    """
    Advisory confidence calibration output.
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
