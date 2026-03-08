
USE habit_garden;

-- ============================================================
-- SEED: plants
-- The plant types users can choose for their habits
-- ============================================================
INSERT INTO plants (name, description, max_stage, css_class) VALUES
('Sunflower',   'Bright and energetic — great for morning habits',       5, 'plant-sunflower'),
('Cactus',      'Tough and resilient — perfect for hard habits',         5, 'plant-cactus'),
('Rose',        'Beautiful when cared for — ideal for self-care habits', 5, 'plant-rose'),
('Bamboo',      'Grows fast with consistency — for daily routines',      5, 'plant-bamboo'),
('Cherry Tree', 'Blooms with patience — for long-term goals',            5, 'plant-cherry'),
('Fern',        'Loves routine — great for reading or study habits',     5, 'plant-fern');

-- ============================================================
-- SEED: achievements
-- Milestone badges users can unlock
-- ============================================================
INSERT INTO achievements (title, description, condition_type, condition_value, icon) VALUES

-- streak-based
('First Spark',     'Complete a habit 3 days in a row',          'streak',       3,  '🔥'),
('Week Warrior',    'Complete a habit 7 days in a row',          'streak',       7,  '⚔️'),
('Monthly Master',  'Complete a habit 30 days in a row',         'streak',       30, '👑'),

-- habit count
('Gardener',        'Add your first habit',                      'total_habits', 1,  '🌱'),
('Plant Parent',    'Grow 3 habits at the same time',            'total_habits', 3,  '🪴'),
('Garden Master',   'Have 6 habits growing in your garden',      'total_habits', 6,  '🏡'),

-- full garden
('First Bloom',     'Grow one habit to its final stage',         'full_garden',  1,  '🌸'),
('Full Harvest',    'Grow 3 habits to their final stage',        'full_garden',  3,  '🌻'),

-- total logs
('Consistent',      'Log a habit completion 10 times total',     'total_logs',   10, '✅'),
('Dedicated',       'Log a habit completion 50 times total',     'total_logs',   50, '🎯'),
('Legendary',       'Log a habit completion 100 times total',    'total_logs',   100,'🏆');

-- ============================================================
-- SEED: demo user (password = "demo1234" — hashed in real app)
-- Use this only in development
-- ============================================================
INSERT INTO users (username, email, password) VALUES
('demo_user', 'demo@habitgarden.com', 'hashed_password_placeholder');

-- ============================================================
-- SEED: demo habits for demo_user (id = 1)
-- ============================================================
INSERT INTO habits (user_id, plant_id, name, description, frequency, current_stage, streak) VALUES
(1, 1, 'Morning Exercise',   'Work out for 30 minutes after waking up',    'daily',  3, 12),
(1, 3, 'Read 20 Pages',      'Read a book before bed every night',         'daily',  2, 5),
(1, 4, 'Drink 2L of Water',  'Stay hydrated throughout the day',           'daily',  4, 20),
(1, 5, 'Weekly Review',      'Review goals and plan the upcoming week',    'weekly', 2, 3);

-- ============================================================
-- SEED: demo habit logs (habit_id 1 = Morning Exercise)
-- ============================================================
INSERT INTO habit_logs (habit_id, user_id, log_date, completed, note) VALUES
(1, 1, CURDATE() - INTERVAL 6 DAY, TRUE,  'Great session!'),
(1, 1, CURDATE() - INTERVAL 5 DAY, TRUE,  NULL),
(1, 1, CURDATE() - INTERVAL 4 DAY, TRUE,  'Felt tired but pushed through'),
(1, 1, CURDATE() - INTERVAL 3 DAY, TRUE,  NULL),
(1, 1, CURDATE() - INTERVAL 2 DAY, TRUE,  'Personal best!'),
(1, 1, CURDATE() - INTERVAL 1 DAY, TRUE,  NULL),
(1, 1, CURDATE(),                  TRUE,  'Starting the day strong');

-- ============================================================
-- SEED: demo habit logs (habit_id 2 = Read 20 Pages)
-- ============================================================
INSERT INTO habit_logs (habit_id, user_id, log_date, completed, note) VALUES
(2, 1, CURDATE() - INTERVAL 4 DAY, TRUE, 'Finished a chapter'),
(2, 1, CURDATE() - INTERVAL 3 DAY, TRUE, NULL),
(2, 1, CURDATE() - INTERVAL 2 DAY, TRUE, 'Really engaging book'),
(2, 1, CURDATE() - INTERVAL 1 DAY, TRUE, NULL),
(2, 1, CURDATE(),                  TRUE, 'Almost done with the book');

-- ============================================================
-- SEED: demo user achievements
-- ============================================================
INSERT INTO user_achievements (user_id, achievement_id)
SELECT 1, id FROM achievements WHERE title IN ('First Spark', 'Gardener', 'Plant Parent', 'Consistent');
