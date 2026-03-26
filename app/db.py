# creating a database connection
import psycopg2

def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        database='workout_tracker',
        user = 'postgres',
        password = 'password'
)

# creating a function that gets user_id, workout_date and workout_duration
# inserts the values into the workout_sessions table
# then returns the workout_id & further closes the DB connection to avoid leaks
def create_workout_session(user_id,workout_date,duration_minutes):
    conn = get_connection()
    cur  = conn.cursor()

    # created a cursor object and this will execute the query
    cur.execute(""" INSERT INTO workout.workout_sessions (user_id,workout_date,duration_minutes) VALUES
                (%s,%s,%s)
                RETURNING workout_session_id; """,(user_id,workout_date,duration_minutes))
    
    # now fetching the returned "workout_id" from returned query
    workout_session_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return workout_session_id

# creating a function to fetch all exercises 

def get_all_exercises():
    conn = get_connection()
    cur = conn.cursor()

    # what this function does
    cur.execute(""" SELECT exercise_id, exercise_name, muscle_group FROM workout.exercises""")
    exercises = cur.fetchall()

    cur.close()
    conn.close()
    
    return exercises

# creating another function to insert the values into workout_exercises table

def create_workout_exercises(workout_session_id,exercise_id,exercise_order):
    conn = get_connection()
    cur = conn.cursor()

    # what this function does is insert the values into workout_exercises table
    cur.execute(""" INSERT INTO workout.workout_exercises (workout_session_id,exercise_id,exercise_order) VALUES 
                (%s,%s,%s) RETURNING workout_exercises_id; """,(workout_session_id,exercise_id,exercise_order))
    
    workout_exercises_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return workout_exercises_id

# finally creating a function insert the sets,reps & weights user performed
# in a single workout session , fetching the performed exercises and workout session
# from workout_exercises table

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

def get_exercises_for_workout(workout_session_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT we.workout_exercises_id, e.exercise_name
        FROM workout.workout_exercises we
        JOIN workout.exercises e
        ON we.exercise_id = e.exercise_id
        WHERE we.workout_session_id = %s;
    """, (workout_session_id,))

    data = cur.fetchall()

    cur.close()
    conn.close()

    return data