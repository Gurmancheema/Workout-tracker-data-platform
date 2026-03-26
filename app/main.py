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

if st.button("Start Workout"):
    workout_session_id = create_workout_session(user_id_input,workout_date_input,duration_input)
    st.success(f"Workout Session Created,{workout_session_id}")
