
-- Create and select the database
CREATE DATABASE IF NOT EXISTS habit_garden
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE habit_garden;

-- ============================================================
-- TABLE: users
-- Stores registered users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id          INT             AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)     NOT NULL UNIQUE,
    email       VARCHAR(120)    NOT NULL UNIQUE,
    password    VARCHAR(255)    NOT NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: plants
-- Defines all available plant types a habit can become
-- ============================================================
CREATE TABLE IF NOT EXISTS plants (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(50)     NOT NULL UNIQUE,
    description     VARCHAR(255),
    max_stage       INT             NOT NULL DEFAULT 5,
    -- stage 1 = seed | 2 = sprout | 3 = growing | 4 = blooming | 5 = fully grown
    css_class       VARCHAR(50)     NOT NULL
    -- CSS class used in the frontend to render the correct plant visual
);

-- ============================================================
-- TABLE: habits
-- Stores each habit created by a user
-- ============================================================
CREATE TABLE IF NOT EXISTS habits (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    plant_id        INT             NOT NULL,
    name            VARCHAR(100)    NOT NULL,
    description     VARCHAR(255),
    frequency       ENUM('daily','weekly') NOT NULL DEFAULT 'daily',
    current_stage   INT             NOT NULL DEFAULT 1,
    -- 1=seed, 2=sprout, 3=growing, 4=blooming, 5=fully grown
    streak          INT             NOT NULL DEFAULT 0,
    -- consecutive days/weeks the habit was completed
    is_wilted       BOOLEAN         NOT NULL DEFAULT FALSE,
    -- TRUE if the user missed the habit and the plant is dying
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_habits_user
        FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_habits_plant
        FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE RESTRICT
);

-- ============================================================
-- TABLE: habit_logs
-- Records every time a user marks a habit as done
-- ============================================================
CREATE TABLE IF NOT EXISTS habit_logs (
    id          INT         AUTO_INCREMENT PRIMARY KEY,
    habit_id    INT         NOT NULL,
    user_id     INT         NOT NULL,
    log_date    DATE        NOT NULL DEFAULT (CURRENT_DATE),
    completed   BOOLEAN     NOT NULL DEFAULT TRUE,
    note        VARCHAR(255),
    -- optional note the user can attach to the log entry

    UNIQUE KEY uq_habit_log_date (habit_id, log_date),
    -- one log entry per habit per day

    CONSTRAINT fk_logs_habit
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    CONSTRAINT fk_logs_user
        FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE
);

-- ============================================================
-- TABLE: achievements
-- Defines available milestone badges
-- ============================================================
CREATE TABLE IF NOT EXISTS achievements (
    id              INT             AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(100)    NOT NULL UNIQUE,
    description     VARCHAR(255)    NOT NULL,
    condition_type  ENUM(
                        'streak',       -- earned after N consecutive days
                        'total_habits', -- earned when user has N habits
                        'full_garden',  -- earned when N habits reach max stage
                        'total_logs'    -- earned after N total log entries
                    ) NOT NULL,
    condition_value INT             NOT NULL,
    -- the threshold number that triggers the achievement
    icon            VARCHAR(10)     NOT NULL DEFAULT '🏅'
);

-- ============================================================
-- TABLE: user_achievements
-- Junction table — tracks which user earned which achievement
-- ============================================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id              INT         AUTO_INCREMENT PRIMARY KEY,
    user_id         INT         NOT NULL,
    achievement_id  INT         NOT NULL,
    earned_at       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_user_achievement (user_id, achievement_id),

    CONSTRAINT fk_ua_user
        FOREIGN KEY (user_id)        REFERENCES users(id)        ON DELETE CASCADE,
    CONSTRAINT fk_ua_achievement
        FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
);
