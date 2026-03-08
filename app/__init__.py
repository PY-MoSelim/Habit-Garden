
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# ── Extensions (initialised without app yet) ─────────────────
db           = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ── Bind extensions ──────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view      = "main.login"
    login_manager.login_message   = "Please log in to access your garden."
    login_manager.login_message_category = "info"

    # ── Register blueprints ──────────────────────────────────
    from app.routes import main
    app.register_blueprint(main)

    # ── Template helpers ─────────────────────────────────────
    @app.template_global()
    def plant_emoji(css_class: str, stage: int, wilted: bool) -> str:
        """Return the right emoji for a plant based on type, stage, and health."""
        if wilted:
            return "🥀"
        stage_maps = {
            "plant-sunflower": ["🌰", "🌱", "🌿", "🌼", "🌻"],
            "plant-cactus":    ["🌰", "🌱", "🪴", "🌵", "🌵"],
            "plant-rose":      ["🌰", "🌱", "🌿", "🥀", "🌹"],
            "plant-bamboo":    ["🌰", "🌱", "🌿", "🎋", "🎋"],
            "plant-cherry":    ["🌰", "🌱", "🌿", "🌸", "🌸"],
            "plant-fern":      ["🌰", "🌱", "🌿", "🍃", "🌿"],
        }
        emojis = stage_maps.get(css_class, ["🌰", "🌱", "🌿", "🌺", "🌸"])
        idx    = max(0, min(stage - 1, len(emojis) - 1))
        return emojis[idx]

    # ── Create tables if they don't exist ────────────────────
    with app.app_context():
        db.create_all()

    return app
