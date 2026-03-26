-- SINCE THE TABLES ARE CREATED & VERIFIED
-- LET'S TRUNCATE THE TABLES TO INSERT THE ORIGINAL CORRECT RECORDS

-- TRUNCATING TABLES

TRUNCATE TABLE 
    workout.exercises_sets,
    workout.workout_exercises,
    workout.workout_sessions,
    workout.users
    RESTART IDENTITY CASCADE;