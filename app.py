import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart daily care planner for your pets.")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Step 1: Owner setup
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
        st.session_state.owner.name = owner_name
        st.session_state.owner.set_available_time(int(available_minutes))
        st.success("Owner info updated. Pets and tasks preserved.")
    else:
        st.session_state.owner = Owner(
            name=owner_name, available_minutes=int(available_minutes)
        )
        st.success(f"Owner '{owner_name}' created.")

# ---------------------------------------------------------------------------
# Step 2: Add pets
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
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added pet '{pet_name}' to {st.session_state.owner.name}'s profile.")

    if st.session_state.owner.pets:
        st.markdown("**Registered pets:**")
        for p in st.session_state.owner.pets:
            note = f" — {p.health_notes}" if p.health_notes else ""
            st.markdown(f"- **{p.name}** ({p.species}, age {p.age}){note}")

# ---------------------------------------------------------------------------
# Step 3: Add tasks
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

    col4, col5, col6 = st.columns(3)
    with col4:
        preferred_time = st.selectbox(
            "Preferred time", ["morning", "afternoon", "evening", "any"], index=3
        )
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
    with col6:
        is_mandatory = st.checkbox("Mandatory (always schedule)")

    if st.button("Add task"):
        task = Task(
            title=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority,
            is_mandatory=is_mandatory,
            preferred_time_of_day=preferred_time,
            frequency=frequency,
        )
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

    # --- All tasks table sorted chronologically via Scheduler.sort_by_time() ---
    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        scheduler = Scheduler(st.session_state.owner)
        sorted_tasks = scheduler.sort_by_time(all_tasks)

        st.markdown("**All tasks (sorted by time of day):**")
        st.table([
            {
                "Pet": next(p.name for p in st.session_state.owner.pets if task in p.tasks),
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority,
                "Time of day": task.preferred_time_of_day,
                "Frequency": task.frequency,
                "Mandatory": "✔" if task.is_mandatory else "",
                "Done": "✔" if task.completed else "",
            }
            for task in sorted_tasks
        ])

        # --- Conflict warnings via Scheduler.detect_conflicts() ---
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.markdown("---")
            st.markdown("**⚠️ Scheduling conflicts detected:**")
            for warning in conflicts:
                # Parse out the pet name and slot from the warning string for a friendlier message
                st.warning(
                    f"{warning}\n\n"
                    "Two or more tasks share the same time slot for this pet. "
                    "Consider changing the preferred time of one task, or making one "
                    "task 'any' time so the Scheduler can place it freely."
                )
    else:
        st.info("No tasks yet.")

# ---------------------------------------------------------------------------
# Step 4: Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Step 4 — Generate Schedule")

if not st.session_state.owner or not st.session_state.owner.get_all_tasks():
    st.info("Add tasks before generating a schedule.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler(owner=st.session_state.owner)

        # --- Show conflict warnings before the plan so the owner can act on them ---
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(
                    f"**Time slot conflict** — {warning}  \n"
                    "These tasks are both preferred for the same time of day. "
                    "The Scheduler will still include both if time allows, but "
                    "you may want to adjust the preferred time of one of them."
                )

        plan = scheduler.generate_plan()
        budget = st.session_state.owner.available_minutes
        used = plan.total_time()
        remaining = budget - used

        # --- Budget summary ---
        c1, c2, c3 = st.columns(3)
        c1.metric("Budget (min)", budget)
        c2.metric("Used (min)", used)
        if remaining >= 0:
            c3.metric("Remaining (min)", remaining)
            st.success(
                f"Schedule ready for **{st.session_state.owner.name}** — "
                f"{used} of {budget} min used."
            )
        else:
            c3.metric("Over budget (min)", abs(remaining))
            st.warning(
                f"Mandatory tasks pushed the plan {abs(remaining)} min over your "
                f"{budget}-min budget. All mandatory tasks are still included."
            )

        # --- Scheduled tasks sorted by time-of-day for natural daily reading order ---
        if plan.scheduled_tasks:
            ordered = scheduler.sort_by_time(plan.scheduled_tasks)
            st.markdown("#### Scheduled tasks")
            for t in ordered:
                if t.is_mandatory:
                    label = "🔴 mandatory"
                elif t.priority == "high":
                    label = "🟠 high priority"
                elif t.priority == "medium":
                    label = "🟡 medium priority"
                else:
                    label = "🟢 low priority"
                st.success(
                    f"**{t.title}** — {t.duration_minutes} min | "
                    f"{t.preferred_time_of_day} | {label} | repeats {t.frequency}"
                )

        # --- Skipped tasks ---
        if plan.skipped_tasks:
            st.markdown("#### Skipped tasks (not enough time remaining)")
            for t in plan.skipped_tasks:
                st.error(
                    f"**{t.title}** — {t.duration_minutes} min | "
                    f"{t.priority} priority | not scheduled today"
                )

        # --- Full reasoning ---
        with st.expander("See full scheduling reasoning"):
            st.text(plan.explain())
