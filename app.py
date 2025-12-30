import streamlit as st
import random
from datetime import datetime
import json
from db import (
    create_tables,
    add_diet,
    get_diets,
    add_meal_category,
    get_meal_categories,
    move_meal_category,
    delete_meal_category,
    add_food,
    get_foods_by_category,
    delete_food,
    get_food_categories,
    add_food_category,
    ensure_default_food_categories,
    delete_food_category,
    save_weekly_plan,
    get_weekly_plans,
    delete_weekly_plan,
    update_weekly_plan_name
)

st.set_page_config(
    page_title="Diet Automation MVP",
    page_icon="🥗",
    layout="wide"
)

create_tables()

# Initialize session state for shuffled plan
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None


def generate_weekly_plan(diet_id, meal_categories):
    """Generate a 7-day meal plan"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
            "Sunday"]
    plan = {}

    for day in days:
        plan[day] = {}

        for cat_id, cat_name, _ in meal_categories:
            foods = get_foods_by_category(cat_id)

            if not foods:
                plan[day][cat_name] = []
                continue

            # Separate mandatory and optional foods
            mandatory_foods = [f for f in foods if
                               f[5] == 1]  # f[5] is mandatory
            optional_foods = [f for f in foods if f[5] == 0]

            selected_foods = []

            # Always include mandatory foods
            for food in mandatory_foods:
                selected_foods.append({
                    'name': food[1],
                    'type': food[2],
                    'portion': food[3],
                    'rating': food[4],
                    'mandatory': True
                })

            # Group optional foods by food category type
            foods_by_type = {}
            for food in optional_foods:
                food_type = food[2]  # food[2] is food_type
                if food_type not in foods_by_type:
                    foods_by_type[food_type] = []
                foods_by_type[food_type].append(food)

            # Select at least one food from each food category type
            for food_type, type_foods in foods_by_type.items():
                # Weight by rating: rating^2 for more preference to high ratings
                weights = [f[4] ** 2 for f in type_foods]  # f[4] is rating
                selected = random.choices(type_foods, weights=weights, k=1)[0]

                selected_foods.append({
                    'name': selected[1],
                    'type': selected[2],
                    'portion': selected[3],
                    'rating': selected[4],
                    'mandatory': False
                })

            plan[day][cat_name] = selected_foods

    return plan


def display_weekly_plan(plan):
    """Display the weekly plan in a nice format"""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
            "Sunday"]

    for day in days:
        st.subheader(f"📅 {day}")

        if day in plan:
            cols = st.columns(len(plan[day]))

            for col, (meal_name, foods) in zip(cols, plan[day].items()):
                with col:
                    st.markdown(f"**{meal_name}**")

                    if not foods:
                        st.caption("_No foods available_")
                    else:
                        for food in foods:
                            icon = "🔒" if food['mandatory'] else "⭐"
                            portion_text = f" - {food['portion']}" if food[
                                'portion'] else ""
                            st.write(
                                f"{icon} {food['name']} ({food['type']}){portion_text}")

        st.divider()


st.title("🥗 Diet Automation MVP")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(
    ["📝 Manage Diet", "🎲 Generate Plan", "⭐ Saved Plans"])

with tab1:
    st.subheader("Create and manage your diets")

    # --- Create diet ---
    with st.form("add_diet_form"):
        diet_name = st.text_input("Diet name",
                                  placeholder="e.g. Nutritionist Plan")
        submitted = st.form_submit_button("Add diet")

        if submitted:
            if diet_name.strip():
                add_diet(diet_name)
                st.success("Diet added successfully!")
                st.rerun()
            else:
                st.warning("Please enter a diet name.")

    st.divider()

    # --- List diets ---
    st.subheader("Your diets")

    diets = get_diets()

    if not diets:
        st.info("No diets created yet.")
        st.stop()

    diet_options = {name: diet_id for diet_id, name in diets}
    selected_diet_name = st.selectbox(
        "Select a diet",
        options=diet_options.keys()
    )

    selected_diet_id = diet_options[selected_diet_name]
    ensure_default_food_categories(selected_diet_id)

    st.divider()

    # Predefined meal categories
    predefined_meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    cols = st.columns(len(predefined_meals))

    for col, meal in zip(cols, predefined_meals):
        if col.button(meal):
            add_meal_category(selected_diet_id, meal)
            st.rerun()

    # Custom meal category
    with st.form("add_custom_meal"):
        custom_meal = st.text_input("Custom meal category")
        submitted = st.form_submit_button("Add custom category")

        if submitted:
            if custom_meal.strip():
                add_meal_category(selected_diet_id, custom_meal)
                st.success("Meal category added.")
                st.rerun()
            else:
                st.warning("Enter a category name.")

    # ---- DISPLAY MEAL CATEGORIES ----
    st.subheader("Meal categories")

    categories = get_meal_categories(selected_diet_id)

    if not categories:
        st.info("No meal categories added yet.")
    else:
        for cat_id, category_name, _ in categories:
            col1, col2 = st.columns([8, 1])
            col1.markdown(f"### {category_name}")

            if col2.button("🗑️", key=f"del_meal_{cat_id}",
                           help="Delete this meal category"):
                delete_meal_category(cat_id)
                st.rerun()

            # -------- ADD FOOD FORM --------
            with st.form(f"add_food_{cat_id}"):
                food_name = st.text_input("Food name", key=f"name_{cat_id}")

                food_categories = get_food_categories(selected_diet_id)

                if not food_categories:
                    st.warning(
                        "No food categories available. Please add some below.")
                    food_cat_options = {}
                else:
                    food_cat_options = {name: fc_id for fc_id, name, _ in
                                        food_categories}

                selected_food_category = st.selectbox(
                    "Food category",
                    options=list(
                        food_cat_options.keys()) if food_cat_options else [
                        "No categories"],
                    key=f"food_cat_{cat_id}",
                    disabled=not food_cat_options
                )

                portion = st.text_input("Portion", key=f"portion_{cat_id}",
                                        placeholder="e.g. 30g, 1 cup, 2 slices")
                rating = st.slider("Preference", 1, 5, 3,
                                   key=f"rating_{cat_id}")
                mandatory = st.checkbox("Mandatory", key=f"mandatory_{cat_id}")

                add_food_btn = st.form_submit_button("➕ Add food")

                if add_food_btn and food_cat_options:
                    if food_name.strip():
                        add_food(
                            diet_id=selected_diet_id,
                            meal_category_id=cat_id,
                            name=food_name,
                            food_type=selected_food_category,
                            portion=portion,
                            rating=rating,
                            mandatory=int(mandatory)
                        )
                        st.rerun()
                    else:
                        st.warning("Please enter a food name.")

            # -------- MANAGE FOOD CATEGORIES --------
            with st.expander("🗂 Manage food categories"):
                food_categories = get_food_categories(selected_diet_id)

                if food_categories:
                    st.write("**Current food categories:**")
                    for fc_id, name, _ in food_categories:
                        col1, col2 = st.columns([8, 1])
                        col1.write(f"• {name}")

                        if col2.button("❌",
                                       key=f"del_food_cat_{cat_id}_{fc_id}"):
                            delete_food_category(fc_id)
                            st.rerun()

                    st.write("")
                else:
                    st.info(
                        "No food categories yet. Add your first one below!")

                st.write("**Add new food category:**")

                col_input, col_button = st.columns([3, 1])

                new_category_name = col_input.text_input(
                    "Category name",
                    key=f"new_cat_input_{cat_id}",
                    placeholder="e.g. Dairy, Nuts, Grains...",
                    label_visibility="collapsed"
                )

                if col_button.button("➕ Add", key=f"add_cat_btn_{cat_id}"):
                    if new_category_name.strip():
                        add_food_category(selected_diet_id, new_category_name)
                        st.success(f"Added '{new_category_name}'!")
                        st.rerun()
                    else:
                        st.warning("Enter a name first.")

            # --- Display foods ---
            foods = get_foods_by_category(cat_id)

            if not foods:
                st.caption("No foods added yet.")
            else:
                for food_id, name, ftype, portion, rating, mandatory in foods:
                    col1, col2 = st.columns([8, 1])

                    label = f"**{name}** ({ftype})"
                    if portion:
                        label += f" — {portion}"
                    label += f" ⭐ {rating}"
                    if mandatory:
                        label += " 🔒"

                    col1.write(label)

                    if col2.button("❌", key=f"del_food_{food_id}"):
                        delete_food(food_id)
                        st.rerun()

            st.divider()

with tab2:
    st.subheader("🎲 Generate Your Weekly Meal Plan")

    diets = get_diets()

    if not diets:
        st.warning("Please create a diet first in the 'Manage Diet' tab.")
        st.stop()

    diet_options = {name: diet_id for diet_id, name in diets}
    selected_diet_name_shuffle = st.selectbox(
        "Select a diet for planning",
        options=diet_options.keys(),
        key="shuffle_diet_select"
    )

    selected_diet_id_shuffle = diet_options[selected_diet_name_shuffle]
    meal_categories = get_meal_categories(selected_diet_id_shuffle)

    if not meal_categories:
        st.warning(
            "Please add meal categories first (e.g., Breakfast, Lunch, Dinner).")
        st.stop()

    # Check if there are foods
    has_foods = False
    for cat_id, _, _ in meal_categories:
        if get_foods_by_category(cat_id):
            has_foods = True
            break

    if not has_foods:
        st.warning("Please add some foods to your meal categories first.")
        st.stop()

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎲 Shuffle New Plan", type="primary",
                     use_container_width=True):
            st.session_state.current_plan = generate_weekly_plan(
                selected_diet_id_shuffle, meal_categories)
            st.rerun()

    with col2:
        if st.button("🔄 Shuffle Again", use_container_width=True,
                     disabled=st.session_state.current_plan is None):
            st.session_state.current_plan = generate_weekly_plan(
                selected_diet_id_shuffle, meal_categories)
            st.rerun()

    st.divider()

    if st.session_state.current_plan:
        display_weekly_plan(st.session_state.current_plan)

        st.divider()
        st.subheader("💾 Save This Plan")

        with st.form("save_plan_form"):
            default_name = f"Week Plan - {datetime.now().strftime('%b %d, %Y')}"
            plan_name = st.text_input("Plan name", value=default_name)

            save_btn = st.form_submit_button("⭐ Save to Favorites")

            if save_btn:
                if plan_name.strip():
                    save_weekly_plan(
                        selected_diet_id_shuffle,
                        plan_name,
                        st.session_state.current_plan
                    )
                    st.success(f"✅ Saved '{plan_name}' to favorites!")
                else:
                    st.warning("Please enter a plan name.")
    else:
        st.info("Click 'Shuffle New Plan' to generate your weekly meal plan!")

with tab3:
    st.subheader("⭐ Your Saved Plans")

    diets = get_diets()

    if not diets:
        st.warning("Please create a diet first.")
        st.stop()

    diet_options = {name: diet_id for diet_id, name in diets}
    selected_diet_name_saved = st.selectbox(
        "Select a diet to view plans",
        options=diet_options.keys(),
        key="saved_diet_select"
    )

    selected_diet_id_saved = diet_options[selected_diet_name_saved]
    saved_plans = get_weekly_plans(selected_diet_id_saved)

    if not saved_plans:
        st.info(
            "No saved plans yet. Generate and save a plan in the 'Generate Plan' tab!")
    else:
        for plan_id, plan_name, created_at, plan_data_json in saved_plans:
            with st.expander(f"📋 {plan_name} (Created: {created_at})"):
                plan_data = json.loads(plan_data_json)

                # Option to rename
                col1, col2, col3 = st.columns([3, 1, 1])

                new_name = col1.text_input(
                    "Rename plan",
                    value=plan_name,
                    key=f"rename_{plan_id}",
                    label_visibility="collapsed"
                )

                if col2.button("✏️ Rename", key=f"rename_btn_{plan_id}"):
                    if new_name.strip() and new_name != plan_name:
                        update_weekly_plan_name(plan_id, new_name)
                        st.success("Renamed!")
                        st.rerun()

                if col3.button("🗑️ Delete", key=f"delete_plan_{plan_id}"):
                    delete_weekly_plan(plan_id)
                    st.success("Deleted!")
                    st.rerun()

                st.divider()
                display_weekly_plan(plan_data)