
from datetime import date, datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# ── User loader for Flask-Login ──────────────────────────────
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# MODEL: User

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer,     primary_key=True)
    username   = db.Column(db.String(50),  nullable=False, unique=True)
    email      = db.Column(db.String(120), nullable=False, unique=True)
    password   = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,    default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    habits            = db.relationship("Habit",           backref="owner",
                                        lazy="dynamic", cascade="all, delete-orphan")
    habit_logs        = db.relationship("HabitLog",        backref="user",
                                        lazy="dynamic", cascade="all, delete-orphan")
    user_achievements = db.relationship("UserAchievement", backref="user",
                                        lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, raw_password: str):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<User {self.username}>"


# MODEL: Plant
class Plant(db.Model):
    __tablename__ = "plants"

    id          = db.Column(db.Integer,     primary_key=True)
    name        = db.Column(db.String(50),  nullable=False, unique=True)
    description = db.Column(db.String(255))
    max_stage   = db.Column(db.Integer,     nullable=False, default=5)
    css_class   = db.Column(db.String(50),  nullable=False)

    habits = db.relationship("Habit", backref="plant", lazy="dynamic")

    def __repr__(self):
        return f"<Plant {self.name}>"


# MODEL: Habit
class Habit(db.Model):
    __tablename__ = "habits"

    id            = db.Column(db.Integer,   primary_key=True)
    user_id       = db.Column(db.Integer,   db.ForeignKey("users.id"),  nullable=False)
    plant_id      = db.Column(db.Integer,   db.ForeignKey("plants.id"), nullable=False)
    name          = db.Column(db.String(100), nullable=False)
    description   = db.Column(db.String(255))
    frequency     = db.Column(db.Enum("daily", "weekly"), nullable=False, default="daily")
    current_stage = db.Column(db.Integer,   nullable=False, default=1)
    streak        = db.Column(db.Integer,   nullable=False, default=0)
    is_wilted     = db.Column(db.Boolean,   nullable=False, default=False)
    created_at    = db.Column(db.DateTime,  default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime,  default=datetime.utcnow,
                              onupdate=datetime.utcnow)

    logs = db.relationship("HabitLog", backref="habit", lazy="dynamic",
                           cascade="all, delete-orphan")

    @property
    def done_today(self) -> bool:
        return HabitLog.query.filter_by(
            habit_id=self.id,
            log_date=date.today()
        ).first() is not None

    @property
    def growth_percent(self) -> int:
        milestones = [0, 3, 7, 14, 21, 30]
        stage = min(self.current_stage, len(milestones) - 1)
        low   = milestones[stage - 1] if stage > 0 else 0
        high  = milestones[stage]      if stage < len(milestones) else milestones[-1]
        if high == low:
            return 100
        return min(100, int((self.streak - low) / (high - low) * 100))

    def complete_today(self, note: str = None):
        if self.done_today:
            return None

        log = HabitLog(
            habit_id=self.id,
            user_id=self.user_id,
            log_date=date.today(),
            completed=True,
            note=note,
        )
        db.session.add(log)

        self.streak   += 1
        self.is_wilted = False

        milestones = [3, 7, 14, 21, 30]
        if self.streak in milestones:
            max_s = self.plant.max_stage if self.plant else 5
            self.current_stage = min(self.current_stage + 1, max_s)

        db.session.commit()
        return log

    def wilt(self):
        self.is_wilted     = True
        self.streak        = 0
        self.current_stage = max(1, self.current_stage - 1)
        db.session.commit()

    def last_7_days(self) -> list:
        result = []
        logs = {
            log.log_date: log.completed
            for log in self.logs.filter(
                HabitLog.log_date >= date.today() - timedelta(days=6)
            ).all()
        }
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            result.append((d, logs.get(d, False)))
        return result

    def __repr__(self):
        return f"<Habit {self.name} stage={self.current_stage}>"


# MODEL: HabitLog
class HabitLog(db.Model):
    __tablename__ = "habit_logs"

    id        = db.Column(db.Integer, primary_key=True)
    habit_id  = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"),  nullable=False)
    log_date  = db.Column(db.Date,    nullable=False, default=date.today)
    completed = db.Column(db.Boolean, nullable=False, default=True)
    note      = db.Column(db.String(255))

    __table_args__ = (
        db.UniqueConstraint("habit_id", "log_date", name="uq_habit_log_date"),
    )

    def __repr__(self):
        return f"<HabitLog habit={self.habit_id} date={self.log_date}>"


# MODEL: Achievement

class Achievement(db.Model):
    __tablename__ = "achievements"

    id              = db.Column(db.Integer,     primary_key=True)
    title           = db.Column(db.String(100), nullable=False, unique=True)
    description     = db.Column(db.String(255), nullable=False)
    condition_type  = db.Column(
        db.Enum("streak", "total_habits", "full_garden", "total_logs"),
        nullable=False
    )
    condition_value = db.Column(db.Integer,    nullable=False)
    icon            = db.Column(db.String(10), nullable=False, default="🏅")

    user_achievements = db.relationship("UserAchievement", backref="achievement",
                                        lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Achievement {self.title}>"


# MODEL: UserAchievement
class UserAchievement(db.Model):
    __tablename__ = "user_achievements"

    id             = db.Column(db.Integer,  primary_key=True)
    user_id        = db.Column(db.Integer,  db.ForeignKey("users.id"),        nullable=False)
    achievement_id = db.Column(db.Integer,  db.ForeignKey("achievements.id"), nullable=False)
    earned_at      = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    def __repr__(self):
        return f"<UserAchievement user={self.user_id} ach={self.achievement_id}>"