-- adding constraint as a single user was adding same
-- exercise multiple times during same workout session
ALTER TABLE workout.workout_exercises
ADD CONSTRAINT unique_workout_session_and_exercise_id
UNIQUE(workout_session_id,exercise_id);


-- convert created_at to timezone-aware timestamp
-- ensures consistency across different regions and avoids timezone-related bugs
ALTER TABLE workout.exercises
ALTER column created_at TYPE TIMESTAMPTZ;


-- enforce case-insensitive uniqueness on username
-- prevents duplicates like "John", "john", "JOHN"
CREATE UNIQUE INDEX unique_lower_name
ON workout.users (LOWER(name));


-- enforce case-insensitive uniqueness on email
-- prevents duplicates like "test@gmail.com" vs "TEST@gmail.com"
CREATE UNIQUE INDEX unique_lower_email_id
ON workout.users (LOWER(email_id));


-- query to inspect all constraints on users table
-- useful for debugging and verifying applied constraints
SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(c.oid) AS definition
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'users';


-- query to inspect all indexes on users table
-- helps verify unique indexes and performance-related indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'users';


-- restrict one workout session per user per day
-- prevents duplicate sessions for same date (data consistency)
ALTER TABLE workout.workout_sessions
ADD CONSTRAINT unique_user_date_per_workout_session
UNIQUE(user_id,workout_date);


-- enforce that username cannot be NULL
-- ensures every user record has a valid name
ALTER TABLE workout.users
ALTER COLUMN name SET NOT NULL;


-- enforce that username is not empty or just whitespace
-- prevents invalid entries like "", "   "
ALTER TABLE workout.users
ADD CONSTRAINT username_not_empty CHECK (length(trim(name)) > 0);


-- add start and end time columns for better workout tracking
-- replaces dependency on duration-only model
ALTER TABLE workout.workout_sessions
ADD COLUMN start_time TIMESTAMP,
ADD COLUMN end_time TIMESTAMP;


-- allow duration to be nullable
-- needed because duration is now derived from start_time and end_time
-- especially useful for live workouts where end_time is not immediately available
ALTER TABLE workout.workout_sessions
ALTER COLUMN duration_minutes DROP NOT NULL;

