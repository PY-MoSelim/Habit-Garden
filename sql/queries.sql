
USE habit_garden;

-- ============================================================
-- SECTION 1 — USER QUERIES
-- ============================================================

-- [1.1] Get a user by username (used during login)
SELECT id, username, email, password, created_at
FROM   users
WHERE  username = :username;

-- [1.2] Get a user by email (used to check if email already exists)
SELECT id, username, email
FROM   users
WHERE  email = :email;


-- ============================================================
-- SECTION 2 — HABIT QUERIES
-- ============================================================

-- [2.1] Get all habits for a specific user with their plant info
SELECT
    h.id,
    h.name                  AS habit_name,
    h.description,
    h.frequency,
    h.current_stage,
    h.streak,
    h.is_wilted,
    h.created_at,
    p.name                  AS plant_name,
    p.css_class             AS plant_css_class,
    p.max_stage
FROM   habits h
JOIN   plants p ON h.plant_id = p.id
WHERE  h.user_id = :user_id
ORDER  BY h.is_wilted ASC, h.streak DESC;

-- [2.2] Get a single habit by id (ownership check included)
SELECT
    h.id,
    h.name                  AS habit_name,
    h.description,
    h.frequency,
    h.current_stage,
    h.streak,
    h.is_wilted,
    p.name                  AS plant_name,
    p.css_class,
    p.max_stage
FROM   habits h
JOIN   plants p ON h.plant_id = p.id
WHERE  h.id = :habit_id
  AND  h.user_id = :user_id;

-- [2.3] Check if a habit was already logged today
SELECT id
FROM   habit_logs
WHERE  habit_id = :habit_id
  AND  log_date = CURRENT_DATE;

-- [2.4] Get the last 7 log entries for a habit (for the streak indicator)
SELECT log_date, completed, note
FROM   habit_logs
WHERE  habit_id = :habit_id
ORDER  BY log_date DESC
LIMIT  7;


-- ============================================================
-- SECTION 3 — GARDEN / DASHBOARD QUERIES
-- ============================================================

-- [3.1] Count how many habits the user has (used for achievements)
SELECT COUNT(*) AS total_habits
FROM   habits
WHERE  user_id = :user_id;

-- [3.2] Count how many habits reached the final stage (full_garden achievement)
SELECT COUNT(*) AS full_grown_habits
FROM   habits h
JOIN   plants p ON h.plant_id = p.id
WHERE  h.user_id    = :user_id
  AND  h.current_stage = p.max_stage;

-- [3.3] Count total log entries for a user (total_logs achievement)
SELECT COUNT(*) AS total_logs
FROM   habit_logs
WHERE  user_id = :user_id
  AND  completed = TRUE;

-- [3.4] Get the longest current streak across all habits for a user
SELECT MAX(streak) AS best_streak
FROM   habits
WHERE  user_id = :user_id;

-- [3.5] Full garden view — all habits with today's completion status
SELECT
    h.id,
    h.name                  AS habit_name,
    h.current_stage,
    h.streak,
    h.is_wilted,
    p.css_class,
    p.max_stage,
    CASE
        WHEN hl.id IS NOT NULL THEN TRUE
        ELSE FALSE
    END                     AS done_today
FROM   habits h
JOIN   plants p  ON h.plant_id    = p.id
LEFT JOIN habit_logs hl
       ON hl.habit_id = h.id
      AND hl.log_date = CURRENT_DATE
WHERE  h.user_id = :user_id
ORDER  BY done_today ASC, h.streak DESC;


-- ============================================================
-- SECTION 4 — ACHIEVEMENT QUERIES
-- ============================================================

-- [4.1] Get all achievements with earned status for a user
SELECT
    a.id,
    a.title,
    a.description,
    a.condition_type,
    a.condition_value,
    a.icon,
    CASE
        WHEN ua.id IS NOT NULL THEN TRUE
        ELSE FALSE
    END                     AS is_earned,
    ua.earned_at
FROM   achievements a
LEFT JOIN user_achievements ua
       ON ua.achievement_id = a.id
      AND ua.user_id        = :user_id
ORDER  BY is_earned DESC, a.condition_value ASC;

-- [4.2] Get only earned achievements for a user
SELECT
    a.title,
    a.description,
    a.icon,
    ua.earned_at
FROM   user_achievements ua
JOIN   achievements a ON ua.achievement_id = a.id
WHERE  ua.user_id = :user_id
ORDER  BY ua.earned_at DESC;

-- [4.3] Check if a specific achievement is already earned
SELECT id
FROM   user_achievements
WHERE  user_id       = :user_id
  AND  achievement_id = :achievement_id;


-- ============================================================
-- SECTION 5 — DEBUG / DEV QUERIES
-- (Useful during development — not used by the app directly)
-- ============================================================

-- [5.1] Overview: all habits across all users
SELECT
    u.username,
    h.name          AS habit,
    p.name          AS plant,
    h.current_stage,
    h.streak,
    h.is_wilted
FROM   habits h
JOIN   users  u ON h.user_id  = u.id
JOIN   plants p ON h.plant_id = p.id
ORDER  BY u.username, h.streak DESC;

-- [5.2] Habits that are wilted (missed)
SELECT
    u.username,
    h.name          AS habit,
    h.streak,
    h.updated_at
FROM   habits h
JOIN   users  u ON h.user_id = u.id
WHERE  h.is_wilted = TRUE;

-- [5.3] Full log history for a specific habit
SELECT
    hl.log_date,
    hl.completed,
    hl.note
FROM   habit_logs hl
WHERE  hl.habit_id = :habit_id
ORDER  BY hl.log_date DESC;

-- [5.4] Users with most achievements
SELECT
    u.username,
    COUNT(ua.id) AS total_achievements
FROM   user_achievements ua
JOIN   users u ON ua.user_id = u.id
GROUP  BY u.id, u.username
ORDER  BY total_achievements DESC;

-- [5.5] Reset a habit for testing (wilt it and reset streak)
UPDATE habits
SET    is_wilted    = TRUE,
       streak       = 0,
       current_stage = 1
WHERE  id = :habit_id;
