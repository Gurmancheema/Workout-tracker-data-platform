SELECT current_database();

-- Creating table "users" and defining the column names
-- using UUID (universal unique indentifier) to generate user_ids
-- data types, null types and finally the constraints

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS workout.users(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    email_id VARCHAR(150) UNIQUE  NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- INSERTING SOME VALUES IN THE TABLE

INSERT INTO workout.users (name,email_id) VALUES
    ('gurman','gurman@test.com'),
    ('cheema','cheema@test.com');

SELECT * FROM workout.users;

-- CREATING TABLE WORKOUT_SESSIONS

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


-- INSERTING VALUES INTO WORKOUT_SESSION TABLE TO VERIFY SCHEMA

INSERT INTO workout.workout_sessions (user_id,duration_minutes,workout_date) VALUES
    ('138a0d43-fc96-4b7a-9ddf-792376be59b9',45,'2026-03-20');


-- CREATING TABLE EXERCISES

CREATE TABLE workout.exercises (
    exercise_id SERIAL PRIMARY KEY,
    exercise_name VARCHAR(150) NOT NULL,
    muscle_group VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INSERTING VALUES INTO EXERCISES TABLE

INSERT INTO workout.exercises (exercise_id,exercise_name,muscle_group) VALUES 
    (1,'Incline Barbell Press','Chest'),
    (2,'Flat Dumbbell Press','Chest'),
    (3,'Fly Machine','Chest'),
    (4,'Incline Dummbell Press','Chest'),
    (5,'Straight Bar Tricep Pushdown','Triceps'),
    (6,'Seated Dumbbell Tricep Extension','Triceps'),
    (7,'Standing Tricep Cable Extension','Triceps'),
    (8,'Wide Grip Lat Pulldown','Back'),
    (9,'Bent Over Barbell Rows','Back'),
    (10,'Seated Machine Rows','Back'),
    (11,'Close Reverse Grip Lat Pulldown','Back'),
    (12,'T-Bar Rows','Back');

-- CREATING A BRIDGE/JUNCTION TABLE WHERE ARE ALL THE ABOVE 3 TABLES
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

-- INSERTING VALUES INTO THIS TABLE TO VERIFY SCHEMA

INSERT INTO workout.workout_exercises(workout_session_id,exercise_id,exercise_order) VALUES 
    ('da9824a2-d48b-46c5-8a49-e5c386845862',4,1);

DROP TABLE workout.users;

SELECT * FROM workout.exercises;SELECT * FROM workout.workout_exercises;