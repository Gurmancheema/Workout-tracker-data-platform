import psycopg2

# creating a function to establish database connection
# need only 4 arguments
def get_connection():
    return psycopg2.connect(
        host = 'localhost',
        database='workout_tracker',
        user = 'postgres',
        password = 'password'
)
def get_timzone():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SET timezone = 'Asia/Kolkata';")
    cur.execute("SHOW timezone;")
    print(cur.fetchone())
    conn.commit()

get_timzone()