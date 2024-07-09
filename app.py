import pandas as pd
from flask import Flask, render_template, request, current_app, url_for
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Charger et préparer les données
data = pd.read_csv('Fertilizer Prediction.csv')
data_transformed = pd.get_dummies(data, columns=['Soil Type', 'Crop Type'])
X = data_transformed.drop(columns=['Fertilizer Name'])
y = data_transformed['Fertilizer Name']

# Encoder les étiquettes
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Diviser les données
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Entraîner le modèle
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Sauvegarder le modèle
joblib.dump(model, 'fertilizer_model.joblib')
joblib.dump(le, 'label_encoder.joblib')

def get_fertilizer_image_url(fertilizer):
    fertilizer_images = {
        "Urea": "https://i.postimg.cc/sgFSZVZP/urea.jpg",
        "DAP": "https://i.postimg.cc/sgFSZVZP/urea.jpg",
        "14-35-14": "https://i.postimg.cc/fbHgsH8r/14-35-14.jpg",
        "28-28": "https://i.postimg.cc/X73hwyBx/gromor-28-28-0-fertilizers.jpg",
        "17-17-17": "https://i.postimg.cc/d3Sytybv/npk-17-all-fertilizer-377061203-0ie8b.avif",
        "20-20": "https://i.postimg.cc/KjK8vMGP/20-20.jpg",
        "10-26-26": "https://i.postimg.cc/xT628PpL/12333.jpg",
    }
    return fertilizer_images.get(fertilizer, "/static/images/default_fertilizer. jpg")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Récupérer les entrées de l'utilisateur
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            moisture = float(request.form['moisture'])
            soil_type = request.form['soil_type']
            crop_type = request.form['crop_type']
            nitrogen = float(request.form['nitrogen'])
            potassium = float(request.form['potassium'])
            phosphorous = float(request.form['phosphorous'])

            # Préparer les données pour la prédiction
            input_data = pd.DataFrame({
                'Temparature': [temperature],
                'Humidity': [humidity],
                'Moisture': [moisture],
                'Nitrogen': [nitrogen],
                'Potassium': [potassium],
                'Phosphorous': [phosphorous]
            })

            # Ajouter les colonnes one-hot pour Soil Type et Crop Type
            for col in X.columns:
                if col not in input_data.columns:
                    if col.startswith('Soil Type_') and col.endswith(soil_type):
                        input_data[col] = 1
                    elif col.startswith('Crop Type_') and col.endswith(crop_type):
                        input_data[col] = 1
                    else:
                        input_data[col] = 0

            current_app.logger.info(f"Colonnes de input_data : {input_data.columns}")

            # Charger le modèle et faire la prédiction
            model = joblib.load('fertilizer_model.joblib')
            le = joblib.load('label_encoder.joblib')
            prediction = model.predict(input_data)
            fertilizer = le.inverse_transform(prediction)[0]

            # Obtenir l'URL de l'image correspondante
            image_url = get_fertilizer_image_url(fertilizer)

            current_app.logger.info(f"Fertilizer prediction: {fertilizer}")
            return render_template('resultat.html', fertilizer=fertilizer, image_url=image_url)

        except Exception as e:
            current_app.logger.error(f"Erreur lors de la prédiction : {str(e)}")
            return render_template('resultat.html', error=str(e))

    return render_template('resultat.html')


# ---------------------------------------------------------------------------------------
    
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secret key for session management

def get_db_connection():
    conn = sqlite3.connect('Agri.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            logging.debug("Form data: %s", request.form)

            first_name = request.form['first_name']
            last_name = request.form['last_name']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['Phone_Number']
            file = request.files['photo']

            logging.debug(f"Received data: first_name={first_name}, last_name={last_name}, username={username}, password={password}, email={email}, phone={phone}")

            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            logging.debug(f"User found: {user}")

            filename = None
            file_path = None
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

            if user:
                cursor.execute('''
                    UPDATE users 
                    SET first_name = ?, last_name = ?, email = ?, phone_number = ?, filename = ?, file_path = ?
                    WHERE username = ?
                ''', (first_name, last_name, email, phone, filename, file_path, username))
                flash('Profile updated successfully!', 'success')
            else:
                cursor.execute('''
                    INSERT INTO users (first_name, last_name, username, password, email, phone_number, filename, file_path) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (first_name, last_name, username, password, email, phone, filename, file_path))
                flash('Profile created successfully!', 'success')

            db.commit()
            logging.debug("Database commit successful")
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            db.rollback()
            flash(f'An error occurred: {e}', 'error')
            logging.error(f"An error occurred: {e}")
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            flash(f'An unexpected error occurred: {e}', 'error')
            return redirect(url_for('login'))
        finally:
            cursor.close()
            db.close()
    return render_template('signup.html')



# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username and password match
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            conn.close()
            return redirect(url_for('profile'))  # Replace with the appropriate route after login
        else:
            flash('Login unsuccessful. Please check your username and password.', 'error')

        conn.close()

    return render_template('login.html')  # Render the login form template



@app.route('/my-fertilizer')
def my_fertilizer():
    return render_template('My Fertilizer.html')

@app.route('/profile')
def profile():
    
    return render_template('profile.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/resultat')
def resultat():
    return render_template('resultat.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('About us.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/form2')
def form2():
    return render_template('form2.html')

@app.route('/plus')
def plus():
    return render_template('plus.html')



# Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True)