# working on front-end now , since i decided to use streamlit therefore
# creating an instance & importing from it

import streamlit as st
print(st.__version__)

# hard-coding front end to get basic user inputs required to Start a workout session
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide"
    )
left, center, right = st.columns([1, 3, 1])

with center:
    st.markdown("## 💪 Workout Tracker")
    st.caption("Track your workouts efficiently")

    st.markdown("### 🏁 Start Workout")

# for columnar format on page
# let's fetch values from user on same page without letting the user to scroll down

#defining column ratios
    col1, col2, col3 = st.columns([2, 2, 1.5])

# creating column labels
    col1.markdown("**User**")
    col2.markdown("**Date**")
    col3.markdown("**Duration**")
#col4.markdown("**Duration (min)**")
#col5.markdown("**Action**")

# defining column placeholders

    with col1:
        user_name = st.text_input("Username",key="user_name",label_visibility="collapsed")

    with col2:
        workout_date_input = st.date_input("Workout Date",key="workout_date",label_visibility="collapsed")

    with col3:
        duration_input = st.number_input("Workout Duration",min_value=10,step=1,key="workout_duration",label_visibility="collapsed")

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

with center:
    if st.button("Start Workout"):
        workout_session_id = create_workout_session(user_id_input,workout_date_input,duration_input)
        st.success(f"Workout Session Created,{workout_session_id}")
        st.session_state["workout_session_id"] = workout_session_id

    st.divider()


# At the press of "Start Workout" button, the workout session details will be inserted into DB
# and a unique workout_session_id will be created for that particular "user" for that particular "date"


    st.markdown("### 🏋️ Select Exercise")

# let's list some exercises for the user to perform in the created workout session
# therefore, importing the function from DB that fetches all exercises from "exercises" table

from db import get_all_exercises
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
with center:
    col7 = st.columns([2])

    with col7[0]:
        selected_exercise = st.selectbox("Select Exercise",options, format_func= lambda x: "Select an exercise" if x is None else x
                                    ,label_visibility="collapsed")





with center:
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

            from db import create_workout_exercises
            workout_exercises_id = create_workout_exercises(
                workout_session_id,
                exercise_id,
                exercise_order
            )
            st.success(f"Exercise added! ID: {workout_exercises_id}")
            st.session_state["workout_exercises_id"] = workout_exercises_id

# UI to insert the sets, reps & weights into the table "exercises_sets"

from db import create_exercises_sets

with center:
    st.divider()
    st.markdown("### 🏋️ Add Sets")

    col8,col4, col5, col6 = st.columns([1, 1, 1, 1])
    col8.markdown("**Set Number**")
    col4.markdown("**Reps**")
    col5.markdown("**Weight**")
    col6.markdown("**Duration**")

    from db import get_set_number
    workout_exercises_id = st.session_state.get("workout_exercises_id")

    if workout_exercises_id is None:
        st.error("Please add an exercise first")
        st.stop()
    set_number = get_set_number(workout_exercises_id)
    with col8:
        st.markdown(f"**{set_number}**")

    # handling the reset for user inputs before the widgets are created
    # streamlit behaviour => Update session_state → THEN rerun → THEN UI reflects change

    if "reset_inputs" in st.session_state and st.session_state["reset_inputs"]:
        st.session_state["reps"] = 1
        st.session_state["duration"] = 5
        st.session_state["reset_inputs"] = False
    with col4:
        reps = st.number_input("Reps", min_value=1, step=1, key= 'reps',label_visibility="collapsed")

    with col5:
        weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5,key='weight',label_visibility="collapsed")

    with col6:
        duration_seconds = st.number_input("Duration (secs)", min_value = 5, step = 1,key= 'duration',label_visibility="collapsed")


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

            # display the success message for added set
            st.session_state["success_message"] = f"Set {set_number} added!"

            # reset the inputs flag trigger
            st.session_state["reset_inputs"] = True

            st.rerun()
st.divider()



st.markdown("### 📊 Workout Progress")
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

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        col1.markdown("**Set**")
        col2.markdown("**Reps**")
        col3.markdown("**Weight**")
        col4.markdown("**Action**")

        for s in sets:
            (we_id,
            name,
            muscle,
            order,
            set_id,
            set_number,
            reps,
            weight
        ) = s
            col1, col2, col3, col4= st.columns([1, 1, 1, 1])

            with col1:
                st.markdown(f"{set_number}")

            with col2:
                st.markdown(f"{reps}")

            with col3:
                st.markdown(f"{weight}")
            
            with col4:
                if st.button("🗑️",key=f"delete_{set_id}"):

                    #import delete_set function from DB

                    from db import delete_set
                    delete_set(set_id)
                    st.rerun()



















# creating a close workout session button when the user is finished with his workout

st.divider()

with center:
    col1,col2,col3 = st.columns([2,2,2])

    with col2:
        finish_button = st.button("🏁 Finish Workout", use_container_width=True)

    # now if the button is clicked, user must see a warning prompt before closing the session

    if finish_button:
        st.session_state["confirm_finish_workout"] = True

    if st.session_state.get("confirm_finish_workout"):

        # prompt warning message
        st.warning("Are you sure you want to finish the workout?")

        col1,col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, Finish"):
                 #CLEAR STATE
                keys_to_clear = [
                    "workout_session_id",
                    "workout_exercises_id",
                    "set_number"
                ]

                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # after resetting keys again set the confirm_finish_session state to False
                st.session_state["confirm_finish_workout"] = False

                st.success("Workout Finished")
                st.rerun()

        with col2:
            if st.button("❌ No, Cancel"):
                st.session_state["confirm_finish_workout"] = False
                st.rerun()