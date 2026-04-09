-- INSERTING SOME RECORDS IN THE SCHEMA & TABLES CREATED
-- TO VERIFY THE INTEGRITY OF THE CREATED DATABASE

-- STARTING FROM FIRST TABLE "users"
-- CREATING A NEW USER WHO INITIATES THE WORKOUT SESSION

INSERT INTO workout.users(name,email_id) VALUES(
    'gurman','gurmancheema@gmail.com'
);

SELECT * FROM workout.users;

-- NOW THIS USER WILL HAVE A WORKOUT SESSION
-- THEREFORE, INSERTING VALUES TO "workout_session" TABLE

INSERT INTO workout.workout_sessions(user_id,workout_date,duration_minutes) VALUES (
    'a7e3e3ba-efac-4eb1-a048-1802c32247ec','2026-03-14',60
);

SELECT * FROM workout.workout_sessions;

-- NOW USER HAS DONE A WORKOUT SESSION
-- THEREFORE, INSERTING THE EXERCISE & ORDER OF EXERCISE THE USER PERFORMED
-- IN A SINGLE WORKOUT SESSION

INSERT INTO workout.workout_exercises(workout_session_id,exercise_id,exercise_order) VALUES
    ('48f542b2-06a0-4b5a-a11b-25f8a8351467',8,1),
    ('48f542b2-06a0-4b5a-a11b-25f8a8351467',9,2),
    ('48f542b2-06a0-4b5a-a11b-25f8a8351467',10,3),
    ('48f542b2-06a0-4b5a-a11b-25f8a8351467',11,4),
    ('48f542b2-06a0-4b5a-a11b-25f8a8351467',12,5);

SELECT * FROM workout.workout_exercises;

-- THE USER HAS PERFOMED EXERCISES IN ORDER IN A SINGLE WORKOUT SESSION
-- NOW LET'S TRACK THE SETS, REPS & WEIGHTS USED BY USER TO PERFORM THOSE
-- EXERCISES IN A SINGLE WORKOUT SESSION

INSERT INTO workout.exercises_sets(workout_exercises_id,set_number,reps,weight,duration_seconds) VALUES
    (1,1,12,25,12),
    (1,2,10,30,12),
    (1,3,10,37.5,12),
    (1,4,8,40,12),
    (2,1,12,30,15),
    (2,2,12,35,12),
    (2,3,12,40,12),
    (2,4,10,55,12),
    (3,1,12,25,12),
    (3,2,12,35,12),
    (3,3,12,40,12),
    (3,4,10,42.5,12),
    (4,1,12,25,15),
    (4,2,10,30,15),
    (4,3,10,37.5,15),
    (4,4,10,37.5,12),
    (5,1,10,20,12),
    (5,2,10,30,12),
    (5,3,10,35,10);

SELECT * FROM workout.exercises_sets;

INSERT INTO workout.exercises (exercise_name,muscle_group) VALUES 
                ('Standing Machine/Barbell Press','Shoulders'),
                ('Cable Lateral Raises','Shoulders'),
                ('Dumbbell Lateral Raises','Shoulders'),
                ('Seated Dumbbell Overhead Press','Shoulders'),
                ('Seated Dumbbell Arnold Press','Shoulders'),
                ('Seated Dumbbell Alternate Arnold Press','Shoulders'),
                ('Rear Delt Fly Machine','Shoulders'),
                ('Standing Dumbbell Shrugs','Shoulders'),
                ('Rope Face Pull','Shoulders'),
                ('Barbell Upright Rows','Shoulders'),
                ('Dumbbell Sumo Squats','Legs'),
                ('Seated Quads Extension','Legs'),
                ('Hamstring curls','Legs'),
                ('Leg Press Machine','Legs'),
                ('Standing Calves Raise','Legs'),
                ('Lunges','Legs'),
                ('Preacher Curl','Biceps'),
                ('Dumbbell Curl','Biceps'),
                ('Barbell Curl','Biceps'),
                ('Hammer Curl','Biceps'),
                ('Reverse Wrist Curl','Forearms'),
                ('Wrist Curl','Forearms');

INSERT INTO workout.exercises (exercise_name,muscle_group) VALUES 
    ('Treadmill','Cardio'),
    ('Elliptical','Cardio');

INSERT INTO workout.exercises (exercise_name,muscle_group) VALUES 
    ('Wide Grip Lat Pulldown','Back'),
    ('Reverse Grip Lat Pulldown (Wide)','Back'),
    ('Reverse Grip Lat Pulldown (Narrow)','Back'),
    ('Neutral Grip Lat Pulldown','Back'),
    ('Bent Over Cable Lat Pulldown','Back'),
    ('Bent Over Barbell Row','Back'),
    ('Seated Single Arm Row','Back'),
    ('Standing Bench Dumbbell Row','Back'),
    ('Bent Over T-Bar Row','Back'),
    ('Deadlift','Back'),
    ('Romanian Deadlift','Back'),
    ('Sumo Deadlift','Back'),
    ('Hyperextension','Back');

INSERT INTO workout.exercises (exercise_name,muscle_group) VALUES 
('Dumbbell Bench Press','Chest'),
('Incline Dumbbell Bench Press','Chest'),
('Barbell Bench Press','Chest'),
('Incline Barbell Bench Press','Chest'),
('Decline Dumbbell Bench Press','Chest'),
('Decline Barbell Bench Press','Chest'),
('Flat Bench Dumbbell Fly','Chest'),
('Incline Bench Dumbbell Fly','Chest'),
('Fly Machine','Chest'),
('Cable Fly','Chest');

SELECT * FROM workout.exercises;

-- if the SERIAL Count is out of sync, use the following code:
SELECT setval(
    pg_get_serial_sequence('workout.exercises', 'exercise_id'),
    (SELECT MAX(exercise_id) FROM workout.exercises)
);
SELECT MAX(exercise_id) FROM workout.exercises;
SELECT nextval('workout.exercises_exercise_id_seq');