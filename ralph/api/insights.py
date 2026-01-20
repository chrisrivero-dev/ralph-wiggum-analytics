from flask import Blueprint, jsonify

from ralph.models import ConfidenceCalibration
from ralph.analytics.intent_coverage import detect_uncovered_intents
from ralph.analytics.guardrail_validation import detect_missing_guardrails
from ralph.analytics.decision_log_validation import detect_missing_decisions
from ralph.analytics.trend_deltas import compute_intent_trend_deltas
from ralph.analytics.repetition_analysis import analyze_intent_frequency
from ralph.analytics.draft_outcome_trends import analyze_draft_outcome_trends


insights_bp = Blueprint("insights", __name__, url_prefix="/insights")


@insights_bp.route("/intent-coverage", methods=["GET"])
def intent_coverage():
    """
    Governance insight:
    Detect intents that have events but no confidence calibration.
    Advisory only.
    """
    insights = detect_uncovered_intents()
    return jsonify(insights), 200

@insights_bp.route("/draft-outcomes", methods=["GET"])
def draft_outcome_trends():
    """
    Analytics insight:
    Draft outcome quality trends (follow-ups & resolutions).
    Trend-only. Advisory. Non-actionable.
    """
    insights = analyze_draft_outcome_trends()
    return jsonify(insights), 200


from ralph.analytics.repetition_analysis import analyze_intent_frequency

@insights_bp.route("/trends", methods=["GET"])
def intent_trend_deltas():
    """
    Analytics insight:
    Show intent frequency deltas between time windows.
    Descriptive only.
    """
    insights = compute_intent_trend_deltas(days=7)
    return jsonify(insights), 200


@insights_bp.route("/repetition", methods=["GET"])
def repetition_analysis():
    """
    Analytics insight:
    Shows which intents appear most frequently.
    Descriptive only.
    """
    insights = analyze_intent_frequency(days=7)
    return jsonify(insights), 200

@insights_bp.route("/guardrails", methods=["GET"])
def guardrail_validation():
    """
    Governance insight:
    Detect missing guardrails for active intents.
    Advisory only.
    """
    insights = detect_missing_guardrails()
    return jsonify(insights), 200


@insights_bp.route("/decision-log", methods=["GET"])
def decision_log_validation():
    """
    Governance insight:
    Detect intents missing explicit human approval decisions.
    Advisory only.
    """
    insights = detect_missing_decisions()
    return jsonify(insights), 200


@insights_bp.route("/calibrations", methods=["GET"])
def get_calibrations():
    """
    Read-only endpoint returning advisory confidence calibrations.
    """
    calibrations = ConfidenceCalibration.query.all()

    return jsonify(
        [
            {
                "intent": c.intent,
                "recommended_threshold": c.recommended_threshold,
                "success_rate": c.success_rate,
                "observation_count": c.observation_count,
                "actionable": False,
                "requires_approval": True,
            }
            for c in calibrations
        ]
    ), 200
