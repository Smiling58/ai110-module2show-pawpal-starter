import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Step 1: Owner setup (one-time; warn if re-saving would reset data)
# ---------------------------------------------------------------------------
st.subheader("Step 1 — Owner Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_minutes = st.number_input(
        "Time available today (min)", min_value=10, max_value=480, value=90
    )

if st.button("Save owner"):
    if st.session_state.owner is not None:
        # Preserve existing pets — only update name/time
        st.session_state.owner.name = owner_name
        st.session_state.owner.set_available_time(int(available_minutes))
        st.success("Owner info updated. Pets and tasks preserved.")
    else:
        st.session_state.owner = Owner(
            name=owner_name, available_minutes=int(available_minutes)
        )
        st.success(f"Owner '{owner_name}' created.")

# ---------------------------------------------------------------------------
# Step 2: Add pets — calls Owner.add_pet()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Step 2 — Add a Pet")

if st.session_state.owner is None:
    st.info("Save an owner first.")
else:
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col2:
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
        health_notes = st.text_input("Health notes (optional)", value="")

    if st.button("Add pet"):
        new_pet = Pet(
            name=pet_name, species=species, age=int(pet_age), health_notes=health_notes
        )
        # → Owner.add_pet() appends to owner.pets list
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added pet '{pet_name}' to {st.session_state.owner.name}'s profile.")

    if st.session_state.owner.pets:
        st.markdown("**Registered pets:**")
        for p in st.session_state.owner.pets:
            note = f" — {p.health_notes}" if p.health_notes else ""
            st.markdown(f"- **{p.name}** ({p.species}, age {p.age}){note}")

# ---------------------------------------------------------------------------
# Step 3: Add tasks to a selected pet — calls Pet.add_task()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Step 3 — Add Tasks")

if not st.session_state.owner or not st.session_state.owner.pets:
    st.info("Add at least one pet before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Add task to pet", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        preferred_time = st.selectbox(
            "Preferred time", ["morning", "afternoon", "evening", "any"], index=3
        )
    with col5:
        is_mandatory = st.checkbox("Mandatory (always schedule)")

    if st.button("Add task"):
        task = Task(
            title=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority,
            is_mandatory=is_mandatory,
            preferred_time_of_day=preferred_time,
        )
        # → Pet.add_task() appends to pet.tasks list
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # Show all tasks across all pets
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.markdown("**All tasks:**")
        st.table([
            {
                "Pet": next(p.name for p in st.session_state.owner.pets if task in p.tasks),
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Mandatory": task.is_mandatory,
                "Time of day": task.preferred_time_of_day,
            }
            for task in all_tasks
        ])
    else:
        st.info("No tasks yet.")

# ---------------------------------------------------------------------------
# Step 4: Generate schedule — calls Scheduler.generate_plan()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Step 4 — Generate Schedule")

if not st.session_state.owner or not st.session_state.owner.get_all_tasks():
    st.info("Add tasks before generating a schedule.")
else:
    if st.button("Generate schedule"):
        # → Scheduler.generate_plan() → DailyPlan
        scheduler = Scheduler(owner=st.session_state.owner)
        plan = scheduler.generate_plan()

        st.success(
            f"Schedule for **{st.session_state.owner.name}** "
            f"— {plan.total_time()} / {st.session_state.owner.available_minutes} min used"
        )

        if plan.scheduled_tasks:
            st.markdown("**Scheduled:**")
            for t in plan.scheduled_tasks:
                tag = " *(mandatory)*" if t.is_mandatory else ""
                st.markdown(
                    f"- **{t.title}** — {t.duration_minutes} min, "
                    f"{t.priority} priority, {t.preferred_time_of_day}{tag}"
                )

        if plan.skipped_tasks:
            st.markdown("**Skipped (not enough time):**")
            for t in plan.skipped_tasks:
                st.markdown(f"- {t.title} — {t.duration_minutes} min")

        with st.expander("See reasoning"):
            st.text(plan.explain())
