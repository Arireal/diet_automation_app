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
    delete_food
)


st.set_page_config(
    page_title="Diet Automation MVP",
    layout="centered"
)

FOOD_TYPES = [
    "Fruit",
    "Vegetable",
    "Protein",
    "Carbohydrate",
    "Fat",
    "Other"
]

create_tables()

st.title("🥗 Diet Automation MVP")
st.subheader("Create and manage your diets")

# --- Create diet ---
with st.form("add_diet_form"):
    diet_name = st.text_input("Diet name", placeholder="e.g. Nutritionist Plan")
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

st.divider()
st.subheader("Meal categories")

# Predefined categories
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

# ---- DISPLAY CATEGORIES (outside the form) ----
st.subheader("Meal categories")

categories = get_meal_categories(selected_diet_id)

if not categories:
    st.info("No meal categories added yet.")
else:
    for cat_id, category_name, _ in categories:
        st.markdown(f"### {category_name}")

        # --- Add food form ---
        with st.form(f"add_food_{cat_id}"):
            food_name = st.text_input("Food name", key=f"name_{cat_id}")
            food_type = st.selectbox("Food type", FOOD_TYPES,
                                     key=f"type_{cat_id}")
            portion = st.text_input("Portion (e.g. 100g, 1 unit)",
                                    key=f"portion_{cat_id}")
            rating = st.slider("Preference", 1, 5, 3, key=f"rating_{cat_id}")
            mandatory = st.checkbox("Mandatory (must appear)",
                                    key=f"mandatory_{cat_id}")

            submitted = st.form_submit_button("➕ Add food")

            if submitted:
                if food_name.strip():
                    add_food(
                        diet_id=selected_diet_id,
                        meal_category_id=cat_id,
                        name=food_name,
                        food_type=food_type,
                        portion=portion,
                        rating=rating,
                        mandatory=int(mandatory)
                    )
                    st.success("Food added.")
                    st.rerun()
                else:
                    st.warning("Food name is required.")

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








