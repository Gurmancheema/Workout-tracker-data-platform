# Importing necessary packages
# Psycopg2-binary is necessary package to enable communication between Python & Postgresql
import psycopg2
import streamlit as st
# creating a function to establish database connection
# need only 4 arguments
def get_connection():
    return psycopg2.connect("postgresql://postgres.rydryqnizixrlqegivlq:gurmanjotnewpassword123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")

# creating a function that creates a new user
# will add a "sign-up" button to create the new user

def create_new_user(name,email_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" INSERT INTO workout.users (name,email_id) VALUES
                (%s,%s) RETURNING user_id;""",(name,email_id))
    
    resulting_user_id = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

# Creating a function that fetches the "user_id" from "user_name" entered by the user 
def get_user_id (user_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute (""" SELECT user_id FROM workout.users WHERE LOWER(name) = LOWER (%s);""",
                  (user_name,))
    
    user_id = cur.fetchone()

    cur.close()
    conn.close()

    return user_id

# creating a function that fetches the "user_id" & "workout_date" & looks for match in DB
# since , a user can have only one workout session per day, therefore, to avoid overriding
# although DB constraints are inplace, creating a function for supporting UI level constraint

def check_existing_session(user_id,workout_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" SELECT workout_session_id 
                    FROM workout.workout_sessions 
                    WHERE user_id = %s AND workout_date = %s""",(user_id,workout_date))
    
    resulting_workout_session_id = cur.fetchone()
    cur.close()
    conn.close()

    return resulting_workout_session_id

# creating a function that fetches the "user_id", "workout_date" and "workout_duration" from user input
# inserts theese values into the "workout_sessions" table
# then returns the "workout_session_id" & further closes the DB connection to avoid leaks
def create_workout_session(user_id,workout_date,start_time,end_time=None,duration=None):
    conn = get_connection()
    cur  = conn.cursor()

    # created a cursor object and this will execute the query
    cur.execute(""" INSERT INTO workout.workout_sessions (user_id,workout_date,start_time) VALUES
                (%s,%s,%s)
                RETURNING workout_session_id; """,(user_id,workout_date,start_time))
    
    # now fetching the returned "workout_id" from returned query
    workout_session_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return workout_session_id

# creating a function that will update the "workout_sessions" table when the user
# clicks on "finish workout" button, that will record the workout duration and end time

def update_workout_sessions(end_time,duration_minutes,workout_session_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" UPDATE workout.workout_sessions SET
                    end_time =%s, duration_minutes =%s
                WHERE workout_session_id = %s;""" ,(end_time,duration_minutes,workout_session_id))
    
    conn.commit()
    cur.close()
    conn.close()


# creating a function to fetch all the exercises listed in "exercises" table 
def get_all_exercises():
    conn = get_connection()
    cur = conn.cursor()

    # what this function does
    cur.execute(""" SELECT exercise_id, exercise_name, muscle_group FROM workout.exercises""")
    exercises = cur.fetchall()

    cur.close()
    conn.close()
    
    return exercises

# creating another function to insert the values into "workout_exercises" table
# this function returns the "workout_exerices_id"
# this table is junction/bridge table which connects three facts tables "workout_sessions","exercises" & "exercises_sets"

def create_workout_exercises(workout_session_id,exercise_id,exercise_order):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" INSERT INTO workout.workout_exercises (workout_session_id,exercise_id,exercise_order) VALUES 
                (%s,%s,%s) RETURNING workout_exercises_id; """,(workout_session_id,exercise_id,exercise_order))
    
    workout_exercises_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return workout_exercises_id

# finally creating a function that fetches the "sets","reps" & "weights" user performed
# in a single workout session
def create_exercises_sets(workout_exercises_id,set_number,reps,weight,duration_seconds):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" INSERT INTO workout.exercises_sets (workout_exercises_id,set_number,reps,weight,duration_seconds) VALUES
            (%s,%s,%s,%s,%s) RETURNING set_id;""" ,(workout_exercises_id,set_number,reps,weight,duration_seconds))
    
    set_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return set_id

# the "set_number" attribute shall increment automatically when a user clicks on "add set" button
# also when a user deletes or edits the wrongfully input "set_number", the set_number must fall back to 
# latest lowest number to preserve the incremental count
# therefore, defining a function that keeps track of "set_number" in "exercises_sets" table

def get_set_number(workout_exercises_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""SELECT set_number 
                FROM workout.exercises_sets
                WHERE workout_exercises_id = %s
                ORDER BY set_number;""", (workout_exercises_id,))
    
    rows = cur.fetchall()

    all_set_numbers_particular_to_workout_session = [row[0] for row in rows]

    cur.close()
    conn.close()

    next_set_num = 1

    for num in all_set_numbers_particular_to_workout_session:
        if num == next_set_num:
            next_set_num += 1
        else:
            break

    return next_set_num



# since the order of exercises performed must be incremented automatically each time user completes one exercise
# therefore, creating a function that fetches the latest count of "exercise_order" in "workout_exercises" table
# and increments it whenever the user adds a new exercise
def get_exercises_order(workout_session_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" SELECT COALESCE (MAX(exercise_order),0) FROM workout.workout_exercises
                WHERE workout_session_id = %s;""", (workout_session_id,))
    
    resulting_exercise_order = cur.fetchone()[0]
    cur.close()
    conn.close()

    return resulting_exercise_order + 1

# To track the progress of a workout session, creating a function that fetches the following from DB:
# 1. exercise_id, exercise_name, muscle_group from "exercises" table
# 2. set_number, reps, weight from "exercises_sets" table
# 3. since "workout_exercises" table is a junction table therefore, joining these 3 tables to get the analytics

def get_whole_workout_session(workout_session_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""SELECT e.exercise_id,e.exercise_name,e.muscle_group,
                we.exercise_order,
                es.set_id,
                es.set_number,
                es.reps,
                es.weight FROM workout.workout_exercises we
                JOIN workout.exercises_sets es
                ON we.workout_exercises_id = es.workout_exercises_id
                JOIN workout.exercises e
                ON we.exercise_id = e.exercise_id 
                WHERE we.workout_session_id = %s;""",(workout_session_id,))
    
    resulting_rows = cur.fetchall()
    conn.close()
    cur.close()

    return resulting_rows

# Edge case found that user can end the "workout session" by just adding "exercises" without any "sets"
# therefore, need a case handler for that; user must've performed atleast 1 set
# or the "workout session" shall be discarded and each detail entered so far
# shall be removed from the DB

def get_total_sets_per_workout_session(workout_session_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" SELECT COUNT(*) 
                    FROM workout.exercises_sets es
                    JOIN workout.workout_exercises we
                        ON es.workout_exercises_id = we.workout_exercises_id
                    WHERE we.workout_session_id = %s""",(workout_session_id,) )
    
    total_sets = cur.fetchone()[0]
    cur.close()
    conn.close()

    return total_sets

# since dual functionality is being offered to user whether to add sets or discard workout
# therefore, creating a function that discards the workout session and truncates the inserted values

def discard_workout(workout_session_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""DELETE FROM workout.workout_sessions 
                    WHERE workout_session_id = %s""",(workout_session_id,))
    
    conn.commit()
    cur.close()
    conn.close()
# now a user can accidentally input the wrong information of sets, reps or weights
# therefore, creating a "delete_set" function to provide editing features to the user

def delete_set(set_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" DELETE FROM workout.exercises_sets 
                    WHERE set_id = %s;""",(set_id,))
    
    conn.commit()
    cur.close
    conn.close()

# Creating a function to fetch the historical data of a user according to the date entered
# Useful for analytics and progress tracking, user shall access workout performed for each previous date

def fetch_historical_workout_data(user_id,workout_date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""SELECT e.exercise_name,e.muscle_group,
                we.exercise_order,
                we.exercise_id,
                es.set_number,
                es.reps,
                es.weight
                FROM workout.workout_sessions ws
                    JOIN workout.workout_exercises we
                        ON ws.workout_session_id = we.workout_session_id
                    JOIN workout.exercises e
                        ON e.exercise_id = we.exercise_id
                JOIN workout.exercises_sets es
                    ON es.workout_exercises_id = we.workout_exercises_id
                WHERE ws.user_id = %s 
                    AND 
                    ws.workout_date = %s
                ORDER BY we.exercise_order;""",(user_id,workout_date))
    
    resulting_historical_data = cur.fetchall()
    cur.close()
    conn.close()

    return resulting_historical_data