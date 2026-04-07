# working on front-end now , since i decided to use streamlit therefore
# Importing streamlit & necessary python packages
import streamlit as st
print(st.__version__)
from datetime import date


# setting page configuration
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide"
    )
left, center, right = st.columns([1, 3, 1])

# ********* NOTIFICATIONS SECTION *************

if st.session_state.get("workout_finished"):
    st.success("Workout finished successfully!")
    st.session_state["workout_finished"] = False

# defining a message placeholder if the user discards the workout 
# process to print the success message
message_placeholder_for_discarded_workout = st.empty()

if "message_for_discarded_workout" not in st.session_state:
    st.session_state["message_for_discarded_workout"] = None

if st.session_state["message_for_discarded_workout"]:
    message_placeholder_for_discarded_workout.success(st.session_state["message_for_discarded_workout"])
    st.session_state["message_for_discarded_workout"] = None

# ******* UI RENDERING STATES ***********
if "show_signup" not in st.session_state:
    st.session_state["show_signup"] = False

if "show_history" not in st.session_state:
    st.session_state["show_history"] = False

# ************ RENDER FUNCTIONS DEFINITIONS ********************

# 1. RENDER WORKOUT HISTORY

def render_history_ui():
    with center:
        st.markdown("## 💪 Workout Tracker")
        st.caption("Track your workouts efficiently")
        st.subheader("Workout History")

        user_name_input = st.text_input("Enter username",key="history_username")
        past_workout_date_input = st.date_input("Select workout day",key="history_date")
        
        if st.button("Fetch Workout"):
            from db import get_user_id
            related_user_id = get_user_id(user_name_input)

            # edge case handling if user is not registered
            if not related_user_id:
                st.error("User not found!")
                return

            from db import fetch_historical_workout_data
            hist_data = fetch_historical_workout_data(
                related_user_id,
                past_workout_date_input
            )

            # printing the fetched historical data now
            current_exercise = None

            for row in hist_data:
                exercise_name, muscle_group, exercise_order, exercise_id, set_number, reps, weight = row

                # when new exercise starts
                if exercise_name != current_exercise:
                    st.markdown("---")
                    st.markdown(f"### {exercise_order}. 💪 {muscle_group} - {exercise_name}")
                    current_exercise = exercise_name

                st.write(f"Set {set_number} → {reps} reps | {weight} kg")

            st.markdown("## 📊 Performance Summary")

            exercise_stats = {}

            for row in hist_data:
                exercise_name, _, _, _, _, reps, weight = row

                if exercise_name not in exercise_stats:
                    exercise_stats[exercise_name] = {"max_weight": 0, "max_reps": 0}

                exercise_stats[exercise_name]["max_weight"] = max(
                    exercise_stats[exercise_name]["max_weight"], weight
                )
                exercise_stats[exercise_name]["max_reps"] = max(
                    exercise_stats[exercise_name]["max_reps"], reps
                )

            for exercise, stats in exercise_stats.items():
                st.write(
                    f"{exercise} → Max Weight: {stats['max_weight']} kg | Max Reps: {stats['max_reps']}"
                )

        if st.button("⬅ Back"):
            st.session_state["show_history"] = False
            st.rerun()


 # 2. RENDER SIGN UP 

def render_signup_ui():
    from db import create_new_user
    import psycopg2
    from psycopg2 import errors

    # creating function to check that either of entered credentials are not left empty

    def check_credentials_and_insert(name,email_id):
        if not name or not email_id:
            st.error("All fields are required")
            return
        
        try:
            create_new_user(name.strip(),email_id.strip())
            st.success("User profile created")

            # reset the fields now
            st.session_state["show_signup"] = False

            return

        except psycopg2.Error as e:

            if isinstance(e, psycopg2.errors.UniqueViolation):
                constraint = e.diag.constraint_name

                if "name" in constraint:
                    st.error("Username already exists")
                elif "email" in constraint:
                    st.error("Email already exists")
            else:
                st.error("Something went wrong")
        return
    
    # Enter new user details
    with center:
        if st.session_state["show_signup"]:
            st.markdown("## 💪 Workout Tracker")
            st.caption("Track your workouts efficiently")
            st.subheader("Create new user")

            signup_name = st.text_input("Enter the username",key="signup_name")
            signup_email = st.text_input("Enter the email",key='signup_email')

            col1,col2 = st.columns(2)

            # creating buttons and defining their actions
            with col1:
                if st.button("Create Account"):
                    check_credentials_and_insert(signup_name,signup_email)
            
            with col2:
                if st.button("Cancel"):
                    st.session_state["show_signup"] = False
                    st.rerun()

# Aligning configurations for feature buttons
with right:    
    col_left , col_right = st.columns([2,5])

# Feature buttons working
with col_right:
    if st.button("Sign Up"):
        st.session_state["show_signup"] = True
    if st.button("Workout History"):
        st.session_state["show_history"] = True

# Render functions flag
if st.session_state.get("show_history"):
    render_history_ui()
    st.stop()

if st.session_state.get("show_signup"):
    render_signup_ui()
    st.stop()

 # **************** Main UI TO TRACK WORKOUT *****************************
from datetime import datetime
with center:
    st.markdown("## 💪 Workout Tracker")
    st.caption("Track your workouts efficiently")
    st.markdown("### 🏁 Start Workout")



    # adding timer UI
    start_time = st.session_state.get("start_time")
    if start_time:
        duration = datetime.now() - start_time
        minutes = int(duration.total_seconds() // 60)



# defining column ratios
with center:
    col1, col2, col3 = st.columns([2, 2, 1.5])

    # creating column labels
    col1.markdown("**User**")
    col2.markdown("**Date**")
    col3.markdown("**Time**")

    mode = st.radio("Workout Mode",
    ["Live Workout", "Log Past Workout"],
    horizontal=True, key= 'mode'
)

if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False

if st.session_state["reset_form"]:
    st.session_state["user_name"] = ""
    st.session_state["workout_date"] = date.today()
    st.session_state["workout_duration"] = 10  # respect min_value
    st.session_state["select_exercise"] = "Select Exercise"

    st.session_state["reset_form"] = False
# defining column placeholders
with center:
    with col1:
        user_name = st.text_input("Username",key="user_name",label_visibility="collapsed")

    with col2:
        workout_date_input = st.date_input("Workout Date",key="workout_date",label_visibility="collapsed")

    with col3:
        current_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f"**🕒{current_time}**")

# creating a session state to hold the values of some variables
# that are required throughout the environment
workout_session_id = st.session_state.get("workout_session_id")
if "workout_session_id" not in st.session_state:
    st.session_state["workout_session_id"] = None

if "set_number" not in st.session_state:
    st.session_state["set_number"] = 1




# since now we have our user fetched from DB, let's fetch the function from DB that will store
# workout session details

from db import create_workout_session
from datetime import datetime
with center:
    if st.button("Start Workout"):
        from db import get_user_id
        # checking empty or null value for username
        if not user_name:
            st.error("Username cannot be null")
            st.stop()
        user_id_input = get_user_id(user_name)

        if st.session_state["mode"] == "Live Workout":
            start_time = datetime.now()
            end_time = None
            duration = None
                    
            workout_session_id = create_workout_session(user_id_input,workout_date_input,start_time)
            st.success(f"Workout Session Created,{workout_session_id}")
            st.session_state["workout_session_id"] = workout_session_id
            st.session_state["start_time"] = start_time

    else:  # Log Past Workout
        # you'll handle later
        start_time = None
        end_time = None
        #duration = user_input_duration
        # fetching user_id from the entered username from  the "users" table
        


    st.divider()


# At the press of "Start Workout" button, the workout session details will be inserted into DB
# and a unique workout_session_id will be created for that particular "user" for that particular "date"


    st.markdown("### 🏋️ Select Exercise")

# let's list some exercises for the user to perform in the created workout session
# therefore, importing the function from DB that fetches all exercises from "exercises" table
from collections import defaultdict
from db import get_all_exercises
exercises_dict ={}

exercises = get_all_exercises()
muscle_to_exercises = defaultdict(list)

for exercise in exercises:
    exercise_id = exercise[0]
    name = exercise[1]
    muscle_group = exercise[2]
    display_name = name
    exercises_dict[display_name] = exercise_id

# creating a list for muscle groups
    muscle_to_exercises[muscle_group].append({
        "id":exercise_id,
        "name":name,
        "display":display_name
    })



# creating dropdown lists for muscle groups and exercises seperately
muscle_group_options = [None] + list(muscle_to_exercises.keys())
options  = [None] + list(exercises_dict.keys())


with center:
    col1, col2 = st.columns([2,2])

    with col1:
        # creating muscle_group dropdown UI
        selected_muscle = st.selectbox("Select Muscle Group",muscle_group_options,format_func= lambda x: "Select Muscle Group" if x is None else x,
                               label_visibility="collapsed",key= "muscle_group")
        
        # creating a filter based on muscle group selected 
        if selected_muscle:
            filtered_exercises = muscle_to_exercises[selected_muscle]
            
        else:
            filtered_exercises=[]
    exercise_options = [None] + filtered_exercises
    with col2:
        
        # creating exercise dropdown UI
        selected_exercise = st.selectbox("Select Exercise",exercise_options, format_func= lambda x: "Select an exercise" if x is None else x['display']
                                    ,label_visibility="collapsed",key="select_exercise")
        derived_exercise_id = selected_exercise["id"] if selected_exercise else None
        

with center:
    if st.button("Add Exercise"):
        workout_session_id = st.session_state.get("workout_session_id")
        if workout_session_id is None:
            st.warning("No active workout session")
            st.stop()
        else:
            # adding a warning
            if selected_exercise is None:
                st.warning("Please select an exercise")
                st.stop()
            else:
                exercise_id = derived_exercise_id


        

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

    #if workout_exercises_id is None:
        #st.error("Please add an exercise first")
        #st.stop()
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
            st.session_state["reset_inputs"] = True
            st.stop()
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
        finish_button = st.button("🏁 Finish Workout", use_container_width=True,disabled=not st.session_state.get("workout_session_id"))

    # now if the button is clicked, user must see a warning prompt before closing the session

    if finish_button:
        st.session_state["confirm_finish_workout"] = True

    if st.session_state.get("confirm_finish_workout"):

        # check for added sets before finishing the workout
        from db import get_total_sets_per_workout_session
        total_sets = get_total_sets_per_workout_session(workout_session_id)

        if total_sets == 0:
            st.warning("⚠️ No sets added.")
            st.session_state["show_discard_options"] = True
            
            st.write("show_discard_options:", st.session_state.get("show_discard_options"))
            if st.session_state.get("show_discard_options"):
            # give user a choice here to add set or discard the workout
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("➕ Add Set Instead"):
                        st.write("continue adding sets")
                        st.rerun()
                with col2:

                    if st.button("Discard Workout Instead"):
                        st.write("Button CLICKED!!!")
                        st.write("imported function from db")
                        from db import discard_workout
                        
                        workout_session_id = st.session_state.get("workout_session_id")
                        
                        # if user clicks the "discard button" twice, set a flag first

                        if st.session_state.get("workout_session_id"):
                            discard_workout(workout_session_id)


                            st.session_state["message_for_discarded_workout"] = "Workout session discarded!"
                            keys_to_clear = [
                                                "workout_session_id",
                                                "workout_exercises_id",
                                                "set_number"
                                            ]

                            for key in keys_to_clear:
                                st.session_state.pop(key, None)

                            # Now trigger reset
                            st.session_state["reset_form"] = True
                            st.rerun()
                        else:
                            st.error("No active workout sessions")
                            st.session_state["reset_form"] = True
                            st.rerun()

        if total_sets > 0 :
            # prompt warning message
            st.warning("Are you sure you want to finish the workout?")

            col1,col2 = st.columns(2)


            with col1:
                if st.button("✅ Yes, Finish"):
                    #CLEAR STATE
                    keys_to_clear = [
                        "workout_session_id",
                        "workout_exercises_id",
                        "set_number",
                        "start_time"
                    ]

                    # here i update my "workout_sessions" table and input the "duration" & "end_time" of workout
                    workout_session_id = st.session_state.get("workout_session_id")
                    start_time = st.session_state.get("start_time")

                    end_time = datetime.now()

                    duration_minutes = int((end_time - start_time).total_seconds() // 60)
                    from db import update_workout_sessions
                    update_workout_sessions(end_time,duration_minutes,workout_session_id)


                    for key in keys_to_clear:
                        st.session_state.pop(key,None)
                    
                    # Trigger reset instead of direct clearing
                    st.session_state["reset_form"] = True

                    
                    
                    # after resetting keys again set the confirm_finish_session state to False
                    st.session_state["confirm_finish_workout"] = False
                    st.session_state["workout_finished"] = True
                    st.rerun()


            with col2:
                if st.button("❌ No, Cancel"):
                    st.session_state["confirm_finish_workout"] = False
                    st.rerun()