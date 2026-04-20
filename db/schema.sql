CREATE SCHEMA IF NOT EXISTS workout_tracker;

CREATE  TABLE workout_tracker.exercises ( 
	exercise_id          integer  NOT NULL  ,
	exercise_name        text  NOT NULL  ,
	body_part            text  NOT NULL  ,
	CONSTRAINT pk_exercises PRIMARY KEY ( exercise_id )
 );

CREATE  TABLE workout_tracker.exercises_sets ( 
	set_id               integer  NOT NULL  ,
	workout_exercise_id  integer  NOT NULL  ,
	set_number           integer  NOT NULL  ,
	reps                 integer  NOT NULL  ,
	weight               integer  NOT NULL  ,
	CONSTRAINT pk_exercises_sets PRIMARY KEY ( set_id ),
	CONSTRAINT unq_exercises_sets_workout_exercise_id UNIQUE ( workout_exercise_id ) 
 );

CREATE  TABLE workout_tracker.users ( 
	user_id              integer  NOT NULL  ,
	CONSTRAINT pk_users PRIMARY KEY ( user_id )
 );

CREATE  TABLE workout_tracker.workout_sessions ( 
	workout_id           integer  NOT NULL  ,
	user_id              integer  NOT NULL  ,
	workout_type         text  NOT NULL  ,
	workout_date         date  NOT NULL  ,
	CONSTRAINT pk_workout_sessions PRIMARY KEY ( workout_id ),
	CONSTRAINT fk_workout_sessions_users FOREIGN KEY ( user_id ) REFERENCES workout_tracker.users( user_id )   
 );

CREATE INDEX unq_workout_sessions_user_id ON workout_tracker.workout_sessions  ( user_id );

COMMENT ON COLUMN workout_tracker.workout_sessions.user_id IS 'will be FK to users table';

CREATE  TABLE workout_tracker.workout_exercises ( 
	workout_exercise_id  integer  NOT NULL  ,
	workout_id           integer  NOT NULL  ,
	exercise_id          integer  NOT NULL  ,
	CONSTRAINT pk_workout_exercises_0 PRIMARY KEY ( workout_exercise_id ),
	CONSTRAINT fk_workout_exercises_workout_sessions FOREIGN KEY ( workout_id ) REFERENCES workout_tracker.workout_sessions( workout_id )   ,
	CONSTRAINT fk_workout_exercises_exercises FOREIGN KEY ( exercise_id ) REFERENCES workout_tracker.exercises( exercise_id )   ,
	CONSTRAINT fk_workout_exercises_exercises_sets FOREIGN KEY ( workout_exercise_id ) REFERENCES workout_tracker.exercises_sets( workout_exercise_id )   
 );

CREATE INDEX pk_workout_exercises ON workout_tracker.workout_exercises  ( workout_exercise_id );

CREATE INDEX unq_workout_exercises_exercise_id ON workout_tracker.workout_exercises  ( exercise_id );

CREATE INDEX unq_workout_exercises_workout_id ON workout_tracker.workout_exercises  ( workout_id );

