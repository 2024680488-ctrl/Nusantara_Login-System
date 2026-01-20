import random
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# --- 1. DATABASE SETUP (Ditambah column 'additional_info') ---
def init_db():
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    # Menambah column 'additional_info' untuk simpan ID atau Email
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, 
                       role TEXT, 
                       collection TEXT, 
                       additional_info TEXT,
                       timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 2. AI LOGIC ---
def get_book_recommendation(collection):
    general_books = ["Modern Python Programming", "The Art of Digital Libraries", "Introduction to Data Science", "The Pickwick Papers", "Lighthouse","Contengan Jalan" , "His Last Bow [8 stories]"]
    special_books = ["Hikayat Hang Tuah", "Ancient Maps of Malay Archipelago", "Kitab Tib", "Kitab Rahsia Ejaan Jawi (1929)", "Kitab Kata-kata Melayu", "Sejarah Melayu: Royal Edition"]
    
    if collection == "Special":
        return random.choice(special_books)
    else:
        return random.choice(general_books)

# --- 3. ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    role = request.form['role']
    collection = request.form['collection']
    
    # Menentukan maklumat tambahan berdasarkan role
    info = ""
    if role == 'Guest':
        info = request.form.get('email') # Ambil email jika Guest
    elif role in ['Student', 'Staff']:
        info = request.form.get('user_id') # Ambil ID jika Student/Staff
    
    if role == 'Admin':
        admin_id = request.form.get('admin_id')
        admin_pass = request.form.get('admin_pass')
        
        if admin_id == "admin123" and admin_pass == "password123":
            session['user_name'] = name
            session['chosen_collection'] = collection
            save_to_db(name, role, collection, "ADMIN-AUTHORIZED")
            return redirect(url_for('admin_dashboard'))
        else:
            return "Wrong Admin ID or Password! <a href='/'>Try again</a>"
    
    # Simpan ke session untuk kegunaan User View
    session['user_name'] = name
    session['chosen_collection'] = collection
    
    # Simpan ke database dengan info tambahan (ID atau Email)
    save_to_db(name, role, collection, info)
    
    rec_book = get_book_recommendation(collection)
    return render_template('user_view.html', name=name, role=role, rec=rec_book, collection=collection)

# Fungsi bantuan dengan tambahan parameter 'info'
def save_to_db(name, role, collection, info):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    # SQL INSERT dikemaskini untuk column baru
    cursor.execute("INSERT INTO attendance (name, role, collection, additional_info, timestamp) VALUES (?, ?, ?, ?, ?)",
                   (name, role, collection, info, time_now))
    conn.commit()
    conn.close()

@app.route('/dashboard')
def admin_dashboard():
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
    all_data = cursor.fetchall()
    total_logins = len(all_data)
    conn.close()
    
    display_name = session.get('user_name', 'Admin')
    chosen_collection = session.get('chosen_collection', 'General') 
    rec_book = get_book_recommendation(chosen_collection)
    
    return render_template('dashboard.html', 
                           name=display_name, 
                           role="Admin", 
                           rec=rec_book, 
                           logs=all_data, 
                           total=total_logins, 
                           collection=chosen_collection)

@app.route('/delete/<int:id>')
def delete_attendance(id):
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit/<int:id>')
def edit_page(id):
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return render_template('edit.html', data=row)

@app.route('/update', methods=['POST'])
def update_data():
    id = request.form['id']
    name = request.form['name']
    role = request.form['role']
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE attendance SET name=?, role=? WHERE id=?", (name, role, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)