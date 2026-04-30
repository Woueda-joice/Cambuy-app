from flask import Flask, render_template, request, redirect, session
from analysis import analyse_data, generate_charts
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "cambuy_secret_key"
init_db()

def get_db_connection():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if not DATABASE_URL:
        raise Exception("DATABASE_URL non définie sur Render")
        
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Création base de données
def init_db(): 
    print("Initialisation DB")
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id SERIAL PRIMARY KEY,
            age INTEGER,
            sexe TEXT,
            ville TEXT,
            frequence TEXT,
            preference TEXT,
            raison TEXT,
            produit TEXT
        )
    ''')

    
    conn.commit()
    cur.close()
    conn.close()
    print("DB prete")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
     try:
         data = (
             request.form.get('age'),
             request.form.get('sexe'),
             request.form.get('ville'),
             request.form.get('frequence'),
             request.form.get('preference'),
             request.form.get('raison'),
             request.form.get('produit')
         )
    
          conn = get_db_connection()
          cur = conn.cursor()
    
          cur.execute('''
              INSERT INTO responses (age, sexe, ville, frequence, preference, raison, produit)
              VALUES (%s, %s, %s, %s, %s, %s, %s)
          ''', data)
    
          conn.commit()
          cur.close()
          conn.close()

           return redirect('/results')

     except Exception as e:
           return f"ERREUR SQL: {e}"



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 🔐 identifiants pour le prof
        if username == "prof" and password == "cambuy2026":
            session['logged_in'] = True
            return redirect('/results')
        else:
           return "❌ Identifiants incorrects"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/results')
def results():
    if not session.get('logged_in'):
        return redirect('/login')
 
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM responses", conn)
    conn.close()

    # --- Statistiques générales ---
    total = len(df)
    moyenne_age = round(df['age'].mean(), 1) if not df.empty else 0

   
    # Sexe
    sexe_counts = df['sexe'].value_counts()
    sexe_labels = list(sexe_counts.index)
    sexe_values = [int(x) for x in sexe_counts.values]

    # Préférence
    pref_counts = df['preference'].value_counts()
    pref_labels = list(pref_counts.index)
    pref_values = [int(x) for x in pref_counts.values]

    # Produits
    prod_counts = df['produit'].value_counts()
    prod_labels = list(prod_counts.index)
    prod_values = [int(x) for x in prod_counts.values]
    
    return render_template(
        'results.html',
        total=total,
        moyenne_age=moyenne_age,
        sexe_labels=sexe_labels,
        sexe_values=sexe_values,
        pref_labels=pref_labels,
        pref_values=pref_values,
        prod_labels=prod_labels,
        prod_values=prod_values
    )
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
    
    
    
    
    
    
