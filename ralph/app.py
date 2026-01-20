from flask import Flask, jsonify

from ralph.config import Config
from ralph.models import db
from ralph.events.routes import events_bp
from ralph.api.insights import insights_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(events_bp)
    app.register_blueprint(insights_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(
            {
                "service": Config.SERVICE_NAME,
                "status": "ok",
            }
        )

    # Create tables on first run (dev-safe)
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
