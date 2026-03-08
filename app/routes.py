
from datetime import date
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify)
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, Plant, Habit, HabitLog, Achievement, UserAchievement

main = Blueprint("main", __name__)


# ── Helper: check and grant achievements ─────────────────────
def check_and_grant_achievements(user: User):
    newly_earned = []
    already_earned_ids = {
        ua.achievement_id for ua in user.user_achievements.all()
    }

    total_habits = user.habits.count()
    total_logs   = user.habit_logs.filter_by(completed=True).count()
    best_streak  = max((h.streak for h in user.habits.all()), default=0)
    full_grown   = sum(
        1 for h in user.habits.all()
        if h.plant and h.current_stage >= h.plant.max_stage
    )

    for ach in Achievement.query.all():
        if ach.id in already_earned_ids:
            continue
        earned = False
        ct, cv = ach.condition_type, ach.condition_value
        if ct == "streak"       and best_streak  >= cv: earned = True
        if ct == "total_habits" and total_habits  >= cv: earned = True
        if ct == "full_garden"  and full_grown    >= cv: earned = True
        if ct == "total_logs"   and total_logs    >= cv: earned = True

        if earned:
            db.session.add(UserAchievement(user_id=user.id, achievement_id=ach.id))
            newly_earned.append(ach)

    if newly_earned:
        db.session.commit()
    return newly_earned


# ============================================================
# AUTH ROUTES
# ============================================================

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.garden"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Welcome to your garden, {username}! 🌱", "success")
        return redirect(url_for("main.garden"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.garden"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user     = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.garden"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've left your garden. See you soon! 🌿", "info")
    return redirect(url_for("main.login"))


# ============================================================
# MAIN ROUTES
# ============================================================

@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.garden"))
    return redirect(url_for("main.login"))


@main.route("/garden")
@login_required
def garden():
    habits = (
        Habit.query
        .filter_by(user_id=current_user.id)
        .join(Habit.plant)
        .all()
    )
    plants      = Plant.query.all()
    total       = len(habits)
    done_today  = sum(1 for h in habits if h.done_today)
    best_streak = max((h.streak for h in habits), default=0)
    full_grown  = sum(1 for h in habits if h.plant and
                      h.current_stage >= h.plant.max_stage)

    return render_template(
        "index.html",
        habits      = habits,
        plants      = plants,
        total       = total,
        done_today  = done_today,
        best_streak = best_streak,
        full_grown  = full_grown,
        today       = date.today().strftime("%B %d, %Y"),
    )


@main.route("/habit/add", methods=["GET", "POST"])
@login_required
def add_habit():
    plants = Plant.query.all()

    if request.method == "POST":
        name        = request.form.get("name",        "").strip()
        description = request.form.get("description", "").strip()
        plant_id    = request.form.get("plant_id")
        frequency   = request.form.get("frequency", "daily")

        if not name or not plant_id:
            flash("Habit name and plant type are required.", "error")
            return render_template("add_habit.html", plants=plants)

        habit = Habit(
            user_id     = current_user.id,
            plant_id    = int(plant_id),
            name        = name,
            description = description,
            frequency   = frequency,
        )
        db.session.add(habit)
        db.session.commit()

        new_ach = check_and_grant_achievements(current_user)
        for a in new_ach:
            flash(f"Achievement unlocked: {a.icon} {a.title}!", "achievement")

        flash(f'"{name}" has been planted! 🌱', "success")
        return redirect(url_for("main.garden"))

    return render_template("add_habit.html", plants=plants)


@main.route("/habit/<int:habit_id>/complete", methods=["POST"])
@login_required
def complete_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    note  = request.json.get("note", "") if request.is_json else ""
    log   = habit.complete_today(note=note or None)

    if log is None:
        return jsonify({"status": "already_done", "message": "Already completed today!"}), 200

    new_ach = check_and_grant_achievements(current_user)

    return jsonify({
        "status":       "success",
        "message":      f"{habit.name} completed! 🎉",
        "new_stage":    habit.current_stage,
        "new_streak":   habit.streak,
        "is_wilted":    habit.is_wilted,
        "achievements": [{"title": a.title, "icon": a.icon} for a in new_ach],
    })


@main.route("/habit/<int:habit_id>/delete", methods=["POST"])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    flash(f'"{habit.name}" has been removed from your garden.', "info")
    return redirect(url_for("main.garden"))


@main.route("/achievements")
@login_required
def achievements():
    all_achievements = Achievement.query.order_by(
        Achievement.condition_type, Achievement.condition_value
    ).all()

    earned_ids = {
        ua.achievement_id: ua.earned_at
        for ua in current_user.user_achievements.all()
    }

    ach_data = [{
        "achievement": a,
        "earned":      a.id in earned_ids,
        "earned_at":   earned_ids.get(a.id),
    } for a in all_achievements]

    return render_template(
        "achievements.html",
        ach_data     = ach_data,
        total_earned = len(earned_ids),
        total_all    = len(all_achievements),
    )