import streamlit as st

from datetime import date, datetime, time

from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Recurrence

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Helpers to bridge the UI inputs to the backend model ------------------

# UI priority labels -> Task.priority ints (1 = highest priority).
PRIORITY_MAP = {"high": 1, "medium": 2, "low": 3}

# Keyword hints used to guess a sensible TaskType from a free-text title.
TASK_TYPE_KEYWORDS = {
    "walk": TaskType.WALK,
    "feed": TaskType.FEEDING,
    "food": TaskType.FEEDING,
    "meal": TaskType.FEEDING,
    "med": TaskType.MEDICATION,
    "pill": TaskType.MEDICATION,
    "vet": TaskType.APPOINTMENT,
    "appointment": TaskType.APPOINTMENT,
}


def guess_task_type(title: str) -> TaskType:
    """Pick a reasonable default TaskType from the task title's wording."""
    lowered = title.lower()
    for keyword, task_type in TASK_TYPE_KEYWORDS.items():
        if keyword in lowered:
            return task_type
    return TaskType.FEEDING


st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Persist a single Owner across reruns: create once, then reuse it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_id=1,
        name=owner_name,
        email=f"{owner_name.lower().replace(' ', '.')}@example.com",
    )
owner = st.session_state.owner

# Monotonic task id counter so every Task gets a unique id.
if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 1

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed into your scheduler as real Task objects.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

type_options = [t.name for t in TaskType]
recurrence_options = [r.name for r in Recurrence]
col4, col5, col6 = st.columns(3)
with col4:
    task_type_name = st.selectbox(
        "Task type",
        type_options,
        index=type_options.index(guess_task_type(task_title).name),
    )
with col5:
    scheduled_time = st.time_input("Scheduled time (today)", value=time(8, 0))
with col6:
    recurrence_name = st.selectbox("Recurrence", recurrence_options, index=0)

if st.button("Add task"):
    # Lazily create the Pet the first time a task is added, and persist it.
    if "pet" not in st.session_state:
        pet = Pet(
            pet_id=1,
            name=pet_name,
            species=species,
            breed="",
            birthdate=date.today(),
            medical_notes="",
        )
        owner.add_pet(pet)
        st.session_state.pet = pet
    pet = st.session_state.pet

    task = Task(
        task_id=st.session_state.next_task_id,
        pet_id=pet.pet_id,
        task_type=TaskType[task_type_name],
        scheduled_time=datetime.combine(date.today(), scheduled_time),
        duration_minutes=int(duration),
        recurrence=Recurrence[recurrence_name],
        priority=PRIORITY_MAP[priority],
        completed=False,
    )
    pet.add_task(task)
    st.session_state.next_task_id += 1

tasks = owner.get_all_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "type": t.task_type.value,
                "time": t.scheduled_time.strftime("%H:%M"),
                "duration (min)": t.duration_minutes,
                "priority": t.priority,
                "recurrence": t.recurrence.value,
                "done": t.completed,
            }
            for t in tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This calls the Scheduler on the owner's data to order, filter, and check today's tasks.")

# Clicking "Generate schedule" latches a flag in session state so the schedule
# (and its per-row action buttons) stay visible across the reruns that
# Streamlit triggers when those buttons are pressed.
if st.button("Generate schedule"):
    st.session_state.schedule_generated = True

if st.session_state.get("schedule_generated"):
    scheduler = Scheduler(owner)
    pet_names = {pet.pet_id: pet.name for pet in owner.get_pets()}

    # --- Controls: sort mode + filters -----------------------------------
    ctrl1, ctrl2 = st.columns(2)
    with ctrl1:
        sort_mode = st.radio("Sort by:", ["Priority", "Time"], horizontal=True)
    with ctrl2:
        pets = owner.get_pets()
        pet_choices = ["All pets"] + [f"{p.name} (#{p.pet_id})" for p in pets]
        selected_pet = st.selectbox("Filter by pet", pet_choices)
    only_incomplete = st.checkbox("Show only incomplete tasks")

    # Map the pet selection back to a pet_id (None = all pets).
    if selected_pet == "All pets":
        filter_pet_id = None
    else:
        filter_pet_id = pets[pet_choices.index(selected_pet) - 1].pet_id
    filter_completed = False if only_incomplete else None

    # --- Conflict detection (runs on every schedule generation) ----------
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for first, second in conflicts:
            first_pet = pet_names.get(first.pet_id, "Unknown")
            second_pet = pet_names.get(second.pet_id, "Unknown")
            st.warning(
                f"⚠️ Conflict: {first.task_type.value} ({first_pet}) at "
                f"{first.scheduled_time.strftime('%H:%M')} overlaps with "
                f"{second.task_type.value} ({second_pet}) at "
                f"{second.scheduled_time.strftime('%H:%M')}"
            )
    else:
        st.success("No conflicts found.")

    # --- Build the ordered, filtered plan for today ----------------------
    todays_ids = {t.task_id for t in scheduler.get_todays_tasks()}
    filtered_ids = {
        t.task_id
        for t in scheduler.filter_tasks(
            pet_id=filter_pet_id, completed=filter_completed
        )
    }
    # sort_by_time()/sort_by_priority() order every task; keep only the ones
    # that are both scheduled for today and pass the active filters.
    ordered_all = (
        scheduler.sort_by_time()
        if sort_mode == "Time"
        else scheduler.sort_by_priority()
    )
    plan = [
        t
        for t in ordered_all
        if t.task_id in todays_ids and t.task_id in filtered_ids
    ]

    if not plan:
        st.info("No tasks match the current filters for today.")
    else:
        st.success(f"Showing {len(plan)} task(s) for today, sorted by {sort_mode.lower()}:")
        st.dataframe(
            [
                {
                    "order": i,
                    "type": t.task_type.value,
                    "pet": pet_names.get(t.pet_id, "Unknown"),
                    "time": t.scheduled_time.strftime("%H:%M"),
                    "duration (min)": t.duration_minutes,
                    "priority": t.priority,
                    "recurrence": t.recurrence.value,
                    "done": t.completed,
                }
                for i, t in enumerate(plan, start=1)
            ],
            hide_index=True,
        )
        if sort_mode == "Priority":
            st.markdown("**Why this order:** tasks are ranked by priority (1 = highest), "
                        "so the most important care happens first.")
        else:
            st.markdown("**Why this order:** tasks are ordered by scheduled time, "
                        "earliest first.")

        # --- Complete recurring tasks (spawns the next occurrence) --------
        recurring_todo = [
            t
            for t in plan
            if t.recurrence is not Recurrence.NONE and not t.completed
        ]
        if recurring_todo:
            st.markdown("#### Complete a recurring task")
            st.caption(
                "Completing a recurring task marks it done and auto-generates "
                "its next occurrence."
            )
            for t in recurring_todo:
                label = (
                    f"✅ Complete {t.task_type.value} "
                    f"({pet_names.get(t.pet_id, 'Unknown')}) at "
                    f"{t.scheduled_time.strftime('%H:%M')} — {t.recurrence.value}"
                )
                if st.button(label, key=f"complete_{t.task_id}"):
                    new_task = scheduler.complete_task(t)
                    # Keep the app's id counter ahead of any id the scheduler
                    # generated, so manually added tasks won't collide.
                    st.session_state.next_task_id = (
                        max(x.task_id for x in owner.get_all_tasks()) + 1
                    )
                    st.success(
                        f"Marked {t.task_type.value} done; generated next "
                        f"occurrence for "
                        f"{new_task.scheduled_time.strftime('%Y-%m-%d %H:%M')}."
                    )
                    st.rerun()
