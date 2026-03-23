SELECT current_database();

-- Creating table "users" and defining the column names
-- using UUID (universal unique indentifier) to generate user_ids
-- defining data types, null types and finally the constraints

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS workout.users(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    email_id VARCHAR(150) UNIQUE  NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Creating table "workout_sessions" and defining the column names
-- using UUID (universal unique indentifier) to workout_session_id 
-- defining data types, null types and finally the constraints

CREATE TABLE IF NOT EXISTS workout.workout_sessions(

    workout_session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    duration_minutes INT NOT NULL,
    workout_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user FOREIGN KEY (user_id)
                       REFERENCES workout.users(user_id)
                       ON DELETE CASCADE
);

-- Creating table "exercises" and defining the column names
-- using SERIAL to exercise_id 
-- defining data types, null types and finally the constraints

CREATE TABLE workout.exercises (
    exercise_id SERIAL PRIMARY KEY,
    exercise_name VARCHAR(150) NOT NULL,
    muscle_group VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CREATING A BRIDGE/JUNCTION TABLE "workout_exercises" WHERE ARE ALL THE ABOVE 3 TABLES
-- WILL SHARE INFORMATION & PROVIDE ANALYTICS
-- THIS TABLE WILL HAVE MANY TO MANY RELATIONSHIP

CREATE TABLE workout.workout_exercises (
    workout_exercises_id SERIAL PRIMARY KEY,
    workout_session_id UUID NOT NULL,
    exercise_id SERIAL NOT NULL,
    exercise_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workout_session FOREIGN KEY (workout_session_id)
                                  REFERENCES workout.workout_sessions(workout_session_id) ON DELETE CASCADE,

    CONSTRAINT fk_exercise FOREIGN KEY (exercise_id)
                           REFERENCES workout.exercises(exercise_id) ON DELETE CASCADE
);

-- CREATING EXERCISES_SETS TABLE TO TRACK THE SETS,REPS & WEIGHTS 
-- THIS IS THE ULITMATE TRACKING TABLE TRACKING THE PROGRESS

CREATE TABLE IF NOT EXISTS workout.exercises_sets (
    set_id SERIAL PRIMARY KEY,
    workout_exercises_id INT NOT NULL,
    set_number INT NOT NULL,
    reps INT NOT NULL,
    weight FLOAT NOT NULL,
    duration_seconds INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workout_exercise FOREIGN KEY (workout_exercises_id) 
                                    REFERENCES workout.workout_exercises(workout_exercises_id)
                                    ON DELETE CASCADE
);
