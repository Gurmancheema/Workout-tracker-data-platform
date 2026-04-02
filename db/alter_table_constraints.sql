ALTER TABLE workout.workout_exercises
ADD CONSTRAINT unique_workout_session_and_exercise_id
UNIQUE(workout_session_id,exercise_id)

ALTER TABLE workout.exercises
ALTER column created_at TYPE TIMESTAMPTZ;

CREATE UNIQUE INDEX unique_lower_name
ON workout.users (LOWER(name));

CREATE UNIQUE INDEX unique_lower_email_id
ON workout.users (LOWER(email_id));

SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(c.oid) AS definition
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'users';

SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'users';

ALTER TABLE workout.workout_sessions
ADD CONSTRAINT unique_user_date_per_workout_session
UNIQUE(user_id,workout_date);

ALTER TABLE workout.users
ALTER COLUMN name SET NOT NULL;
ALTER TABLE workout.users
ADD CONSTRAINT username_not_empty CHECK (length(trim(name)) > 0);