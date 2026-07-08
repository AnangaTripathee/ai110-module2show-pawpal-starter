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
col4, col5 = st.columns(2)
with col4:
    task_type_name = st.selectbox(
        "Task type",
        type_options,
        index=type_options.index(guess_task_type(task_title).name),
    )
with col5:
    scheduled_time = st.time_input("Scheduled time (today)", value=time(8, 0))

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
        recurrence=Recurrence.NONE,
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
st.caption("This calls the Scheduler on the owner's data and orders today's tasks by priority.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    todays_ids = {t.task_id for t in scheduler.get_todays_tasks()}
    # sort_by_priority() orders every task (1 = highest); keep only today's.
    plan = [t for t in scheduler.sort_by_priority() if t.task_id in todays_ids]

    if not plan:
        st.info("No tasks scheduled for today. Add some tasks above, then try again.")
    else:
        st.success(f"Planned {len(plan)} task(s) for today, highest priority first:")
        st.table(
            [
                {
                    "order": i,
                    "type": t.task_type.value,
                    "time": t.scheduled_time.strftime("%H:%M"),
                    "duration (min)": t.duration_minutes,
                    "priority": t.priority,
                }
                for i, t in enumerate(plan, start=1)
            ]
        )
        st.markdown("**Why this order:** tasks are ranked by priority (1 = highest), "
                    "so the most important care happens first.")
