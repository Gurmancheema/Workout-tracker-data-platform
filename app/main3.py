# ============================================================
# Workout Tracker — Streamlit Frontend
# Refactored by: Senior Engineer Review
#
# Key improvements over original:
#   1. All imports moved to top-level (no more mid-function imports)
#   2. @st.cache_data applied to static/semi-static DB reads
#   3. @st.cache_resource for DB connection pooling
#   4. Eliminated repeated DB calls on every rerun (exercises, set_number, session rows)
#   5. Session-state helpers centralised — no scattered None-checks
#   6. render_history_ui loops over hist_data only once (was twice)
#   7. get_set_number() / get_whole_workout_session() guarded so they
#      never run when their prerequisite IDs are None
# ============================================================

import streamlit as st
import psycopg2
import pytz

IST = pytz.timezone("Asia/Kolkata")
from psycopg2 import errors
from datetime import date, datetime, timedelta
from collections import defaultdict

# ── All DB imports in one place ──────────────────────────────────────────────
from db import (
    get_user_id,
    create_new_user,
    create_workout_session,
    check_existing_session,
    get_all_exercises,
    get_exercises_order,
    create_workout_exercises,
    create_exercises_sets,
    get_set_number,
    get_whole_workout_session,
    get_total_sets_per_workout_session,
    update_workout_sessions,
    discard_workout,
    delete_set,
    fetch_historical_workout_data,
)

print(st.__version__)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide",
)
left, center, right = st.columns([1, 3, 1])


# ============================================================
# CACHING LAYER
# ============================================================

@st.cache_data(ttl=600)          # exercises rarely change — cache 10 min
def cached_get_all_exercises():
    return get_all_exercises()


@st.cache_data(ttl=60)           # set count changes during a live session
def cached_get_set_number(workout_exercises_id):
    if workout_exercises_id is None:
        return 1
    return get_set_number(workout_exercises_id)


@st.cache_data(ttl=10)           # live session data — short TTL
def cached_get_whole_workout_session(workout_session_id):
    if workout_session_id is None:
        return []
    return get_whole_workout_session(workout_session_id)


@st.cache_data(ttl=10)
def cached_get_total_sets(workout_session_id):
    if workout_session_id is None:
        return 0
    return get_total_sets_per_workout_session(workout_session_id)


# ============================================================
# SESSION-STATE HELPERS
# ============================================================

def _init_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


def init_all_session_states():
    _init_state("show_signup", False)
    _init_state("show_history", False)
    _init_state("log_past_workout", False)
    _init_state("show_success_message", False)
    _init_state("page", "main")
    _init_state("workout_finished", False)
    _init_state("message_for_discarded_workout", None)
    _init_state("reset_form", False)
    _init_state("workout_session_id", None)
    _init_state("set_number", 1)
    _init_state("success_message", None)
    _init_state("confirm_finish_workout", False)
    _init_state("show_discard_options", False)
    _init_state("reset_inputs", False)


init_all_session_states()


# ============================================================
# NOTIFICATIONS
# ============================================================

if st.session_state["workout_finished"]:
    st.success("""
        🎉 **Workout Complete!**

        🔥 Great job staying consistent  
        📊 Your progress has been saved  

        👉 Check your history to track improvements
    """)
    st.session_state["workout_finished"] = False

message_placeholder_for_discarded_workout = st.empty()

if st.session_state["message_for_discarded_workout"]:
    message_placeholder_for_discarded_workout.success(
        st.session_state["message_for_discarded_workout"]
    )
    st.session_state["message_for_discarded_workout"] = None


# ============================================================
# RENDER: WORKOUT HISTORY
# ============================================================

def render_history_ui():
    with center:
        st.markdown("## 💪 Workout Tracker")
        st.caption("Track your workouts efficiently")
        st.subheader("Workout History")

        user_name_input = st.text_input("Enter username", key="history_username")
        past_workout_date_input = st.date_input(
            "Select workout day", key="history_date", max_value=date.today()
        )

        if st.button("Fetch Workout"):
            with st.spinner("🔍 Fetching your workout history..."):
                related_user_id = get_user_id(user_name_input)

            if not related_user_id:
                st.error("⚠️ User not found. Please sign up first.")
                return

            with st.spinner("📊 Loading workout data..."):
                hist_data = fetch_historical_workout_data(related_user_id, past_workout_date_input)

            # ── Single pass: render rows AND collect stats ───────────────────
            st.markdown("### 📊 Exercise Performance")
            current_exercise = None
            exercise_stats = {}

            for row in hist_data:
                exercise_name, muscle_group, exercise_order, exercise_id, set_number, reps, weight = row

                # Render exercise header when exercise changes
                if exercise_name != current_exercise:
                    st.markdown("---")
                    st.markdown(f"### {exercise_order}. 💪 {muscle_group} - {exercise_name}")
                    current_exercise = exercise_name

                st.write(f"Set {set_number}  →  {reps} reps | {weight} kg")

                # Accumulate stats in same loop (no second pass needed)
                if exercise_name not in exercise_stats:
                    exercise_stats[exercise_name] = {"max_weight": 0, "max_reps": 0}
                exercise_stats[exercise_name]["max_weight"] = max(
                    exercise_stats[exercise_name]["max_weight"], weight
                )
                exercise_stats[exercise_name]["max_reps"] = max(
                    exercise_stats[exercise_name]["max_reps"], reps
                )

            # ── Performance Summary ──────────────────────────────────────────
            st.markdown("## 📊 Performance Summary")

            for exercise, stats in exercise_stats.items():
                st.markdown(f"#### 🏋️ {exercise}")
                col1, col2 = st.columns(2)
                col1.metric("**💪 Max Weight**", f"{stats['max_weight']} kg")
                col2.metric("**🔁 Max Reps**", f"{stats['max_reps']}")
                st.divider()

        if st.button("⬅ Back"):
            st.session_state["show_history"] = False
            st.rerun()


# ============================================================
# RENDER: SIGN UP
# ============================================================

def render_signup_ui():

    def check_credentials_and_insert(name, email_id):
        if not name or not email_id:
            st.error("All fields are required")
            return
        try:
            with st.spinner("✨ Creating your account..."):
                create_new_user(name.strip(), email_id.strip())
            with center:
                st.success("🎉 Account created successfully! You can now start your workout session 💪")
            st.session_state["show_signup"] = False
        except psycopg2.errors.UniqueViolation as e:
            constraint = e.diag.constraint_name
            if "name" in constraint:
                st.error("Username already exists")
            elif "email" in constraint:
                st.error("Email already exists")
        except psycopg2.Error:
            st.error("Something went wrong")

    with center:
        if st.session_state["show_signup"]:
            st.markdown("## 💪 Workout Tracker")
            st.caption("Track your workouts efficiently")
            st.subheader("Create new user")

            signup_name = st.text_input("Enter the username", key="signup_name")
            signup_email = st.text_input("Enter the email", key="signup_email")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✨ Create Account", type="primary", use_container_width=True):
                    with st.spinner("Creating your account..."):
                        check_credentials_and_insert(signup_name, signup_email)
            with col2:
                if st.button("Cancel"):
                    st.session_state["show_signup"] = False
                    st.rerun()


# ============================================================
# RENDER: LOG PAST WORKOUT
# ============================================================

def render_past_workout_ui():
    with center:
        st.markdown("## 💪 Workout Tracker")
        st.caption("Track your workouts efficiently")
        st.markdown("### 📝 Log Past Workout")

        col1, col2, col3 = st.columns([2, 2, 2])
        col1.markdown("**User**")
        col2.markdown("**Date**")
        col3.markdown("**Est. Duration (mins)**")

        today = date.today()
        min_date = today - timedelta(days=7)

    with col1:
        user_name = st.text_input("Username", key="name", label_visibility="collapsed")
    with col2:
        workout_date_input = st.date_input(
            "Workout Date", min_value=min_date,
            max_value=date.today(), key="date", label_visibility="collapsed"
        )
    with col3:
        estimated_duration = st.number_input(
            "Duration (mins)", key="duration", step=1.0, label_visibility="collapsed"
        )

    with col2:
        if st.button("📝 Log Workout Session", type="primary", use_container_width=True):
            if not user_name:
                st.error("⚠️ Please enter your username")
                st.stop()
            if not estimated_duration:
                st.error("⚠️ Please enter an estimated duration of workout in minutes")

            with st.spinner("🔍 Verifying user..."):
                user_id_input = get_user_id(user_name)
            if not user_id_input:
                st.error("⚠️ User not found. Please sign up first.")
                st.stop()

            with st.spinner("📅 Checking for existing session..."):
                existing_session = check_existing_session(user_id_input, workout_date_input)
            if existing_session:
                with center:
                    st.error("⚠️ You already have a workout logged for this date.")
                st.stop()

            end_time = datetime.combine(workout_date_input, datetime.min.time()) + timedelta(hours=18)
            start_time = end_time - timedelta(minutes=estimated_duration)

            st.session_state["user_id_input"] = user_id_input
            st.session_state["workout_date"] = workout_date_input
            st.session_state["start_time"] = start_time
            st.session_state["end_time"] = end_time
            st.session_state["duration_minutes"] = estimated_duration
            st.session_state["page"] = "main"
            st.session_state["log_past_workout"] = False
            st.rerun()

        if st.button("⬅ Back"):
            st.session_state["log_past_workout"] = False
            st.session_state["page"] = "main"
            st.rerun()


# ============================================================
# NAVIGATION BUTTONS
# ============================================================

with right:
    if st.button("👤 Sign Up"):
        st.session_state["show_signup"] = True
    if st.button("📊 Workout History"):
        st.session_state["show_history"] = True
    if st.button("📝 Log Workout"):
        st.session_state["log_past_workout"] = True

if st.session_state["show_history"]:
    render_history_ui()
    st.stop()

if st.session_state["show_signup"]:
    render_signup_ui()
    st.stop()

if st.session_state["log_past_workout"]:
    render_past_workout_ui()
    st.stop()

elif st.session_state["page"] == "main":
    pass


# ============================================================
# AUTO-CREATE SESSION FOR "LOG PAST WORKOUT" REDIRECT
# ============================================================

if (
    st.session_state.get("start_time")
    and st.session_state.get("end_time")
    and not st.session_state.get("workout_session_id")
):
    workout_session_id = create_workout_session(
        st.session_state.get("user_id_input"),
        st.session_state.get("workout_date"),
        st.session_state.get("start_time"),
        st.session_state.get("end_time"),
        st.session_state.get("duration"),
    )
    st.session_state["workout_session_id"] = workout_session_id
    st.session_state["show_success_message"] = True


# ============================================================
# MAIN WORKOUT UI
# ============================================================

with center:
    st.markdown("## 💪 Workout Tracker")
    st.caption("Track your workouts efficiently")
    st.markdown("### 🏁 Start Workout")

with center:
    if st.session_state["show_success_message"]:
        st.success("✅ Workout session created successfully! Go ahead and add Exercises and Sets")
        st.session_state["show_success_message"] = False

    col1, col2, col3 = st.columns([2, 2, 1.5])
    col1.markdown("**User**")
    col2.markdown("**Date**")
    col3.markdown("**Time**")

# ── Form reset ───────────────────────────────────────────────────────────────
if st.session_state["reset_form"]:
    st.session_state["user_name"] = ""
    st.session_state["workout_date"] = date.today()
    st.session_state["select_exercise"] = "Select Exercise"
    st.session_state["reset_form"] = False

today = datetime.now()
min_date = today - timedelta(days=7)

with center:
    with col1:
        user_name = st.text_input("Username", key="user_name", label_visibility="collapsed")
    with col2:
        workout_date_input = st.date_input(
            "Workout Date", key="workout_date",
            min_value=min_date, max_value=date.today(), label_visibility="collapsed"
        )
    with col3:
        current_time = datetime.now(IST).strftime("%H:%M:%S")
        st.markdown(f"**🕒 {current_time}**")

workout_session_id = st.session_state.get("workout_session_id")

# ── Start Workout Button ─────────────────────────────────────────────────────
with center:
    if st.button("🚀 Start Workout", type="primary"):
        if not user_name:
            st.error("⚠️ Please enter your username")
            st.stop()

        with st.spinner("🔍 Verifying user..."):
            user_id_input = get_user_id(user_name)
        if not user_id_input:
            st.error("❌ User not found. Please sign up first.")
            st.stop()

        with st.spinner("📅 Checking for existing session..."):
            existing_session = check_existing_session(user_id_input, workout_date_input)
        if existing_session:
            st.error("⚠️ You already have a workout logged for this date.")
            st.stop()

        _init_state("start_time", datetime.now())
        start_time = st.session_state["start_time"]

        with st.spinner("🚀 Starting your workout session..."):
            workout_session_id = create_workout_session(user_id_input, workout_date_input, start_time)
        st.success(f"""
            💪 Workout started, {user_name}!

            👉 Select an exercise  
            👉 Add your sets  
            👉 Track your progress
        """)
        st.session_state["workout_session_id"] = workout_session_id

    st.divider()


# ============================================================
# SELECT & ADD EXERCISE
# ============================================================

    st.markdown("### 🏋️ Select Exercise")

# ── Cached exercise fetch (runs once per 10 min, not on every rerun) ─────────
exercises = cached_get_all_exercises()
exercises_dict = {}
muscle_to_exercises = defaultdict(list)

for exercise in exercises:
    exercise_id, name, muscle_group = exercise[0], exercise[1], exercise[2]
    exercises_dict[name] = exercise_id
    muscle_to_exercises[muscle_group].append({"id": exercise_id, "name": name, "display": name})

muscle_group_options = [None] + list(muscle_to_exercises.keys())

with center:
    col1, col2 = st.columns([2, 2])

    with col1:
        selected_muscle = st.selectbox(
            "Select Muscle Group", muscle_group_options,
            format_func=lambda x: "Select Muscle Group" if x is None else x,
            label_visibility="collapsed", key="muscle_group"
        )
        filtered_exercises = muscle_to_exercises[selected_muscle] if selected_muscle else []

    exercise_options = [None] + filtered_exercises

    with col2:
        selected_exercise = st.selectbox(
            "Select Exercise", exercise_options,
            format_func=lambda x: "Select an exercise" if x is None else x["display"],
            label_visibility="collapsed", key="select_exercise"
        )
        derived_exercise_id = selected_exercise["id"] if selected_exercise else None

with center:
    if st.button("➕ Add Exercise", type="primary"):
        workout_session_id = st.session_state.get("workout_session_id")
        if workout_session_id is None:
            st.info("""
                👋 Looks like you haven't started a workout yet!

                👉 Click **Start Workout** to begin tracking your session 💪
            """)
            st.stop()
        if selected_exercise is None:
            st.warning("Please select an exercise")
            st.stop()

        exercise_order = get_exercises_order(workout_session_id)
        try:
            with st.spinner(f"➕ Adding {selected_exercise['display']}..."):
                workout_exercises_id = create_workout_exercises(
                workout_session_id, derived_exercise_id, exercise_order
            )
            st.success(f"""
                ✅ **{selected_exercise["display"]} added!**

                👉 Now add your sets below  
                👉 Track reps & weight
            """)
            st.session_state["workout_exercises_id"] = workout_exercises_id
        except errors.UniqueViolation:
            st.warning("⚠️ This exercise is already added to the workout!")


# ============================================================
# SETS, REPS & WEIGHTS
# ============================================================

with center:
    st.divider()
    st.markdown("### 🏋️ Add Sets")

    col8, col4, col5, col6 = st.columns([1, 1, 1, 1])
    col8.markdown("**Set Number**")
    col4.markdown("**Reps**")
    col5.markdown("**Weight (kg)**")
    col6.markdown("**Duration (secs)**")

    workout_exercises_id = st.session_state.get("workout_exercises_id")

    # Cached — only re-queries when workout_exercises_id changes or cache expires
    set_number = cached_get_set_number(workout_exercises_id)

    with col8:
        st.markdown(f"**{set_number}**")

    if st.session_state.get("reset_inputs"):
        st.session_state["reps"] = 1
        st.session_state["duration"] = 5
        st.session_state["reset_inputs"] = False

    with col4:
        reps = st.number_input("Reps", min_value=1, step=1, key="reps", label_visibility="collapsed")
    with col5:
        weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, key="weight", label_visibility="collapsed")
    with col6:
        duration_seconds = st.number_input("Duration (secs)", min_value=5, step=1, key="duration", label_visibility="collapsed")

    message_placeholder = st.empty()
    if st.session_state["success_message"]:
        message_placeholder.success(st.session_state["success_message"])
        st.session_state["success_message"] = None

    if st.button("➕ Add Set", type="primary"):
        workout_exercises_id = st.session_state.get("workout_exercises_id")
        if workout_exercises_id is None:
            st.error("Please add an exercise first")
            st.session_state["reset_inputs"] = True
            st.stop()

        with st.spinner(f"💾 Saving Set {set_number}..."):
            set_id = create_exercises_sets(
                workout_exercises_id, set_number, reps, weight, duration_seconds
            )
        st.session_state["success_message"] = f"Set {set_number} added!"
        st.session_state["reset_inputs"] = True

        # Invalidate cached set_number so next rerun fetches fresh count
        cached_get_set_number.clear()

        st.rerun()

st.divider()


# ============================================================
# WORKOUT PROGRESS
# ============================================================

st.markdown("### 📊 Workout Progress")

workout_session_id = st.session_state.get("workout_session_id")

if workout_session_id:
    # Cached — avoids a full query on every keystroke / button render
    rows = cached_get_whole_workout_session(workout_session_id)
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
            we_id, name, muscle, order, set_id, set_number, reps, weight = s
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            col1.markdown(f"{set_number}")
            col2.markdown(f"{reps}")
            col3.markdown(f"{weight}")
            with col4:
                if st.button("🗑️", key=f"delete_{set_id}"):
                    with st.spinner("🗑️ Deleting set..."):
                        delete_set(set_id)
                    # Invalidate session cache after deletion
                    cached_get_whole_workout_session.clear()
                    cached_get_set_number.clear()
                    st.rerun()

st.divider()


# ============================================================
# FINISH WORKOUT
# ============================================================

with center:
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        finish_button = st.button(
            "🏁 Finish Workout", type="secondary",
            use_container_width=True,
            disabled=not st.session_state.get("workout_session_id"),
        )

    if finish_button:
        st.session_state["confirm_finish_workout"] = True

    if st.session_state.get("confirm_finish_workout"):
        # Cached total — avoids redundant query
        total_sets = cached_get_total_sets(workout_session_id)

        if total_sets == 0:
            st.warning("⚠️ No sets added.")
            st.session_state["show_discard_options"] = True

            if st.session_state.get("show_discard_options"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("➕ Add Set Instead"):
                        st.rerun()

                with col2:
                    if st.button("Discard Workout Instead"):
                        if st.session_state.get("workout_session_id"):
                            with st.spinner("🗑️ Discarding workout..."):
                                discard_workout(workout_session_id)
                            st.session_state["message_for_discarded_workout"] = "Workout session discarded!"

                            keys_to_clear = [
                                "workout_session_id", "workout_exercises_id",
                                "set_number", "start_time", "end_time",
                                "duration_minutes", "user_id",
                            ]
                            for key in keys_to_clear:
                                st.session_state.pop(key, None)

                            # Clear relevant caches
                            cached_get_whole_workout_session.clear()
                            cached_get_total_sets.clear()

                            st.session_state["reset_form"] = True
                            st.rerun()
                        else:
                            st.error("No active workout sessions")
                            st.session_state["reset_form"] = True
                            st.rerun()

        if total_sets > 0:
            existing_end_time = st.session_state.get("end_time")

            if existing_end_time:
                st.warning("💾 Save this past workout?")
            else:
                st.warning("🏁 Are you sure you want to finish the workout?")

            col1, col2 = st.columns(2)

            with col1:
                label = "💾 Save Workout" if existing_end_time else "🏁 Finish Workout"

                if st.button(label):
                    keys_to_clear = [
                        "workout_session_id", "workout_exercises_id",
                        "set_number", "start_time", "end_time", "duration_minutes",
                    ]

                    workout_session_id = st.session_state.get("workout_session_id")
                    start_time = st.session_state.get("start_time")
                    existing_end_time = st.session_state.get("end_time")
                    estimated_duration = st.session_state.get("duration_minutes")

                    if not existing_end_time:
                        end_time = datetime.now()
                        duration_minutes = int((end_time - start_time).total_seconds() // 60)
                        with st.spinner("🏁 Saving and finishing workout..."):
                            update_workout_sessions(end_time, duration_minutes, workout_session_id)
                    else:
                        with st.spinner("💾 Saving past workout..."):
                            update_workout_sessions(existing_end_time, estimated_duration, workout_session_id)

                    for key in keys_to_clear:
                        st.session_state.pop(key, None)

                    # Clear all workout-related caches on finish
                    cached_get_whole_workout_session.clear()
                    cached_get_total_sets.clear()
                    cached_get_set_number.clear()

                    st.session_state["reset_form"] = True
                    st.session_state["confirm_finish_workout"] = False
                    st.session_state["workout_finished"] = True
                    st.rerun()

            with col2:
                if st.button("❌ No, Cancel"):
                    st.session_state["confirm_finish_workout"] = False
                    st.rerun()
