from flask import Flask ,render_template ,request,redirect,url_for,session
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import sqlite3
app = Flask(__name__)
app.secret_key = 'pamitha05'


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/main')
def main():
    return render_template("main.html")


@app.route('/admin_login')
def admin_login():
    return render_template("admin_login.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/package')
def package():
    return render_template("package.html")


@app.route('/food_tracking')
def food_tracking():
    return render_template("food_tracking.html")


@app.route('/adminDashboard')
def adminDashboard():
    return render_template("adminDashboard.html")


@app.route('/bmi')
def bmi():
    return render_template("bmi.html")


@app.route('/register1', methods=['GET', 'POST'])
def register1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database2.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO my_user (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))
    return render_template('register.html')


@app.route('/login1', methods=['GET', 'POST'])
def login1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database2.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM my_user WHERE username = ? AND password = ?', (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return render_template('main.html')
        else:
            return "Incorrect username or password"
    return render_template('login.html')


@app.route('/package1', methods=['GET', 'POST'])
def package1():
    if request.method == 'POST':
        package = request.form['package']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        # Check if the user has already booked a package
        conn = sqlite3.connect('database2.db')
        c = conn.cursor()
        c.execute("SELECT * FROM package WHERE name = ?", (name,))
        existing_booking = c.fetchone()
        conn.close()

        if existing_booking:
            # User has already booked a package, handle the validation here
            return "You have already booked a package!"
        else:
            # User hasn't booked a package yet, proceed with inserting the new booking
            conn = sqlite3.connect('database2.db')
            c = conn.cursor()
            c.execute("INSERT INTO package (package, name, email, phone) VALUES (?, ?, ?, ?)",
                      (package, name, email, phone))
            conn.commit()
            conn.close()
            return redirect(url_for('diet'))
    return render_template('login.html')


data = pd.read_csv(r'C:\PAMITHA\project\pynuticare\static\Calories.csv')


def calculate_bmr(age, height, weight, gender):
    if gender == "Male":
        bmr = 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
    else:  # Female
        bmr = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)
    return bmr
def adjust_bmr_for_activity(bmr, activity_level):
    activity_multipliers = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (light exercise/sports 1-3 days/week)": 1.375,
        "Moderately active (moderate exercise/sports 3-5 days/week)": 1.55,
        "Very active (hard exercise/sports 6-7 days a week)": 1.725,
        "Super active (very hard exercise/sports & a physical job)": 1.9
    }
    return bmr * activity_multipliers[activity_level]


def apply_weight_plan(maintenance_calories, weight_plan):
    weight_plan_multipliers = {
        "Maintain weight": 1,
        "Mild weight loss": 0.9,
        "Weight loss": 0.8,
        "Extreme weight loss": 0.6,
        "Mild weight gain": 1.1,
        "Weight gain": 1.2,
        "Rapid weight gain": 1.3
    }
    return round(maintenance_calories * weight_plan_multipliers[weight_plan], 2)


def calculate_macronutrients(caloric_needs):
    protein_grams = (0.10 * caloric_needs) / 4
    carbs_grams = (0.55 * caloric_needs) / 4
    fats_grams = (0.30 * caloric_needs) / 9
    fiber_grams = (caloric_needs / 1000) * 14
    return protein_grams, carbs_grams, fats_grams, fiber_grams


def recommend_recipes(user_caloric_needs, pipeline, user_nutritional_needs, data, RecipeCategory):
    total_calories = 0
    recommended_indices_list = []
    neighbors_to_consider = 8  # Start with 10 neighbors

    # Filter the data based on the selected category
    filtered_data = data[data['RecipeCategory'] == RecipeCategory]

    if filtered_data.empty:
        # If no recipes match the category, return an empty DataFrame
        return pd.DataFrame()

    while total_calories < user_caloric_needs and neighbors_to_consider <= filtered_data.shape[0]:
        # Update the pipeline to consider more neighbors
        pipeline.set_params(NN__kw_args={'n_neighbors': neighbors_to_consider, 'return_distance': False})

        # Get recommended indices
        recommended_indices = pipeline.transform(user_nutritional_needs)[0]

        for index in recommended_indices:
            if index not in recommended_indices_list and index < len(filtered_data):  # Check if index exists
                recipe = filtered_data.iloc[index]
                total_calories += recipe['Calories']
                recommended_indices_list.append(index)

                if total_calories >= user_caloric_needs:
                    return filtered_data.iloc[recommended_indices_list]

        # If we haven't met the caloric needs, consider more neighbors in the next iteration
        neighbors_to_consider += 8

    return filtered_data.iloc[recommended_indices_list]
def has_generated_food(username, date):
    conn = sqlite3.connect('database2.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users_data WHERE username = ? AND date = ?", (username, date))
    data = cur.fetchone()
    conn.close()
    return data is not None
@app.route('/diet.html', methods=['POST', 'GET'])
def diet():
    if request.method == 'POST':
        username = request.form['username']
        date = request.form['date']
        session['date'] = date
        # Check if the user has already generated food for the given date
        if not has_generated_food(username, date):
            age = int(request.form['age'])
            height = float(request.form['height'])
            weight = float(request.form['weight'])
            gender = request.form['gender']
            activity_level = request.form['activity_level']
            weight_plan = request.form['weight_plan']
            RecipeCategory = request.form['RecipeCategory']
            conn = sqlite3.connect('database2.db')
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO users_data (username,date,age,height,weight,gender,ActivityLevel,Weightplan,RecipeCategory) VALUES (?,?,?,?,?,?,?,?,?)',
                (username, date, age, height, weight, gender, activity_level, weight_plan, RecipeCategory))
            conn.commit()
            conn.close()
        else:
            # Handle the case where food for the given date already exists
            return "You have already generated food for this date."


        bmr = calculate_bmr(age, height, weight, gender)
        maintenance_calories = adjust_bmr_for_activity(bmr, activity_level)
        final_caloric_needs = apply_weight_plan(maintenance_calories, weight_plan)
        # Print statement to verify caloric needs
        print(f"Caloric needs: {final_caloric_needs}")
        user_nutritional_needs = np.array([calculate_macronutrients(final_caloric_needs)])
        daily_protein, daily_carbohydrates, daily_fats, daily_fiber = calculate_macronutrients(final_caloric_needs)
        # Filter recipes based on nutritional criteria
        max_Calories = final_caloric_needs
        max_daily_fat = final_caloric_needs * 0.30 / 9
        max_daily_Saturatedfat = 13
        max_daily_Cholesterol = 300
        max_daily_Sodium = 2300
        max_daily_Carbohydrate = final_caloric_needs * 0.55 / 4
        max_daily_Fiber = final_caloric_needs / 1000 * 14
        max_daily_Sugar = 40
        max_daily_Protein = final_caloric_needs * 0.10 / 4

        max_list = [max_Calories, max_daily_fat, max_daily_Saturatedfat, max_daily_Cholesterol, max_daily_Sodium,
                    max_daily_Carbohydrate, max_daily_Fiber, max_daily_Sugar, max_daily_Protein]

        extracted_data = data.copy()
        relevant_columns = [4, 5, 6, 7, 9]
        for column, maximum in zip(extracted_data.columns[relevant_columns], max_list):
            extracted_data = extracted_data[extracted_data[column] < maximum]

        # Standardize the nutritional data
        scaler = StandardScaler()
        prep_data = scaler.fit_transform(extracted_data.iloc[:, relevant_columns].to_numpy())

        neigh = NearestNeighbors(metric='cosine', algorithm='brute')
        neigh.fit(prep_data)

        transformer = FunctionTransformer(neigh.kneighbors, kw_args={'return_distance': False})
        pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])

        params = {'n_neighbors': 8, 'return_distance': False}
        pipeline.set_params(NN__kw_args=params)

        daily_calories = final_caloric_needs

        user_nutritional_needs = np.array([[daily_calories, daily_fats, daily_carbohydrates, daily_fiber, daily_protein]])
        recommended_recipes = recommend_recipes(final_caloric_needs, pipeline, user_nutritional_needs, extracted_data, RecipeCategory)
        # return render_template('diet.html', recommended_recipes=recommended_recipes)
        return render_template('diet.html', recommended_recipes=recommended_recipes, final_caloric_needs=final_caloric_needs)


    return render_template('diet.html', recommended_recipes=None)
@app.route('/save_data', methods=['POST'])
def save_data():
    if request.method == 'POST':
        try:
            # Get the username and date from the session if available
            username = session.get('username')
            date = session.get('date')

            # Get the recommended recipes data from the form
            names = request.form.getlist('names[]')
            calories = request.form.getlist('calories[]')
            carbohydrate_contents = request.form.getlist('carbohydrate_contents[]')
            recipe_categories = request.form.getlist('recipe_categories[]')

            # Connect to the SQLite3 database
            conn = sqlite3.connect('database2.db')
            cursor = conn.cursor()

            # Insert each recipe into the database
            for name, calorie, carbohydrate_content, recipe_category in zip(names, calories, carbohydrate_contents, recipe_categories):
                cursor.execute('INSERT INTO recipes (date ,username, name, calories, carbohydrate_content, recipe_category) VALUES (?, ?, ?, ?, ?, ?)',
                    (date,username, name, calorie, carbohydrate_content, recipe_category))

            # Commit the transaction and close the connection
            conn.commit()
            conn.close()

            # Optionally, redirect to a success page or render a success message
            return render_template('main.html')

        except Exception as e:
            # Handle any errors or exceptions
            return f"An error occurred: {str(e)}"


@app.route('/dash.html')
def dash():
    return render_template('dash.html')


@app.route('/foods')
def foods():
    return render_template('foods.html')


@app.route('/user_recipies')
def user_recipies():
    return render_template('user_recipies.html')


@app.route('/display_recipes', methods=['POST'])
def display_recipes():
    if 'username' in session:
        if request.method == 'POST':
            try:
                date = request.form['date']
                username = session['username']
                print(username)
                conn = sqlite3.connect('database2.db')
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM recipes WHERE username = ? AND date = ?", (username, date,))
                recipes = cursor.fetchall()
                conn.close()

                return render_template('user_recipies.html', recipes=recipes)

            except Exception as e:
                return f"An error occurred: {str(e)}"


@app.route('/log_details', methods=['POST'])
def log_details():
    if request.method == 'POST':
        username = request.form['username']
        log_date = request.form['log_date']
        food_names = request.form.getlist('food_name[]')
        calories_list = request.form.getlist('calories[]')

        # Check if the user has already logged foods for the specified date
        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food_log WHERE username = ? AND log_date = ?", (username, log_date))
        existing_logs = cursor.fetchall()
        conn.close()

        # If user has already logged foods for the date, redirect back to the main page
        if existing_logs:
            return "you already logged your food items"

        # If user hasn't logged foods for the date, insert new records into the database
        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()
        for food_name, calories in zip(food_names, calories_list):
            cursor.execute('''INSERT INTO food_log (username, log_date, food_name, calories)
                     VALUES (?, ?, ?, ?)''', (username, log_date, food_name, calories))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))


@app.route('/adlog', methods=['GET', 'POST'])
def adlog():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database2.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM admin WHERE username = ? AND password = ?  ', (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            return redirect(url_for('adminDashboard'))
        else:
            return "Incorrect username or password"


@app.route('/admin_users')
def admin_users():
    # Connect to the SQLite database
    conn = sqlite3.connect('database2.db')
    c = conn.cursor()

    # Fetch customer data from the database
    c.execute("SELECT * FROM my_user ")
    customers = c.fetchall()

    # Close the database connection
    conn.close()

    # Render HTML template with customer data
    return render_template('admin_users.html', customers=customers)


@app.route('/admin_udetails')
def admin_udetails():
    # Connect to the SQLite database
    conn = sqlite3.connect('database2.db')
    c = conn.cursor()

    # Fetch customer data from the database
    c.execute("SELECT * FROM users_data ")
    customers = c.fetchall()

    # Close the database connect
    conn.close()

    # Render HTML template with customer data
    return render_template('admin_udetails.html', customers=customers)


@app.route('/ad_fooddetails')
def ad_fooddetails():
    # Connect to the SQLite database
    conn = sqlite3.connect('database2.db')
    c = conn.cursor()

    # Fetch customer data from the database
    c.execute("SELECT * FROM recipes ")
    customers = c.fetchall()
    conn.close()
    return render_template('ad_fooddetails.html', customers=customers)


@app.route('/admin_upackage.html')
def admin_upackage():
    # Connect to the SQLite database
    conn = sqlite3.connect('database2.db')
    c = conn.cursor()

    # Fetch customer data from the database
    c.execute("SELECT * FROM package ")
    customers = c.fetchall()

    # Close the database connect
    conn.close()

    # Render HTML template with customer data
    return render_template('admin_upackage.html', customers=customers)


@app.route('/ad_foodlogs.html')
def ad_foodlogs():
    # Connect to the SQLite database
    conn = sqlite3.connect('database2.db')
    c = conn.cursor()

    # Fetch customer data from the database
    c.execute("SELECT * FROM food_log ")
    customers = c.fetchall()

    # Close the database connect
    conn.close()

    # Render HTML template with customer data
    return render_template('ad_foodlogs.html', customers=customers)


def foodslog(username):
    conn = sqlite3.connect('database2.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM food_log WHERE username=?", (username,))
    bookings = cur.fetchall()
    print(bookings)
    conn.close()
    return bookings


@app.route('/my_foodlog')
def my_foodlog():
    if 'username' in session:
        username = session['username']
        bookings = foodslog(username)

        return render_template('my_foodlog.html', bookings=bookings)
    else:
        return 'You are not logged in'


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


if __name__ == '__main__':
    app.run()
