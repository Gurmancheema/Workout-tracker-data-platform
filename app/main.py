# working on front-end now , since i decided to use streamlit therefore
# creating an instance & importing from it

import streamlit as st
print(st.__version__)

# hard-coding front end to get basic user inputs required to Start a workout session
st.title("Workout Tracker")

user_name = st.text_input("Enter the Username")

workout_date_input = st.date_input("Enter the workout date")

duration_input = st.number_input("Enter the expected workout duration in minutes")

# creating a session state to hold the values of some variables
# that are required throughout the environment
workout_session_id = st.session_state.get("workout_session_id")
if "workout_session_id" not in st.session_state:
    st.session_state["workout_session_id"] = None

if "set_number" not in st.session_state:
    st.session_state["set_number"] = 1


# fetching user_id from the entered username from  the "users" table
from db import get_user_id

user_id_input = get_user_id(user_name)

# since now we have our user fetched from DB, let's fetch the function from DB that will store
# workout session details

from db import create_workout_session

if st.button("Start Workout"):
    workout_session_id = create_workout_session(user_id_input,workout_date_input,duration_input)
    st.success(f"Workout Session Created,{workout_session_id}")
    st.session_state["workout_session_id"] = workout_session_id


# At the press of "Start Workout" button, the workout session details will be inserted into DB
# and a unique workout_session_id will be created for that particular "user" for that particular "date"


# let's list some exercises for the user to perform in the created workout session
# therefore, importing the function from DB that fetches all exercises from "exercises" table

from db import get_all_exercises

st.subheader("Add Exercises")

exercises_dict ={}

exercises = get_all_exercises()
for exercise in exercises:
    exercise_id = exercise[0]
    name = exercise[1]
    muscle_group = exercise[2]
    display_name = name + " (" + muscle_group + ")"
    exercises_dict[display_name] = exercise_id


# creating exercise dropdown UI

options  = [None] + list(exercises_dict.keys())
selected_exercise = st.selectbox("Select Exercise",options, format_func= lambda x: "Select an exercise" if x is None else x)



from db import create_workout_exercises
if st.button("Add Exercise"):
    workout_session_id = st.session_state["workout_session_id"]
    if workout_session_id is None:
        st.warning("Please add workout session details")
    else:
        # adding a warning
        if selected_exercise is None:
            st.warning("Please select an exercise")
            st.stop()
        else:
            exercise_id = exercises_dict[selected_exercise]


    

        # fetch the current exercise order for the current workout session
        from db import get_exercises_order
        exercise_order = get_exercises_order(workout_session_id)

        workout_exercises_id = create_workout_exercises(
            workout_session_id,
            exercise_id,
            exercise_order
        )
        st.session_state["set_number"] = 1
        st.success(f"Exercise added! ID: {workout_exercises_id}")
        st.session_state["workout_exercises_id"] = workout_exercises_id

# UI to insert the sets, reps & weights into the table "exercises_sets"

from db import create_exercises_sets

st.subheader("Add Sets")

set_number = st.session_state["set_number"]
st.write(f"Set Number: {st.session_state['set_number']}")
reps = st.number_input("Reps", min_value=1, step=1)
weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5)
duration_seconds = st.number_input("Duration (secs)", min_value = 5, step = 1)

# Initialize message state
message_placeholder =st.empty()

if "success_message" not in st.session_state:
    st.session_state["success_message"] = None

if st.session_state["success_message"]:
    message_placeholder.success(st.session_state["success_message"])
    st.session_state["success_message"] = None
    
if st.button("Add Set"):
    workout_exercises_id = st.session_state.get("workout_exercises_id")

    if workout_exercises_id is None:
        st.error("Please add an exercise first")
    else:
        set_id = create_exercises_sets(
            workout_exercises_id,
            set_number,
            reps,
            weight,
            duration_seconds
        )

        st.session_state["success_message"] = f"Set {st.session_state['set_number']} added!"
        st.session_state["set_number"] += 1
        st.rerun()

st.subheader("Workout Progress")

from db import get_whole_workout_session

from collections import defaultdict

workout_session_id = st.session_state.get("workout_session_id")

if workout_session_id:
    rows = get_whole_workout_session(workout_session_id)
    grouped = defaultdict(list)

    for row in rows:
        exercise_key = (row[0], row[1], row[2], row[3])  
        grouped[exercise_key].append(row)
    
    for (we_id, name, muscle, order), sets in grouped.items():

        st.markdown(f"### {order}. {name} ({muscle})")

        for s in sets:
            st.write(
                f"Set {s[4]} | Reps: {s[5]} | Weight: {s[6]}"
        )
