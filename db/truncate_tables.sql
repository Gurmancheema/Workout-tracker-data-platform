-- SINCE THE TABLES ARE CREATED & VERIFIED
-- LET'S TRUNCATE THE TABLES TO INSERT THE ORIGINAL CORRECT RECORDS

-- TRUNCATING TABLES

TRUNCATE TABLE 
    workout.exercises_sets,
    workout.workout_exercises,
    workout.workout_sessions
    RESTART IDENTITY CASCADE;

SELECT * FROM workout.exercises_sets;
SELECT * FROM workout.workout_exercises;
SELECT * FROM workout.workout_sessions;
SELECT * FROM workout.users;
SELECT * FROM workout.exercises;