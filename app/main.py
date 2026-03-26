print("helloworld")
import sys
print(sys.version)

# working on front-end now , since i decided to use streamlit therefore
# creating an instance & importing from it

import streamlit as st

print(st.__version__)

# importing the database connection files

from db import create_workout_session

# hard-coding front end
st.title("Workout_tracker")

user_id_input = st.text_input("Enter the user ID")

workout_date_input = st.date_input("Enter the workout date")

duration_input = st.number_input("Enter the expected workout duration in minutes")

# creating a session state to hold the values of some variables
# that are required throughout the environment
workout_session_id = st.session_state.get("workout_session_id")
if "workout_session_id" not in st.session_state:
    st.session_state["workout_session_id"] = None

if "set_number" not in st.session_state:
    st.session_state["set_number"] = 1

if st.button("Start Workout"):
    workout_session_id = create_workout_session(user_id_input,workout_date_input,duration_input)
    st.success(f"Workout Session Created,{workout_session_id}")
    st.session_state["workout_session_id"] = workout_session_id

# creating exercise dropdown UI

from db import get_all_exercises

exercises_dict ={}

exercises = get_all_exercises()
for exercise in exercises:
    exercise_id = exercise[0]
    name = exercise[1]
    muscle_group = exercise[2]
    display_name = name + " (" + muscle_group + ")"
    exercises_dict[display_name] = exercise_id

selected_exercise = st.selectbox("Select Exercise", list(exercises_dict.keys()))

from db import create_workout_exercises
if st.button("Add Exercise"):
    workout_session_id = st.session_state["workout_session_id"]
    exercise_id = exercises_dict[selected_exercise]

    workout_exercises_id = create_workout_exercises(
        workout_session_id,
        exercise_id,
        exercise_order=1  # we’ll improve this next
    )
    st.session_state["set_number"] = 1
    st.success(f"Exercise added! ID: {workout_exercises_id}")
    st.session_state["workout_exercises_id"] = workout_exercises_id

# UI to insert the sets, reps & weights into the table "exercises_sets"

from db import create_exercises_sets

st.subheader("Add Sets")

set_number = st.session_state["set_number"]
st.write(f"Set Number: {set_number}")
reps = st.number_input("Reps", min_value=1, step=1)
weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5)
duration_seconds = st.number_input("Duration (secs)", min_value = 5, step = 1)

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

        st.success(f"Set added! ID: {set_id}")
        st.session_state["set_number"] += 1

from db import get_exercises_for_workout
exercises_for_display = get_exercises_for_workout(st.session_state["workout_session_id"])

st.subheader("Workout Progress")

for ex in exercises_for_display:
    st.write(ex)