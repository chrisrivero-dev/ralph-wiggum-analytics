import os


class Config:
    """
    Central configuration for the Ralph analytics service.

    Ralph is advisory-only:
    - Reads events
    - Writes analytics + insights
    - Never writes back to source systems
    """

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Store the SQLite DB inside ralph/instance/
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(INSTANCE_DIR, "ralph.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Safety + identity
    SERVICE_NAME = "ralph"
    MODE = os.getenv("RALPH_MODE", "development")

    # Analytics behavior (safe defaults)
    CONFIDENCE_BASELINE = 0.85
    MIN_SAMPLE_SIZE = 5
