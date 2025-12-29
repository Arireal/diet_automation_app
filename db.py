import sqlite3

DB_PATH = "data/diet_app.db"


def get_connection():
    return sqlite3.connect("data/diet_app.db")


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # existing tables...
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

    # 👇 NEW TABLE
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


