import sqlite3

conn = sqlite3.connect('database2.db')
print("Opened database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS my_user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
print("Table 2 created successfully")
conn.execute('''CREATE TABLE IF NOT EXISTS users_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date DATE,
                age INTEGER,
                height INTEGER,
                weight INTEGER,
                gender TEXT,
                ActivityLevel TEXT,
                Weightplan TEXT,
                RecipeCategory TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES my_user (id)
            )
        ''')

conn.execute('''
            CREATE TABLE IF NOT EXISTS fat_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                height INTEGER,
                waist INTEGER,
                gender TEXT,
                hip INTEGER,
                neck INTEGER
            )
        ''')
conn.execute('''CREATE TABLE IF NOT EXISTS package (
    id INTEGER PRIMARY KEY,
    package TEXT,
    name TEXT,
    email TEXT,
    phone TEXT
)''')

conn.execute('''CREATE TABLE IF NOT EXISTS recipies(
    date DATE,
    name TEXT,
    calories TEXT,
    protein_contents TEXT,
    carbohydrate_contents TEXT,
    recipe_categories TEXT
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS recipes(
    date DATE,
    username TEXT,
    name TEXT,
    calories TEXT,
    carbohydrate_content TEXT,
    recipe_category TEXT
)''')
conn.execute('''CREATE TABLE IF NOT EXISTS food_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    log_date DATE,
                    food_name TEXT,
                    calories INTEGER
                )''')
conn.execute('CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
print(" admin  Table  created successfully")
conn.close()
