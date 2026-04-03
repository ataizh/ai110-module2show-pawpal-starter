import json
import os
import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

DATA_FILE = "data.json"

# --- Helpers ---

def save_data():
    """Challenge 2: Persist owner data to data.json."""
    if st.session_state.owner:
        st.session_state.owner.save_to_json(DATA_FILE)

def load_data():
    """Challenge 2: Load owner data from data.json if it exists."""
    if os.path.exists(DATA_FILE):
        try:
            owner = Owner.load_from_json(DATA_FILE)
            st.session_state.owner = owner
            st.session_state.caretaker = Scheduler(owner)
        except (json.JSONDecodeError, KeyError):
            pass  # corrupt file — start fresh

# --- Session State Setup ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "caretaker" not in st.session_state:
    st.session_state.caretaker = None
if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

# --- Header ---
st.title("🐾 PawPal+")
st.caption("A smart pet care planner for busy pet parents.")

# --- Step 1: Owner Setup ---
st.header("1. Who are you?")

with st.form("owner_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First name",
            value=st.session_state.owner.first_name if st.session_state.owner else "Jordan")
    with col2:
        last_name = st.text_input("Last name",
            value=st.session_state.owner.last_name if st.session_state.owner else "Lee")
    phone = st.text_input("Phone (optional)",
        value=st.session_state.owner.phone if st.session_state.owner else "")
    email = st.text_input("Email (optional)",
        value=st.session_state.owner.email if st.session_state.owner else "")
    submitted = st.form_submit_button("Save Owner")

if submitted:
    if st.session_state.owner is None:
        st.session_state.owner = Owner(first_name=first_name, last_name=last_name,
                                         phone=phone, email=email)
        st.session_state.caretaker = Scheduler(st.session_state.owner)
    else:
        st.session_state.owner.first_name = first_name
        st.session_state.owner.last_name  = last_name
        st.session_state.owner.phone      = phone
        st.session_state.owner.email      = email
    save_data()
    st.success(f"Welcome, {st.session_state.owner.full_name}! Data saved. 💾")

if st.session_state.owner is None:
    st.info("Fill in your name above to get started.")
    st.stop()

owner: Owner     = st.session_state.owner
caretaker: Scheduler = st.session_state.caretaker

st.divider()

# --- Step 2: Register a Pet ---
st.header("2. Register a Pet")

with st.form("patient_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["Cat", "Dog", "Rabbit", "Bird", "Other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    medical_notes = st.text_area("Medical notes (optional)", value="")
    add_pet = st.form_submit_button("Register Pet")

if add_pet:
    existing_names = [p.name for p in owner.pets]
    if pet_name in existing_names:
        st.warning(f"{pet_name} is already registered.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species,
                                       age=age, medical_notes=medical_notes))
        save_data()
        st.success(f"{pet_name} the {species} has been registered and saved! 💾")

if owner.pets:
    st.write("**Registered pets:**", ", ".join(str(p) for p in owner.pets))

st.divider()

# --- Step 3: Book an Appointment ---
st.header("3. Book an Appointment")

if not owner.pets:
    st.info("Register at least one pet before booking appointments.")
else:
    with st.form("appointment_form"):
        patient_name = st.selectbox("Pet", [p.name for p in owner.pets])
        title        = st.text_input("Appointment title", value="Morning Walk")
        col1, col2   = st.columns(2)
        with col1:
            appt_date = st.date_input("Date", value=date.today())
        with col2:
            appt_time = st.time_input("Time")
        col3, col4, col5 = st.columns(3)
        with col3:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=20)
        with col4:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col5:
            repeat = st.selectbox("Repeat", ["none", "daily", "weekly"])
        book = st.form_submit_button("Book Appointment")

    if book:
        target = next(p for p in owner.pets if p.name == patient_name)
        target.add_task(Task(
            title=title,
            date=appt_date.strftime("%Y-%m-%d"),
            time=appt_time.strftime("%H:%M"),
            duration_minutes=int(duration),
            priority=priority,
            frequency=repeat,
        ))
        save_data()
        st.success(f"Booked '{title}' for {patient_name} at {appt_time.strftime('%H:%M')}! 💾")

    # Challenge 1: Next Available Slot finder
    st.markdown("#### 🔍 Find Next Available Slot")
    col_dur, col_dt, col_btn = st.columns([2, 2, 1])
    with col_dur:
        slot_duration = st.number_input("Task duration (min)", min_value=5, max_value=300,
                                         value=30, key="slot_dur")
    with col_dt:
        slot_date = st.date_input("On date", value=date.today(), key="slot_date")
    with col_btn:
        st.write("")
        st.write("")
        find_slot = st.button("Find Slot")

    if find_slot:
        slot = caretaker.find_next_slot(int(slot_duration), slot_date.strftime("%Y-%m-%d"))
        if slot:
            st.success(f"✅ Next available {slot_duration}-min slot on {slot_date}: **{slot}**")
        else:
            st.error("No available slot found for that day.")

st.divider()

# --- Step 4: Daily Schedule ---
st.header("4. Today's Schedule")

selected_date = st.date_input("View schedule for", value=date.today())
date_str = selected_date.strftime("%Y-%m-%d")

col_sort, col_budget = st.columns(2)
with col_sort:
    sort_mode = st.radio("Sort by", ["Time", "Priority"], horizontal=True)
with col_budget:
    use_budget = st.checkbox("Apply time budget")
    time_budget = st.number_input("Available minutes", min_value=1, max_value=1440,
                                   value=120, disabled=not use_budget)

if st.button("Generate Schedule"):
    if use_budget:
        day = caretaker.what_fits(int(time_budget), date_str)
    else:
        day = caretaker.plan_day(date_str)

    if sort_mode == "Priority" and not use_budget:
        rank = {"high": 0, "medium": 1, "low": 2}
        day = sorted(day, key=lambda x: (rank.get(x[1].priority, 99), x[1].time))

    if not day:
        st.info(f"No appointments scheduled for {date_str}.")
    else:
        # Challenge 3 & 4: color-coded, emoji-rich table
        rows = []
        for patient_name, appt in day:
            rows.append({
                "":         appt.emoji,
                "Time":     appt.time,
                "Pet":      patient_name,
                "Task":     appt.title,
                "Duration": f"{appt.duration_minutes} min",
                "Priority": f"{appt.priority_emoji} {appt.priority}",
                "Repeat":   appt.frequency,
                "Status":   "✅ Done" if appt.completed else "⏳ Pending",
            })
        st.table(rows)

        # Conflict warnings
        conflicts = caretaker.detect_conflicts()
        day_conflicts = [(a1, a2) for a1, a2 in conflicts if a1[1].date == date_str]
        if day_conflicts:
            for (n1, a1), (n2, a2) in day_conflicts:
                st.warning(
                    f"⚠️ **Conflict:** **{n1}** '{a1.title}' and **{n2}** '{a2.title}' "
                    f"are both at **{a1.time}**. Consider rescheduling one."
                )
        else:
            st.success("✅ No scheduling conflicts detected!")

    if use_budget:
        with st.expander("💡 Why was my schedule built this way?"):
            explanation = caretaker.explain_plan(int(time_budget), date_str)
            st.code(explanation, language=None)

st.divider()

# --- Step 5: Mark Appointments Done ---
st.header("5. Mark Appointments as Done")

all_appts = owner.get_all_tasks()
pending   = [(name, appt) for name, appt in all_appts if not appt.completed]

if not pending:
    st.info("No pending appointments.")
else:
    for i, (patient_name, appt) in enumerate(pending):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(
                f"{appt.emoji} {appt.priority_emoji} **{patient_name}** — "
                f"{appt.title} on {appt.date} at {appt.time} ({appt.duration_minutes} min)"
            )
        with col2:
            if st.button("Done ✅", key=f"done_{i}"):
                appt.mark_complete()
                next_appt = appt.next_occurrence()
                if next_appt:
                    target = next(p for p in owner.pets if p.name == patient_name)
                    target.add_task(next_appt)
                    st.success(f"Done! Next '{appt.title}' booked for {next_appt.date}.")
                else:
                    st.success(f"'{appt.title}' marked as done.")
                save_data()
                st.rerun()
