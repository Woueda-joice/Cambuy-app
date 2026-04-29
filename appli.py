from flask import Flask, render_template, request, redirect, session
from analysis import analyse_data, generate_charts
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "cambuy_secret_key"


# Création base de données
def init_db():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            sexe TEXT,
            ville TEXT,
            frequence TEXT,
            preference TEXT,
            raison TEXT,
            produit TEXT
        )
    ''')
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = (
        request.form['age'],
        request.form['sexe'],
        request.form['ville'],
        request.form['frequence'],
        request.form['preference'],
        request.form['raison'],
        request.form['produit']
    )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    conn.execute('''
        INSERT INTO responses (age, sexe, ville, frequence, preference, raison, produit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

    return redirect('/results')



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
 
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    
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
    app.run(host="0.0.0.0", port=port)
    
    
    
    
    
    
    
