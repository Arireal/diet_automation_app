import sqlite3
import json
from datetime import datetime

DB_PATH = "data/diet_app.db"

DEFAULT_FOOD_CATEGORIES = [
    "Fruits",
    "Vegetables",
    "Proteins",
    "Carbohydrates",
    "Fats"
]


def get_connection():
    return sqlite3.connect("data/diet_app.db")


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diet_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        order_index INTEGER NOT NULL,
        FOREIGN KEY (diet_id) REFERENCES diets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diet_id INTEGER NOT NULL,
        meal_category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        food_type TEXT NOT NULL,
        portion TEXT,
        rating INTEGER DEFAULT 3,
        mandatory INTEGER DEFAULT 0,
        FOREIGN KEY (diet_id) REFERENCES diets (id),
        FOREIGN KEY (meal_category_id) REFERENCES meal_categories (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diet_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        order_index INTEGER NOT NULL,
        FOREIGN KEY (diet_id) REFERENCES diets (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weekly_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diet_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL,
        plan_data TEXT NOT NULL,
        FOREIGN KEY (diet_id) REFERENCES diets (id)
    )
    """)

    conn.commit()
    conn.close()


def add_diet(name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO diets (name) VALUES (?)",
        (name,)
    )

    conn.commit()
    conn.close()


def get_diets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM diets")
    diets = cursor.fetchall()

    conn.close()
    return diets


def add_meal_category(diet_id: int, name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COALESCE(MAX(order_index), 0) + 1 FROM meal_categories WHERE diet_id = ?",
        (diet_id,)
    )
    next_order = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO meal_categories (diet_id, name, order_index)
        VALUES (?, ?, ?)
        """,
        (diet_id, name, next_order)
    )

    conn.commit()
    conn.close()


def get_meal_categories(diet_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, order_index
        FROM meal_categories
        WHERE diet_id = ?
        ORDER BY order_index
        """,
        (diet_id,)
    )

    categories = cursor.fetchall()
    conn.close()
    return categories


def move_meal_category(category_id: int, direction: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT diet_id, order_index FROM meal_categories WHERE id = ?",
        (category_id,)
    )
    diet_id, current_order = cursor.fetchone()

    if direction == "up":
        cursor.execute(
            """
            SELECT id, order_index FROM meal_categories
            WHERE diet_id = ? AND order_index < ?
            ORDER BY order_index DESC LIMIT 1
            """,
            (diet_id, current_order)
        )
    else:
        cursor.execute(
            """
            SELECT id, order_index FROM meal_categories
            WHERE diet_id = ? AND order_index > ?
            ORDER BY order_index ASC LIMIT 1
            """,
            (diet_id, current_order)
        )

    neighbor = cursor.fetchone()
    if neighbor:
        neighbor_id, neighbor_order = neighbor

        cursor.execute(
            "UPDATE meal_categories SET order_index = ? WHERE id = ?",
            (neighbor_order, category_id)
        )
        cursor.execute(
            "UPDATE meal_categories SET order_index = ? WHERE id = ?",
            (current_order, neighbor_id)
        )

    conn.commit()
    conn.close()


def delete_meal_category(category_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM meal_categories WHERE id = ?",
        (category_id,)
    )

    conn.commit()
    conn.close()


def add_food(
        diet_id,
        meal_category_id,
        name,
        food_type,
        portion,
        rating,
        mandatory
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO foods (
        diet_id,
        meal_category_id,
        name,
        food_type,
        portion,
        rating,
        mandatory
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        diet_id,
        meal_category_id,
        name,
        food_type,
        portion,
        rating,
        mandatory
    ))

    conn.commit()
    conn.close()


def get_foods_by_category(meal_category_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, food_type, portion, rating, mandatory
    FROM foods
    WHERE meal_category_id = ?
    ORDER BY rating DESC
    """, (meal_category_id,))

    foods = cursor.fetchall()
    conn.close()
    return foods


def delete_food(food_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM foods WHERE id = ?",
        (food_id,)
    )

    conn.commit()
    conn.close()


def add_food_category(diet_id: int, name: str):
    """Add a new food category to a diet"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM food_categories WHERE diet_id = ? AND name = ?",
        (diet_id, name)
    )

    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]

    cursor.execute(
        "SELECT COALESCE(MAX(order_index), 0) + 1 FROM food_categories WHERE diet_id = ?",
        (diet_id,)
    )
    order_index = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO food_categories (diet_id, name, order_index)
        VALUES (?, ?, ?)
        """,
        (diet_id, name, order_index)
    )

    new_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return new_id


def get_food_categories(diet_id: int):
    """Get all food categories for a diet"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, order_index
        FROM food_categories
        WHERE diet_id = ?
        ORDER BY order_index
        """,
        (diet_id,)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def ensure_default_food_categories(diet_id: int):
    """
    Ensure default food categories exist for a diet.
    Only adds them if they don't already exist (by name).
    """
    conn = get_connection()
    cursor = conn.cursor()

    for default_name in DEFAULT_FOOD_CATEGORIES:
        cursor.execute(
            "SELECT id FROM food_categories WHERE diet_id = ? AND name = ?",
            (diet_id, default_name)
        )

        if not cursor.fetchone():
            cursor.execute(
                "SELECT COALESCE(MAX(order_index), 0) + 1 FROM food_categories WHERE diet_id = ?",
                (diet_id,)
            )
            order_index = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO food_categories (diet_id, name, order_index)
                VALUES (?, ?, ?)
                """,
                (diet_id, default_name, order_index)
            )

    conn.commit()
    conn.close()


def delete_food_category(food_category_id: int):
    """Delete a food category"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM food_categories WHERE id = ?",
        (food_category_id,)
    )

    conn.commit()
    conn.close()


def seed_default_food_categories(diet_id: int):
    """
    DEPRECATED - Use ensure_default_food_categories instead.
    """
    ensure_default_food_categories(diet_id)


def save_weekly_plan(diet_id: int, name: str, plan_data: dict):
    """Save a weekly plan to favorites"""
    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO weekly_plans (diet_id, name, created_at, plan_data)
        VALUES (?, ?, ?, ?)
        """,
        (diet_id, name, created_at, json.dumps(plan_data))
    )

    conn.commit()
    conn.close()


def get_weekly_plans(diet_id: int):
    """Get all saved weekly plans for a diet"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, created_at, plan_data
        FROM weekly_plans
        WHERE diet_id = ?
        ORDER BY created_at DESC
        """,
        (diet_id,)
    )

    plans = cursor.fetchall()
    conn.close()
    return plans


def delete_weekly_plan(plan_id: int):
    """Delete a weekly plan"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM weekly_plans WHERE id = ?",
        (plan_id,)
    )

    conn.commit()
    conn.close()


def update_weekly_plan_name(plan_id: int, new_name: str):
    """Update the name of a weekly plan"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE weekly_plans SET name = ? WHERE id = ?",
        (new_name, plan_id)
    )

    conn.commit()
    conn.close()