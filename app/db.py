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