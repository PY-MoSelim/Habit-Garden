
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask ────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

    # ── MySQL via SQLAlchemy ─────────────────────────────────
    DB_USER     = os.getenv("DB_USER",     "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST     = os.getenv("DB_HOST",     "localhost")
    DB_PORT     = os.getenv("DB_PORT",     "3306")
    DB_NAME     = os.getenv("DB_NAME",     "habit_garden")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # How many missed days before a plant wilts
    WILT_THRESHOLD_DAYS = 1

    # Streak milestones that grow the plant to the next stage
    GROWTH_MILESTONES = [3, 7, 14, 21, 30]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Active config — change to ProductionConfig when deploying
config = DevelopmentConfig