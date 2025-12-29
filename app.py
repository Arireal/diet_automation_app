import streamlit as st
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
    seed_default_food_categories
)

st.set_page_config(
    page_title="Diet Automation MVP",
    layout="centered"
)

create_tables()

st.title("🥗 Diet Automation MVP")
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

# Initialize default food categories for this diet
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
        # Header with delete button for meal category
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

            portion = st.text_input("Portion", key=f"portion_{cat_id}")
            rating = st.slider("Preference", 1, 5, 3, key=f"rating_{cat_id}")
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

        # -------- MANAGE FOOD CATEGORIES (OUTSIDE FORM) --------
        with st.expander("🗂 Manage food categories"):
            # Show existing food categories with delete buttons
            food_categories = get_food_categories(selected_diet_id)

            if food_categories:
                st.write("**Current food categories:**")
                for fc_id, name, _ in food_categories:
                    col1, col2 = st.columns([8, 1])
                    col1.write(f"• {name}")

                    if col2.button("❌", key=f"del_food_cat_{cat_id}_{fc_id}"):
                        delete_food_category(fc_id)
                        st.rerun()

                st.write("")  # spacing
            else:
                st.info("No food categories yet. Add your first one below!")

            # Add new food category - SIMPLE APPROACH
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